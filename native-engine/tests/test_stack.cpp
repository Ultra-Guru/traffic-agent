// ForwardStack (基建一「通」) unit tests.
//
// Every test synthesizes client-side packets with buildTcpPacket/buildUdpPacket
// (valid checksums) and asserts on the emitted TUN packets and on the command
// outbox (connects / sends / closes).

#include <cstring>
#include <string>
#include <vector>

#include "test_framework.hpp"
#include "builders.hpp"
#include "traffic/packet_build.h"
#include "traffic/stack.h"

namespace {

using traffic::FlowKey;
using traffic::ForwardStack;
using traffic::StackConfig;
using traffic::TcpHeader;

constexpr uint32_t kClientIp = 0xC0A8010A;  // 192.168.1.10
constexpr uint32_t kServerIp = 0x8EFA0A14;  // 142.250.10.20
constexpr uint16_t kClientPort = 40000;
constexpr uint16_t kPlainPort = 8081;  // non-redirected target port

using Bytes = std::vector<uint8_t>;

struct Parsed {
    traffic::Ipv4Header ip{};
    traffic::TcpHeader tcp{};
    const uint8_t* payload = nullptr;
    size_t payloadLen = 0;
};

Parsed parseOut(const Bytes& pkt) {
    Parsed p;
    traffic::parseIpv4(pkt.data(), pkt.size(), &p.ip);
    const uint8_t* transport = traffic::ipv4Payload(pkt.data(), pkt.size());
    size_t transportLen = pkt.size() - static_cast<size_t>(transport - pkt.data());
    traffic::parseTcp(transport, transportLen, &p.tcp);
    size_t off = traffic::tcpPayloadOffset(p.tcp);
    if (off < transportLen) {
        p.payload = transport + off;
        p.payloadLen = transportLen - off;
    }
    return p;
}

Bytes clientTcp(uint32_t seq, uint8_t flags, uint16_t window, const Bytes& payload,
                uint16_t dstPort = kPlainPort, uint32_t ack = 0) {
    return traffic::buildTcpPacket(kClientIp, kServerIp, kClientPort, dstPort, seq, ack, flags,
                                   window, payload.data(), payload.size());
}

FlowKey cf(uint16_t dstPort = kPlainPort) {
    FlowKey k;
    k.srcAddr = kClientIp;
    k.srcPort = kClientPort;
    k.dstAddr = kServerIp;
    k.dstPort = dstPort;
    return k;
}

Bytes clientUdp(uint16_t dstPort, const Bytes& payload) {
    return traffic::buildUdpPacket(kClientIp, kServerIp, kClientPort, dstPort, payload.data(),
                                    payload.size());
}

Bytes str(const std::string& s) { return Bytes(s.begin(), s.end()); }

std::string payloadOf(const Bytes& pkt) {
    Parsed p = parseOut(pkt);
    return std::string(p.payload, p.payload + p.payloadLen);
}

}  // namespace

TA_TEST(stack_syn_answers_synack_with_valid_checksums) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);

    TA_CHECK_EQ(out.size(), 1u);
    Parsed p = parseOut(out[0]);
    TA_CHECK_EQ(p.ip.srcAddr, kServerIp);   // packet FROM the original server
    TA_CHECK_EQ(p.ip.dstAddr, kClientIp);   // TO the client
    TA_CHECK_EQ(p.tcp.srcPort, kPlainPort);
    TA_CHECK_EQ(p.tcp.dstPort, kClientPort);
    TA_CHECK(p.tcp.has(TcpHeader::kSyn));
    TA_CHECK(p.tcp.has(TcpHeader::kAck));
    TA_CHECK_EQ(p.tcp.ack, 1001u);  // SYN consumed one sequence number
    TA_CHECK(p.tcp.seq != 0u);
    TA_CHECK(traffic::verifyIpChecksum(out[0].data(), out[0].size()));
    TA_CHECK(traffic::verifyTcpChecksum(out[0].data(), out[0].size()));

    auto connects = stack.takeConnects();
    TA_CHECK_EQ(connects.size(), 1u);
    TA_CHECK_EQ(connects[0].original.dstPort, kPlainPort);
    TA_CHECK_EQ(connects[0].effective.dstPort, kPlainPort);  // transparent, not redirected
    TA_CHECK(!connects[0].isUdp);
    TA_CHECK_EQ(stack.flowCount(), 1u);
    TA_CHECK(stack.takeSends().empty());
    TA_CHECK(stack.takeCloses().empty());
}

