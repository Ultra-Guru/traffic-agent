#include "traffic/engine.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

FlowKey makeFlow(uint16_t srcPort) {
    FlowKey k;
    k.srcAddr = 0x0A000001;
    k.srcPort = srcPort;
    k.dstAddr = 0x08080808;
    k.dstPort = 80;
    return k;
}

struct Collector : TcpReassembly::Listener {
    std::vector<std::pair<FlowKey, std::vector<uint8_t>>> received;
    std::vector<FlowKey> resets;
    void onSegment(const FlowKey& f, const uint8_t* p, size_t n) override {
        received.emplace_back(f, std::vector<uint8_t>(p, p + n));
    }
    void onReset(const FlowKey& f) override { resets.push_back(f); }
};

}  // namespace

TA_TEST(reassembly_in_order_delivery) {
    Collector c;
    TcpReassembly r(&c);
    auto f = makeFlow(1111);
    r.onSegment(f, 1000, TcpHeader::kAck, tb::str("AB").data(), 2);
    r.onSegment(f, 1002, TcpHeader::kAck, tb::str("CD").data(), 2);
    TA_CHECK_EQ(c.received.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(r.buffered(f), static_cast<size_t>(4));
}

TA_TEST(reassembly_dedups_retransmission) {
    Collector c;
    TcpReassembly r(&c);
    auto f = makeFlow(2222);
    r.onSegment(f, 1000, TcpHeader::kAck, tb::str("AB").data(), 2);
    r.onSegment(f, 1000, TcpHeader::kAck, tb::str("AB").data(), 2);  // retransmit
    r.onSegment(f, 999, TcpHeader::kAck, tb::str("XAB").data(), 3);  // overlapping
    TA_CHECK_EQ(c.received.size(), static_cast<size_t>(1));
}

TA_TEST(reassembly_buffers_out_of_order_then_drains) {
    Collector c;
    TcpReassembly r(&c);
    auto f = makeFlow(3333);
    r.onSegment(f, 1000, TcpHeader::kAck, tb::str("AB").data(), 2);  // delivered, next=1002
    r.onSegment(f, 1004, TcpHeader::kAck, tb::str("CD").data(), 2);  // parked (gap at 1002)
    r.onSegment(f, 1006, TcpHeader::kAck, tb::str("EF").data(), 2);  // parked (gap chain)
    TA_CHECK_EQ(c.received.size(), static_cast<size_t>(1));
    r.onSegment(f, 1002, TcpHeader::kAck, tb::str("GH").data(), 2);  // delivered, drains CD+EF
    TA_CHECK_EQ(c.received.size(), static_cast<size_t>(4));         // AB, GH, CD, EF
    TA_CHECK_EQ(r.buffered(f), static_cast<size_t>(8));
}

TA_TEST(reassembly_syn_advances_baseline) {
    Collector c;
    TcpReassembly r(&c);
    auto f = makeFlow(4444);
    r.onSegment(f, 5000, TcpHeader::kSyn, {}, 0);
    r.onSegment(f, 5001, TcpHeader::kAck, tb::str("X").data(), 1);  // seq continues after SYN
    TA_CHECK_EQ(c.received.size(), static_cast<size_t>(1));
    r.onSegment(f, 5001, TcpHeader::kAck, tb::str("X").data(), 1);  // dup ignored
    TA_CHECK_EQ(c.received.size(), static_cast<size_t>(1));
}

TA_TEST(reassembly_reset_clears_flow) {
    Collector c;
    TcpReassembly r(&c);
    auto f = makeFlow(5555);
    r.onSegment(f, 1000, TcpHeader::kAck, tb::str("AB").data(), 2);
    r.onSegment(f, 1002, TcpHeader::kRst | TcpHeader::kAck, tb::str("ZZ").data(), 2);
    TA_CHECK_EQ(c.resets.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(r.buffered(f), static_cast<size_t>(0));
    TA_CHECK_EQ(r.flowCount(), static_cast<size_t>(0));
}

TA_TEST(engine_detects_http_request_from_packet) {
    Engine e;
    std::string raw = "GET /a HTTP/1.1\r\nHost: h.io\r\n\r\n";
    auto pkt = tb::ipv4(tb::tcpSegment(1000, TcpHeader::kPsh | TcpHeader::kAck, tb::str(raw)));
    e.feedPacket(pkt.data(), pkt.size(), 1700000000123ULL);
    TA_CHECK_EQ(e.events().size(), static_cast<size_t>(1));
    TA_CHECK(e.events()[0].kind == EngineEvent::Kind::Http1RequestDetected);
    TA_CHECK_ST(e.events()[0].text, "GET /a");
    TA_CHECK_EQ(e.events()[0].timestampMs, 1700000000123ULL);
}

TA_TEST(engine_detects_tls_sni_from_packet) {
    Engine e;
    auto hello = tb::clientHello("secure.example.net");
    auto pkt = tb::ipv4(tb::tcpSegment(7000, TcpHeader::kPsh | TcpHeader::kAck, hello));
    e.feedPacket(pkt.data(), pkt.size(), 17ULL);
    TA_CHECK_EQ(e.events().size(), static_cast<size_t>(1));
    TA_CHECK(e.events()[0].kind == EngineEvent::Kind::TlsSniDetected);
    TA_CHECK_ST(e.events()[0].text, "secure.example.net");
}

TA_TEST(engine_detects_http_response) {
    Engine e;
    std::string raw = "HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n";
    auto pkt = tb::ipv4(tb::tcpSegment(900, TcpHeader::kPsh | TcpHeader::kAck, tb::str(raw)));
    e.feedPacket(pkt.data(), pkt.size(), 5ULL);
    TA_CHECK_EQ(e.events().size(), static_cast<size_t>(1));
    TA_CHECK(e.events()[0].kind == EngineEvent::Kind::Http1ResponseDetected);
    TA_CHECK_ST(e.events()[0].text, "204 No Content");
}

TA_TEST(engine_detects_quic_on_udp_443) {
    Engine e;
    Bytes q = {0xC0, 0x00, 0x00, 0x00, 0x01, 0x08, 0x09};
    auto pkt = tb::ipv4(tb::udpDatagram(50000, 443, q), 17);
    TA_CHECK_EQ(e.feedPacket(pkt.data(), pkt.size(), 9ULL), Ipv4Status::Ok);
    TA_CHECK_EQ(e.events().size(), static_cast<size_t>(1));
    TA_CHECK(e.events()[0].kind == EngineEvent::Kind::QuicDetected);
    TA_CHECK_EQ(e.events()[0].numeric, 1);
}

TA_TEST(engine_ignores_udp_443_non_quic) {
    Engine e;
    auto pkt = tb::ipv4(tb::udpDatagram(50000, 443, {0x00, 0x01, 0x02, 0x03, 0x04, 0x05}), 17);
    e.feedPacket(pkt.data(), pkt.size(), 9ULL);
    TA_CHECK(e.events().empty());
}

TA_TEST(engine_rejects_invalid_ip) {
    Engine e;
    Bytes bad(10, 0);
    TA_CHECK_EQ(e.feedPacket(bad.data(), bad.size(), 0ULL), Ipv4Status::TooShort);
}

TA_TEST(engine_events_once_per_flow) {
    Engine e;
    std::string raw = "GET /once HTTP/1.1\r\nHost: h\r\n\r\n";
    auto seg = tb::tcpSegment(1000, TcpHeader::kPsh | TcpHeader::kAck, tb::str(raw));
    auto pkt = tb::ipv4(seg);
    e.feedPacket(pkt.data(), pkt.size(), 1ULL);
    e.feedPacket(pkt.data(), pkt.size(), 2ULL);  // same packet again -> retransmission
    TA_CHECK_EQ(e.events().size(), static_cast<size_t>(1));
}
