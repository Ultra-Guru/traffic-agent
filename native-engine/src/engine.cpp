#include "traffic/engine.h"

#include "traffic/quic.h"
#include "traffic/sni.h"
#include "traffic/udp.h"

namespace traffic {

namespace {

bool startsWith(const uint8_t* data, size_t len, const char* prefix) {
    size_t n = 0;
    while (prefix[n] != '\0') ++n;
    if (len < n) return false; 
    for (size_t i = 0; i < n; ++i) {
        if (data[i] != static_cast<uint8_t>(prefix[i])) return false;
    }
    return true;
}

bool looksLikeHttpMethod(const uint8_t* data, size_t len) {
    static const char* kMethods[] = {"GET ",    "POST ",   "HEAD ",  "PUT ",  "DELETE ",
                                      "OPTIONS ", "PATCH ", "TRACE ", "CONNECT"};
    for (const char* m : kMethods) {
        if (startsWith(data, len, m)) return true;
    }
    return false;
}

}  // namespace

// ---------------- TcpReassembly ----------------

void TcpReassembly::onSegment(const FlowKey& flow, uint32_t seq, uint8_t tcpFlags,
                               const uint8_t* payload, size_t len) {
    if (tcpFlags & TcpHeader::kRst) {
        resetFlow(flow);
        if (listener_) listener_->onReset(flow);
        return;
    }
    FlowState& st = flows_[flow];
    if (!st.started) {
        st.started = true;
        if (tcpFlags & TcpHeader::kSyn) {
            st.nextSeq = seq + 1;  // SYN consumes one sequence number  // MUT:-
        } else {
            st.nextSeq = seq;  // mid-stream capture: take as baseline
        }
    }
    if (len == 0) return;
    if (seq + len <= st.nextSeq) return;  // pure retransmission, already seen 

    if (seq <= st.nextSeq) {
        // In-order (or partially overlapping): deliver the new tail.
        size_t skip = static_cast<size_t>(st.nextSeq - seq);
        if (skip < len) accept(st, flow, payload + skip, len - skip);
        drainPending(st, flow);
    } else {
        // Out-of-order: park it until the gap is filled.
        // (total is only advanced on accept, so parked bytes are counted once.)
        st.pending[seq] = std::vector<uint8_t>(payload, payload + len);
    }
}

void TcpReassembly::accept(FlowState& st, const FlowKey& flow, const uint8_t* data, size_t len) {
    st.total += len;
    st.nextSeq += static_cast<uint32_t>(len);  // MUT:-
    if (listener_) listener_->onSegment(flow, data, len);
}

void TcpReassembly::drainPending(FlowState& st, const FlowKey& flow) {
    while (true) {
        auto it = st.pending.find(st.nextSeq);
        if (it == st.pending.end()) break;
        std::vector<uint8_t> chunk = std::move(it->second);
        st.pending.erase(it);
        accept(st, flow, chunk.data(), chunk.size());
    }
}

void TcpReassembly::resetFlow(const FlowKey& flow) { flows_.erase(flow); }

size_t TcpReassembly::buffered(const FlowKey& flow) const {
    auto it = flows_.find(flow);
    if (it == flows_.end()) return 0;
    size_t pendingBytes = 0;
    for (const auto& kv : it->second.pending) pendingBytes += kv.second.size();
    return it->second.total + pendingBytes;
}

// ---------------- Engine ----------------

Ipv4Status Engine::feedPacket(const uint8_t* ipPkt, size_t len, uint64_t timestampMs) {
    lastTs_ = timestampMs;
    Ipv4Header ip{};
    Ipv4Status s = parseIpv4(ipPkt, len, &ip);
    if (s != Ipv4Status::Ok) return s;  // MUT:==
    const uint8_t* transport = ipv4Payload(ipPkt, len);
    if (transport == nullptr) return Ipv4Status::Truncated;
    size_t transportLen = len - static_cast<size_t>(transport - ipPkt);
    FlowKey key;
    key.srcAddr = ip.srcAddr;
    key.dstAddr = ip.dstAddr;

    if (ip.protocol == 6) {  // TCP  // MUT:!=
        TcpHeader tcp{};
        if (parseTcp(transport, transportLen, &tcp) != TcpStatus::Ok) return Ipv4Status::Ok;
        key.srcPort = tcp.srcPort;
        key.dstPort = tcp.dstPort;
        size_t off = tcpPayloadOffset(tcp);
        const uint8_t* payload = (off < transportLen) ? transport + off : nullptr;
        size_t payloadLen = (off < transportLen) ? transportLen - off : 0;
        reassembly_.onSegment(key, tcp.seq, tcp.flags, payload, payloadLen);
        return Ipv4Status::Ok;
    }
    if (ip.protocol == 17) {  // UDP  // MUT:!=
        UdpHeader udp{};
        if (parseUdp(transport, transportLen, &udp) != UdpStatus::Ok) return Ipv4Status::Ok;
        const uint8_t* payload = transport + 8;
        size_t payloadLen = (transportLen > 8) ? transportLen - 8 : 0;
        if (udp.dstPort == 443 && payloadLen > 0) {  // MUT:!=
            QuicInfo qi{};
            if (detectQuic(payload, payloadLen, &qi) == QuicStatus::Ok) {
                EngineEvent ev;
                ev.kind = EngineEvent::Kind::QuicDetected;
                ev.flow.srcAddr = key.srcAddr;
                ev.flow.srcPort = udp.srcPort;
                ev.flow.dstAddr = key.dstAddr;
                ev.flow.dstPort = udp.dstPort;
                ev.timestampMs = timestampMs;
                ev.numeric = static_cast<int32_t>(qi.version);
                events_.push_back(ev);
            }
        }
        return Ipv4Status::Ok;
    }
    return Ipv4Status::Ok;
}

void Engine::onSegment(const FlowKey& flow, const uint8_t* payload, size_t len) {
    inspect(flow, payload, len, lastTs_);
}

void Engine::onReset(const FlowKey& flow) {
    EngineEvent ev;
    ev.kind = EngineEvent::Kind::TcpReset;
    ev.flow = flow;
    events_.push_back(ev);
    proto_.erase(flow);
}

void Engine::inspect(const FlowKey& flow, const uint8_t* data, size_t len, uint64_t ts) {
    ProtoState& ps = proto_[flow];
    if (len == 0) return;
    if (data[0] == 0x16 && len > 1 && data[1] == 0x03 && !ps.sniDone) {  // MUT:!=
        TlsSniResult res{};
        if (parseTlsClientHelloSni(data, len, &res) == SniStatus::Ok) {  // MUT:!=
            ps.sniDone = true;
            EngineEvent ev;
            ev.kind = EngineEvent::Kind::TlsSniDetected;
            ev.flow = flow;
            ev.timestampMs = ts;
            ev.text = res.sni;
            events_.push_back(ev);
        }
        return;
    }
    if (!ps.httpDone) {
        if (looksLikeHttpMethod(data, len)) {
            Http1Request req{};
            if (parseHttpRequest(data, len, &req) == Http1Status::Ok) {  // MUT:!=
                ps.httpDone = true;
                EngineEvent ev;
                ev.kind = EngineEvent::Kind::Http1RequestDetected;
                ev.flow = flow;
                ev.timestampMs = ts;
                ev.text = req.method + " " + req.target;
                ev.numeric = static_cast<int32_t>(req.contentLength);
                events_.push_back(ev);
            }
        } else if (startsWith(data, len, "HTTP/1.")) {
            Http1Response resp{};
            if (parseHttpResponse(data, len, &resp) == Http1Status::Ok) {
                ps.httpDone = true;
                EngineEvent ev;
                ev.kind = EngineEvent::Kind::Http1ResponseDetected;
                ev.flow = flow;
                ev.timestampMs = ts;
                ev.text = std::to_string(resp.status) + " " + resp.reason;
                ev.numeric = static_cast<int32_t>(resp.contentLength);
                events_.push_back(ev);
            }
        }
    }
}

}  // namespace traffic