TA_TEST(stack_mitm_redirect_for_443_and_80) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(2000, TcpHeader::kSyn, 65535, {}, 443);
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Bytes syn80 = clientTcp(2000, TcpHeader::kSyn, 65535, {}, 80);
    stack.onTunPacket(syn80.data(), syn80.size(), 2, &out);

    auto connects = stack.takeConnects();
    TA_CHECK_EQ(connects.size(), 2u);
    TA_CHECK_EQ(connects[0].effective.dstAddr, 0x7F000001u);  // 127.0.0.1
    TA_CHECK_EQ(connects[0].effective.dstPort, 8843);
    TA_CHECK_EQ(connects[0].effective.srcPort, kClientPort);
    TA_CHECK_EQ(connects[1].effective.dstPort, 8808);  // plain HTTP relay port
    TA_CHECK_EQ(connects[1].effective.dstAddr, 0x7F000001u);

    // With MITM disabled everything stays transparent.
    StackConfig off;
    off.mitmEnabled = false;
    ForwardStack plain{off};
    Bytes syn2 = clientTcp(2000, TcpHeader::kSyn, 65535, {}, 443);
    plain.onTunPacket(syn2.data(), syn2.size(), 1, &out);
    auto c2 = plain.takeConnects();
    TA_CHECK_EQ(c2.size(), 1u);
    TA_CHECK_EQ(c2[0].effective.dstPort, 443);
    TA_CHECK_EQ(c2[0].effective.dstAddr, kServerIp);
}

TA_TEST(stack_client_data_relayed_dedup_and_overlap) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;

    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);

    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 2, &out);

    // In-order data.
    Bytes data = clientTcp(1001, TcpHeader::kPsh | TcpHeader::kAck, 65535, str("hello"));
    stack.onTunPacket(data.data(), data.size(), 3, &out);
    auto sends = stack.takeSends();
    TA_CHECK_EQ(sends.size(), 1u);
    TA_CHECK_ST(std::string(sends[0].data.begin(), sends[0].data.end()), "hello");
    Parsed dataAck = parseOut(out.back());
    TA_CHECK_EQ(dataAck.tcp.ack, 1006u);

    // Pure retransmission: acknowledged again, not delivered twice.
    stack.onTunPacket(data.data(), data.size(), 4, &out);
    TA_CHECK(stack.takeSends().empty());
    TA_CHECK_EQ(parseOut(out.back()).tcp.ack, 1006u);

    // Retransmission carrying more bytes: only the new tail is delivered.
    Bytes bigger = clientTcp(1001, TcpHeader::kPsh | TcpHeader::kAck, 65535, str("hello world"));
    stack.onTunPacket(bigger.data(), bigger.size(), 5, &out);
    auto tail = stack.takeSends();
    TA_CHECK_EQ(tail.size(), 1u);
    TA_CHECK_ST(std::string(tail[0].data.begin(), tail[0].data.end()), " world");
    TA_CHECK_EQ(parseOut(out.back()).tcp.ack, 1012u);
}

TA_TEST(stack_out_of_order_parked_then_delivered_in_order) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);
    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 2, &out);

    // Second half arrives first: parked with a duplicate ACK.
    Bytes second = clientTcp(1006, TcpHeader::kPsh | TcpHeader::kAck, 65535, str("world"));
    stack.onTunPacket(second.data(), second.size(), 3, &out);
    TA_CHECK(stack.takeSends().empty());
    TA_CHECK_EQ(parseOut(out.back()).tcp.ack, 1001u);

    // First half fills the gap; both halves flow out in order.
    Bytes first = clientTcp(1001, TcpHeader::kPsh | TcpHeader::kAck, 65535, str("hello"));
    stack.onTunPacket(first.data(), first.size(), 4, &out);
    auto sends = stack.takeSends();
    TA_CHECK_EQ(sends.size(), 2u);
    TA_CHECK_ST(std::string(sends[0].data.begin(), sends[0].data.end()), "hello");
    TA_CHECK_ST(std::string(sends[1].data.begin(), sends[1].data.end()), "world");
    TA_CHECK_EQ(parseOut(out.back()).tcp.ack, 1011u);
}

