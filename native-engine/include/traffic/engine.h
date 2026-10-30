#pragma once

#include <cstddef>
#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "http1.h"
#include "http1flow.h"
#include "http2flow.h"
#include "ip.h"
#include "tcp.h"
#include "ws.h"

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
    enum class Kind {
        TcpReset,
        TlsSniDetected,
        Http1RequestDetected,
        Http1ResponseDetected,
        QuicDetected,
        // --- extensions (Task 2-a) ---
        Http2HeadersDetected,  // text: first decoded HPACK headers
        TlsJa3Detected,         // text: "sni|ja3md5"
        DnsMessageParsed,       // text: "example.com A 1.2.3.4" / "example.com?"
        // --- extensions (engine deep dive) ---
        GrpcMessageDetected,    // text: "grpc <len>B <preview>", numeric: stream id
        WsMessageDetected       // text: "c>s text 12B <preview>" (added with WS wiring)
    };
    Kind kind = EngineEvent::Kind::TcpReset;
    FlowKey flow;
    uint64_t timestampMs = 0;
    std::string text;     // SNI or "GET /path"
    int32_t numeric = 0;  // e.g. QUIC version, HTTP/2 stream id
};

// One request/response exchange as seen on the wire. Bodies are capped at
// Http1FlowParser::kMaxBodyBytes per direction.
struct HttpExchangeRecord {
    FlowKey flow;  // client -> server direction
    uint64_t timestampMs = 0;
    Http1Request request;
    Http1Response response;
    std::vector<uint8_t> requestBody;
    std::vector<uint8_t> responseBody;
    std::vector<uint8_t> responseDecoded;  // gzip/deflate decoded when possible
    std::string responseMime;
    bool truncated = false;
    std::string protocol = "HTTP1";  // "HTTP1" or "HTTP2" (stream-level capture)
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
// detection events (TLS SNI/JA3, HTTP/1 requests/responses with exchange
// pairing, HTTP/2 header blocks, DNS, QUIC).
class Engine : public TcpReassembly::Listener {
public:
    Engine() : reassembly_(this) {}

    // Feed one raw IPv4 packet; returns IP parse status.
    Ipv4Status feedPacket(const uint8_t* ipPkt, size_t len, uint64_t timestampMs);

    void onSegment(const FlowKey& flow, const uint8_t* payload, size_t len) override;
    void onReset(const FlowKey& flow) override;

    const std::vector<EngineEvent>& events() const { return events_; }
    void clearEvents() { events_.clear(); }

    const std::vector<HttpExchangeRecord>& exchanges() const { return exchanges_; }
    void clearExchanges() { exchanges_.clear(); }

private:
    // Both directions of a TCP conversation resolve to one Conversation.
    struct Conversation {
        enum class Kind { Unknown, Http, Tls, H2, Skip };

        Kind kind = Kind::Unknown;
        FlowKey clientFlow;        // client -> server direction
        bool clientKnown = false;
        bool sniDone = false;
        bool ja3Done = false;
        std::vector<uint8_t> helloBuf;  // leading ClientHello bytes (cap 8 KiB)

        Http1FlowParser req{Http1FlowParser::Mode::Requests};
        Http1FlowParser resp{Http1FlowParser::Mode::Responses};
        std::vector<Http1Message> pendingRequests;  // FIFO awaiting responses

        // Websocket tunnel state after a 101 Switching Protocols.
        struct WsState {
            bool active = false;
            WsMessageAssembler c2s;  // client -> server direction
            WsMessageAssembler s2c;  // server -> client direction
        };
        WsState ws;

        // HTTP/2 per-direction raw frame buffer (index 0 = client, 1 = server).
        struct H2Dir {
            std::vector<uint8_t> buf;
        };
        H2Dir h2[2];
        H2StreamTracker h2Streams;  // stream-level reassembly + gRPC framing
        std::map<uint32_t, uint64_t> h2StreamBytes;  // DATA bytes per stream
        size_t h2PrefaceConsumed = 0;                // client preface skip state

        uint8_t probe[24] = {};  // leading bytes used for direction sniffing
        size_t probeLen = 0;
    };

    void inspect(const FlowKey& flow, const uint8_t* data, size_t len, uint64_t ts);
    Conversation* conversationFor(const FlowKey& flow);
    void classify(const FlowKey& flow, const uint8_t* data, size_t len, uint64_t ts);
    void feedHttp(Conversation& c, bool clientSide, const uint8_t* data, size_t len, uint64_t ts);
    void feedWs(Conversation& c, bool clientSide, const uint8_t* data, size_t len, uint64_t ts);
    void feedTls(Conversation& c, bool clientSide, const uint8_t* data, size_t len, uint64_t ts);
    void feedH2(Conversation& c, bool clientSide, const uint8_t* data, size_t len, uint64_t ts);
    void drainParserMessages(Conversation& c, uint64_t ts);
    void emitHttp2Headers(Conversation& c, uint32_t streamId, const uint8_t* block, size_t len,
                          uint64_t ts);
    void emitHttp2HeaderList(Conversation& c, uint32_t streamId,
                             const std::vector<HpackHeader>& headers, uint64_t ts);
    void emitH2Exchange(Conversation& c, const H2StreamRecord& rec, uint64_t ts);
    void handleDns(const FlowKey& flow, uint32_t srcPort, uint32_t dstPort, const uint8_t* payload,
                  size_t len, uint64_t ts);

    TcpReassembly reassembly_;
    std::map<FlowKey, std::shared_ptr<Conversation>> convByFlow_;
    std::vector<EngineEvent> events_;
    std::vector<HttpExchangeRecord> exchanges_;
    uint64_t lastTs_ = 0;
};

}  // namespace traffic
