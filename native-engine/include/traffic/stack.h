#pragma once

// User-space TCP/IP forwarding stack (基建一「通」).
//
// The Android VpnService feeds every packet that the device sends into a TUN
// interface. ForwardStack plays the "other end" of those connections:
//
//   * it answers TCP SYNs with SYN-ACKs so device apps believe the remote
//     server accepted the connection,
//   * it ACKs and relays client payload (dedup + out-of-order repair) to the
//     Kotlin socket layer, which opens real protected sockets upstream,
//   * it relays upstream bytes back towards the client with correct sequence
//     numbers, honoring the client's advertised receive window,
//   * it can redirect TLS(443)/HTTP(80) flows to the local MITM proxy and drop
//     QUIC (UDP 443) so browsers fall back to interceptable TCP TLS.
//
// Single-threaded by design: the VpnService engine loop owns the only
// reference. All commands/results are exchanged via plain vectors.

#include <cstddef>
#include <cstdint>
#include <map>
#include <vector>

#include "engine.h"
#include "ip.h"
#include "tcp.h"
#include "udp.h"

namespace traffic {

struct StackConfig {
    bool mitmEnabled = true;
    uint32_t proxyIp = 0x7F000001;  // 127.0.0.1 (raw network order)
    uint16_t tlsProxyPort = 8843;
    uint16_t plainProxyPort = 8808;
    uint16_t tlsPort = 443;
    uint16_t httpPort = 80;
    bool blockQuic = true;
    uint32_t clientMss = 1300;          // our segments towards the client
    uint32_t ourWindow = 0xFFFF;        // window we advertise to the client
    uint64_t idleTimeoutMs = 60000;
};

class ForwardStack {
public:
    struct Connect {
        FlowKey original;    // what the app thinks it talks to
        FlowKey effective;   // where the socket layer should really connect
        bool isUdp = false;
    };
    struct Send {
        FlowKey flow;                 // client-side flow key (client -> peer)
        std::vector<uint8_t> data;    // payload to write upstream
        bool isUdp = false;
    };
    struct Close {
        FlowKey flow;
    };

    explicit ForwardStack(const StackConfig& cfg, uint32_t issSeed = 0x12345678u);

    // A packet read from the TUN fd (client -> network direction).
    void onTunPacket(const uint8_t* pkt, size_t len, uint64_t nowMs,
                     std::vector<std::vector<uint8_t>>* outToTun);

    // Upstream socket produced bytes (network -> client direction).
    void onUpstreamData(const FlowKey& clientFlow, const uint8_t* data, size_t len,
                        uint64_t nowMs, std::vector<std::vector<uint8_t>>* outToTun);

    // Upstream socket hit EOF / error.
    void onUpstreamClosed(const FlowKey& clientFlow, uint64_t nowMs,
                          std::vector<std::vector<uint8_t>>* outToTun);

    // Drops idle flows (emits RST + Close for them).
    void sweep(uint64_t nowMs, std::vector<std::vector<uint8_t>>* outToTun);

    std::vector<Connect> takeConnects() { return std::move(connects_); }
    std::vector<Send> takeSends() { return std::move(sends_); }
    std::vector<Close> takeCloses() { return std::move(closes_); }

    size_t flowCount() const { return tcp_.size() + udp_.size(); }
    size_t udpFlowCount() const { return udp_.size(); }
    uint64_t packetsFromTun() const { return packetsFromTun_; }
    uint64_t packetsToTun() const { return packetsToTun_; }
    uint64_t quicDropped() const { return quicDropped_; }

private:
    struct TcpFlow {
        enum class St { SynReceived, Established, ClientFin } st = St::SynReceived;
        uint32_t clientIss = 0;       // client initial sequence number
        uint32_t nextClientByte = 0;  // our cumulative ACK position
        uint32_t iss = 0;             // our initial sequence number
        uint32_t ourSeq = 0;          // next byte we will send to the client
        uint32_t lastClientAck = 0;   // highest client ACK of our data
        uint16_t clientWindow = 65535;
        FlowKey effective{};
        std::map<uint32_t, std::vector<uint8_t>> pending;  // out-of-order park
        std::vector<uint8_t> sendQueue;                    // window-throttled
        bool upstreamClosed = false;
        bool finSent = false;
        uint64_t lastActiveMs = 0;
    };
    struct UdpFlow {
        uint64_t lastActiveMs = 0;
    };

    void handleTcp(const Ipv4Header& ip, const TcpHeader& tcp, const uint8_t* payload,
                   size_t len, uint64_t nowMs, std::vector<std::vector<uint8_t>>* out);
    void handleUdp(const Ipv4Header& ip, const UdpHeader& udp, const uint8_t* payload,
                   size_t len, uint64_t nowMs);
    void emitSegment(TcpFlow& f, const FlowKey& cf, uint8_t flags, const uint8_t* data,
                     size_t len, std::vector<std::vector<uint8_t>>* out);
    void emitAck(TcpFlow& f, const FlowKey& cf, std::vector<std::vector<uint8_t>>* out);
    void acceptClientData(TcpFlow& f, const FlowKey& cf, const uint8_t* data, size_t len,
                          std::vector<std::vector<uint8_t>>* out);
    void drainPending(TcpFlow& f, const FlowKey& cf, std::vector<std::vector<uint8_t>>* out);
    void flushSendQueue(TcpFlow& f, const FlowKey& cf, std::vector<std::vector<uint8_t>>* out);
    void maybeSendFin(TcpFlow& f, const FlowKey& cf, std::vector<std::vector<uint8_t>>* out);
    FlowKey targetFor(const FlowKey& original) const;
    uint32_t nextIss();

    StackConfig cfg_;
    std::map<FlowKey, TcpFlow> tcp_;
    std::map<FlowKey, UdpFlow> udp_;
    std::vector<Connect> connects_;
    std::vector<Send> sends_;
    std::vector<Close> closes_;
    uint32_t issState_;
    uint16_t ipId_ = 0x0100;
    uint64_t packetsFromTun_ = 0;
    uint64_t packetsToTun_ = 0;
    uint64_t quicDropped_ = 0;
};

}  // namespace traffic