TA_TEST(stack_client_fin_acked_and_stale_fin_does_not_regress) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);
    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 2, &out);

    Bytes fin = clientTcp(1001, TcpHeader::kFin | TcpHeader::kAck, 65535, {});
    stack.onTunPacket(fin.data(), fin.size(), 3, &out);
    TA_CHECK_EQ(parseOut(out.back()).tcp.ack, 1002u);
    auto closes = stack.takeCloses();
    TA_CHECK_EQ(closes.size(), 1u);
    TA_CHECK_EQ(closes[0].flow.srcPort, kClientPort);
    TA_CHECK_EQ(stack.flowCount(), 1u);  // half-closed, still receives

    // A stale FIN retransmission must not rewind the ACK position.
    Bytes staleFin = clientTcp(1000, TcpHeader::kFin | TcpHeader::kAck, 65535, {});
    stack.onTunPacket(staleFin.data(), staleFin.size(), 4, &out);
    TA_CHECK_EQ(parseOut(out.back()).tcp.ack, 1002u);
}

TA_TEST(stack_upstream_data_reversal_checksums_and_mss) {
    StackConfig cfg;
    ForwardStack stack{cfg};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);
    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 2, &out);

    Bytes resp = str("resp");
    stack.onUpstreamData(cf(), resp.data(), resp.size(), 3, &out);
    TA_CHECK_EQ(out.size(), 2u);  // SYN-ACK + this data packet
    Parsed p = parseOut(out[1]);
    TA_CHECK_EQ(p.ip.srcAddr, kServerIp);
    TA_CHECK_EQ(p.ip.dstAddr, kClientIp);
    TA_CHECK_EQ(p.tcp.srcPort, kPlainPort);
    TA_CHECK_EQ(p.tcp.dstPort, kClientPort);
    TA_CHECK_EQ(p.tcp.seq, synack.tcp.seq + 1);
    TA_CHECK_EQ(p.tcp.ack, 1001u);
    TA_CHECK_ST(payloadOf(out[1]), "resp");
    TA_CHECK(traffic::verifyTcpChecksum(out[1].data(), out[1].size()));
}

TA_TEST(stack_upstream_data_chunked_by_mss) {
    StackConfig cfg;
    cfg.clientMss = 100;
    ForwardStack stack{cfg};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);
    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 2, &out);

    Bytes big(250, 0x41);
    stack.onUpstreamData(cf(), big.data(), big.size(), 3, &out);
    TA_CHECK_EQ(out.size(), 4u);  // SYN-ACK + 3 data segments
    TA_CHECK_EQ(parseOut(out[1]).payloadLen, 100u);
    TA_CHECK_EQ(parseOut(out[2]).payloadLen, 100u);
    TA_CHECK_EQ(parseOut(out[3]).payloadLen, 50u);
    uint32_t s2 = parseOut(out[1]).tcp.seq;
    TA_CHECK_EQ(parseOut(out[2]).tcp.seq, s2 + 100);
    TA_CHECK_EQ(parseOut(out[3]).tcp.seq, s2 + 200);
}

