#pragma once

#include <cstddef>
#include <cstdint>
#include <map>
#include <string>
#include <vector>

#include "http1.h"
#include "ip.h"
#include "tcp.h"

namespace traffic {

struct FlowKey {
    uint32_t srcAddr = 0;
    uint16_t srcPort = 0;
    uint32_t dstAddr = 0;
    uint16_t dstPort = 0;

    bool operator<(const FlowKey& o) const {
        if (srcAddr != o.srcAddr) return srcAddr < o.srcAddr;
        if (srcPort != o.srcPort) return srcPort < o.srcPort;
        if (dstAddr != o.dstAddr) return dstAddr < o.dstAddr;
        return dstPort < o.dstPort;
    }
    bool operator==(const FlowKey& o) const {
        return srcAddr == o.srcAddr && srcPort == o.srcPort && dstAddr == o.dstAddr &&
               dstPort == o.dstPort;
    }
};

struct EngineEvent {
    enum class Kind { TcpReset, TlsSniDetected, Http1RequestDetected, Http1ResponseDetected, QuicDetected };
    Kind kind = Kind::TcpReset;
    FlowKey flow;
    uint64_t timestampMs = 0;
    std::string text;     // SNI or "GET /path"
    int32_t numeric = 0;  // e.g. QUIC version
};

// TCP stream reassembly: dedup of retransmissions, out-of-order buffering,
// reset handling. Accepted in-order data is forwarded to the listener.
class TcpReassembly {
public:
    struct Listener {
        virtual ~Listener() = default;
        virtual void onSegment(const FlowKey& flow, const uint8_t* payload, size_t len) = 0;
        virtual void onReset(const FlowKey& flow) { (void)flow; }
    };

    explicit TcpReassembly(Listener* listener) : listener_(listener) {}

    void onSegment(const FlowKey& flow, uint32_t seq, uint8_t tcpFlags, const uint8_t* payload,
                   size_t len);
    void resetFlow(const FlowKey& flow);

    // Bytes currently buffered (delivered + pending) for a flow.
    size_t buffered(const FlowKey& flow) const;
    size_t flowCount() const { return flows_.size(); }

private:
    struct FlowState {
        bool started = false;
        uint32_t nextSeq = 0;
        std::map<uint32_t, std::vector<uint8_t>> pending;  // out-of-order segments
        size_t total = 0;
    };

    void accept(FlowState& st, const FlowKey& flow, const uint8_t* data, size_t len);
    void drainPending(FlowState& st, const FlowKey& flow);

    Listener* listener_;
    std::map<FlowKey, FlowState> flows_;
};

// L1/L2 engine: feeds raw IPv4 packets, reassembles TCP and emits protocol
// detection events (TLS SNI, HTTP/1 requests/responses, QUIC).
class Engine : public TcpReassembly::Listener {
public:
    Engine() : reassembly_(this) {}

    // Feed one raw IPv4 packet; returns IP parse status.
    Ipv4Status feedPacket(const uint8_t* ipPkt, size_t len, uint64_t timestampMs);

    void onSegment(const FlowKey& flow, const uint8_t* payload, size_t len) override;
    void onReset(const FlowKey& flow) override;

    const std::vector<EngineEvent>& events() const { return events_; }
    void clearEvents() { events_.clear(); }

private:
    struct ProtoState {
        bool sniDone = false;
        bool httpDone = false;
    };

    void inspect(const FlowKey& flow, const uint8_t* data, size_t len, uint64_t ts);

    TcpReassembly reassembly_;
    std::map<FlowKey, ProtoState> proto_;
    std::vector<EngineEvent> events_;
    uint64_t lastTs_ = 0;
};

}  // namespace traffic