TA_TEST(stack_upstream_data_honors_client_window) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);

    // Client completes the handshake but advertises a small window (60).
    Bytes ack60 = clientTcp(1001, TcpHeader::kAck, 60, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack60.data(), ack60.size(), 2, &out);

    Bytes big(200, 0x42);
    stack.onUpstreamData(cf(), big.data(), big.size(), 3, &out);
    size_t afterFirst = out.size();
    TA_CHECK_EQ(afterFirst, 2u);                       // SYN-ACK + one data packet
    TA_CHECK_EQ(parseOut(out[1]).payloadLen, 60u);    // window capped

    // Client ACKs the 60 bytes but keeps the window small: next 60 flow out.
    Bytes ackMore = clientTcp(1001, TcpHeader::kAck, 60, {}, kPlainPort,
                              parseOut(out[1]).tcp.seq + 60);
    stack.onTunPacket(ackMore.data(), ackMore.size(), 4, &out);
    TA_CHECK_EQ(out.size(), 3u);
    TA_CHECK_EQ(parseOut(out[2]).payloadLen, 60u);
    TA_CHECK_EQ(parseOut(out[2]).tcp.seq, parseOut(out[1]).tcp.seq + 60);

    // A generous window flushes the remainder.
    Bytes ackWide = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort,
                              parseOut(out[2]).tcp.seq + 60);
    stack.onTunPacket(ackWide.data(), ackWide.size(), 5, &out);
    TA_CHECK_EQ(out.size(), 4u);
    TA_CHECK_EQ(parseOut(out[3]).payloadLen, 80u);

    // A pure ACK with nothing pending produces no output at all.
    Bytes idle = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort,
                           parseOut(out[3]).tcp.seq + 80);
    stack.onTunPacket(idle.data(), idle.size(), 6, &out);
    TA_CHECK_EQ(out.size(), 4u);
}

TA_TEST(stack_upstream_close_emits_fin_then_flow_completes) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);
    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 2, &out);

    Bytes resp = str("abc");
    stack.onUpstreamData(cf(), resp.data(), resp.size(), 3, &out);
    stack.onUpstreamClosed(cf(), 4, &out);
    Parsed fin = parseOut(out.back());
    TA_CHECK(fin.tcp.has(TcpHeader::kFin));
    TA_CHECK(fin.tcp.has(TcpHeader::kAck));
    TA_CHECK_EQ(fin.payloadLen, 0u);
    TA_CHECK_EQ(fin.tcp.seq, synack.tcp.seq + 1 + 3);

    // ACKing only the data (not the FIN) keeps the flow alive...
    Bytes ackData = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, fin.tcp.seq);
    stack.onTunPacket(ackData.data(), ackData.size(), 5, &out);
    TA_CHECK_EQ(stack.flowCount(), 1u);

    // ...ACKing the FIN completes it.
    Bytes ackFin = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, fin.tcp.seq + 1);
    stack.onTunPacket(ackFin.data(), ackFin.size(), 6, &out);
    TA_CHECK_EQ(stack.flowCount(), 0u);
}

TA_TEST(stack_client_rst_removes_flow_unknown_rst_is_silent) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes rst = clientTcp(1000, TcpHeader::kRst, 0, {});
    stack.onTunPacket(rst.data(), rst.size(), 1, &out);  // unknown flow
    TA_CHECK(out.empty());
    TA_CHECK(stack.takeCloses().empty());

    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 2, &out);
    TA_CHECK_EQ(stack.flowCount(), 1u);

    Bytes rst2 = clientTcp(1001, TcpHeader::kRst, 0, {});
    stack.onTunPacket(rst2.data(), rst2.size(), 3, &out);
    TA_CHECK_EQ(stack.flowCount(), 0u);
    auto closes = stack.takeCloses();
    TA_CHECK_EQ(closes.size(), 1u);
    TA_CHECK_EQ(closes[0].flow.srcPort, kClientPort);
}

TA_TEST(stack_syn_retrans_reanswered_only_before_established) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    TA_CHECK_EQ(out.size(), 1u);
    stack.onTunPacket(syn.data(), syn.size(), 2, &out);  // retransmitted SYN
    TA_CHECK_EQ(out.size(), 2u);
    Parsed synack = parseOut(out[1]);
    TA_CHECK_EQ(synack.tcp.seq, parseOut(out[0]).tcp.seq);  // same iss
    TA_CHECK_EQ(synack.tcp.ack, 1001u);

    Bytes ack = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ack.data(), ack.size(), 3, &out);
    TA_CHECK_EQ(out.size(), 2u);  // pure ACK produces nothing

    // A stray duplicate SYN after establishment is ignored, not re-answered.
    stack.onTunPacket(syn.data(), syn.size(), 4, &out);
    TA_CHECK_EQ(out.size(), 2u);
}

TA_TEST(stack_udp_forwarded_and_upstream_reversed) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;

    Bytes dns = clientUdp(53, str("qq"));
    stack.onTunPacket(dns.data(), dns.size(), 1, &out);
    TA_CHECK(out.empty());  // UDP is connectionless: no handshake packets
    auto connects = stack.takeConnects();
    TA_CHECK_EQ(connects.size(), 1u);
    TA_CHECK(connects[0].isUdp);
    TA_CHECK_EQ(connects[0].effective.dstPort, 53);
    auto sends = stack.takeSends();
    TA_CHECK_EQ(sends.size(), 1u);
    TA_CHECK_ST(std::string(sends[0].data.begin(), sends[0].data.end()), "qq");

    // A second datagram on the same flow does not queue another connect.
    stack.onTunPacket(dns.data(), dns.size(), 2, &out);
    TA_CHECK(stack.takeConnects().empty());
    TA_CHECK_EQ(stack.takeSends().size(), 1u);

    // Upstream reply is wrapped back towards the client.
    stack.onUpstreamData(cf(53), str("rr").data(), 2, 3, &out);
    TA_CHECK_EQ(out.size(), 1u);
    traffic::Ipv4Header ip{};
    traffic::parseIpv4(out[0].data(), out[0].size(), &ip);
    TA_CHECK_EQ(ip.srcAddr, kServerIp);
    TA_CHECK_EQ(ip.dstAddr, kClientIp);
    const uint8_t* transport = traffic::ipv4Payload(out[0].data(), out[0].size());
    traffic::UdpHeader udp{};
    traffic::parseUdp(transport, out[0].size() - 20, &udp);
    TA_CHECK_EQ(udp.srcPort, 53);
    TA_CHECK_EQ(udp.dstPort, kClientPort);
    TA_CHECK_EQ(out[0].size() - 28u, 2u);  // payload length
}

TA_TEST(stack_udp_443_quic_blocked) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes quic = clientUdp(443, str("q"));
    stack.onTunPacket(quic.data(), quic.size(), 1, &out);
    TA_CHECK(out.empty());
    TA_CHECK(stack.takeConnects().empty());
    TA_CHECK(stack.takeSends().empty());
    TA_CHECK_EQ(stack.quicDropped(), 1u);
    TA_CHECK_EQ(stack.flowCount(), 0u);
}

TA_TEST(stack_unknown_udp_close_is_silent) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    // Closing a flow we never saw must not queue a Close.
    stack.onUpstreamClosed(cf(53), 1, &out);
    TA_CHECK(stack.takeCloses().empty());

    // A real UDP flow does close cleanly.
    Bytes dns = clientUdp(53, str("qq"));
    stack.onTunPacket(dns.data(), dns.size(), 2, &out);
    stack.onUpstreamClosed(cf(53), 3, &out);
    auto closes = stack.takeCloses();
    TA_CHECK_EQ(closes.size(), 1u);
    TA_CHECK_EQ(closes[0].flow.dstPort, 53);
}

TA_TEST(stack_udp_sweep_boundary) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes dns = clientUdp(53, str("qq"));
    stack.onTunPacket(dns.data(), dns.size(), 1000, &out);

    stack.sweep(1000 + 60000, &out);  // exactly at the timeout: still alive
    TA_CHECK_EQ(stack.udpFlowCount(), 1u);
    TA_CHECK(stack.takeCloses().empty());

    stack.sweep(1000 + 60001, &out);  // one past it: swept
    TA_CHECK_EQ(stack.udpFlowCount(), 0u);
    TA_CHECK_EQ(stack.takeCloses().size(), 1u);
}

TA_TEST(stack_midstream_flow_adopted) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes data = clientTcp(5000, TcpHeader::kPsh | TcpHeader::kAck, 65535, str("hi"));
    stack.onTunPacket(data.data(), data.size(), 1, &out);
    auto connects = stack.takeConnects();
    TA_CHECK_EQ(connects.size(), 1u);
    TA_CHECK_EQ(connects[0].original.dstPort, kPlainPort);
    auto sends = stack.takeSends();
    TA_CHECK_EQ(sends.size(), 1u);
    TA_CHECK_ST(std::string(sends[0].data.begin(), sends[0].data.end()), "hi");
    TA_CHECK_EQ(parseOut(out[0]).tcp.ack, 5002u);
    TA_CHECK_EQ(stack.flowCount(), 1u);
}

TA_TEST(stack_sweep_boundary_and_expiry) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1000, &out);

    stack.sweep(1000 + 60000, &out);  // exactly at the timeout: still alive
    TA_CHECK_EQ(stack.flowCount(), 1u);
    TA_CHECK(stack.takeCloses().empty());

    stack.sweep(1000 + 60001, &out);  // one past it: swept with an RST
    TA_CHECK_EQ(stack.flowCount(), 0u);
    TA_CHECK_EQ(stack.takeCloses().size(), 1u);
    TA_CHECK(parseOut(out.back()).tcp.has(TcpHeader::kRst));
}

TA_TEST(stack_fin_with_pending_upstream_data_sends_data_first) {
    ForwardStack stack{StackConfig{}};
    std::vector<Bytes> out;
    Bytes syn = clientTcp(1000, TcpHeader::kSyn, 65535, {});
    stack.onTunPacket(syn.data(), syn.size(), 1, &out);
    Parsed synack = parseOut(out[0]);
    // Handshake with a zero-ish window parks everything upstream sends.
    Bytes ackZero = clientTcp(1001, TcpHeader::kAck, 0, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ackZero.data(), ackZero.size(), 2, &out);

    Bytes resp = str("late");
    stack.onUpstreamData(cf(), resp.data(), resp.size(), 3, &out);
    TA_CHECK_EQ(out.size(), 1u);  // nothing could be sent (window 0)

    stack.onUpstreamClosed(cf(), 4, &out);
    TA_CHECK_EQ(out.size(), 1u);  // FIN must wait for the queued data

    // Client opens the window: data first, then the FIN.
    Bytes ackWide = clientTcp(1001, TcpHeader::kAck, 65535, {}, kPlainPort, synack.tcp.seq + 1);
    stack.onTunPacket(ackWide.data(), ackWide.size(), 5, &out);
    TA_CHECK_EQ(out.size(), 3u);
    TA_CHECK_ST(payloadOf(out[1]), "late");
    TA_CHECK(parseOut(out[2]).tcp.has(TcpHeader::kFin));
    TA_CHECK(!parseOut(out[1]).tcp.has(TcpHeader::kFin));
}

TA_TEST(stack_packet_builder_checksum_and_layout) {
    // Exact checksum values for a known buffer (RFC 1071 worked example).
    const uint8_t data[12] = {0x00, 0x01, 0xf2, 0x03, 0xf4, 0xf5, 0xf6, 0xf7};
    TA_CHECK_EQ(traffic::ipChecksum(data, 8), 0x220du);

    // Odd-length buffer takes the trailing byte as the high octet.
    const uint8_t odd[3] = {0x12, 0x34, 0x56};
    TA_CHECK_EQ(traffic::ipChecksum(odd, 3), static_cast<uint16_t>(~((0x1234 + 0x5600) & 0xFFFF)));

    // A corrupted packet must not verify.
    Bytes good = traffic::buildTcpPacket(kClientIp, kServerIp, 1, 2, 3, 4, TcpHeader::kAck, 100,
                                         str("x").data(), 1);
    TA_CHECK(traffic::verifyIpChecksum(good.data(), good.size()));
    TA_CHECK(traffic::verifyTcpChecksum(good.data(), good.size()));
    Bytes bad = good;
    bad[20 + 4] ^= 0x01;  // corrupt the sequence number
    TA_CHECK(!traffic::verifyTcpChecksum(bad.data(), bad.size()));
}
