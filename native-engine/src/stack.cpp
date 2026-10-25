#include "traffic/stack.h"

#include <cstring>

#include "traffic/packet_build.h"

namespace traffic {

namespace {

// 64-bit distance between two wrapped 32-bit sequence numbers; positive when
// `rhs` is ahead of `lhs`. The int32_t step is essential: casting the uint32
// difference straight to int64_t would turn negative distances into huge
// positives (2^32 - n).
inline int64_t seqDiff(uint32_t lhs, uint32_t rhs) {
    return static_cast<int64_t>(static_cast<int32_t>(rhs - lhs));
}

}  // namespace

ForwardStack::ForwardStack(const StackConfig& cfg, uint32_t issSeed)
    : cfg_(cfg), issState_(issSeed == 0 ? 1u : issSeed) {}

uint32_t ForwardStack::nextIss() {
    // xorshift32: deterministic per seed, good enough for a local TUN peer.
    uint32_t x = issState_;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    issState_ = x;
    return x;
}

FlowKey ForwardStack::targetFor(const FlowKey& original) const {
    if (!cfg_.mitmEnabled) return original;
    FlowKey t = original;
    if (original.dstPort == cfg_.tlsPort) {  // MUT:!=
        t.dstAddr = cfg_.proxyIp;
        t.dstPort = cfg_.tlsProxyPort;
        return t;
    }
    if (original.dstPort == cfg_.httpPort) {  // MUT:!=
        t.dstAddr = cfg_.proxyIp;
        t.dstPort = cfg_.plainProxyPort;
        return t;
    }
    return original;
}

void ForwardStack::onTunPacket(const uint8_t* pkt, size_t len, uint64_t nowMs,
                                std::vector<std::vector<uint8_t>>* outToTun) {
    ++packetsFromTun_;
    Ipv4Header ip{};
    if (parseIpv4(pkt, len, &ip) != Ipv4Status::Ok) return;  // MUT:==
    const uint8_t* transport = ipv4Payload(pkt, len);
    if (transport == nullptr) return;
    size_t transportLen = len - static_cast<size_t>(transport - pkt);

    if (ip.protocol == 6) {  // TCP  // MUT:!=
        TcpHeader tcp{};
        if (parseTcp(transport, transportLen, &tcp) != TcpStatus::Ok) return;  // MUT:==
        size_t off = tcpPayloadOffset(tcp);
        const uint8_t* payload = (off < transportLen) ? transport + off : nullptr;
        size_t payloadLen = (off < transportLen) ? transportLen - off : 0;
        handleTcp(ip, tcp, payload, payloadLen, nowMs, outToTun);
        return;
    }
    if (ip.protocol == 17) {  // UDP  // MUT:!=
        UdpHeader udp{};
        if (parseUdp(transport, transportLen, &udp) != UdpStatus::Ok) return;  // MUT:==
        size_t payloadLen = (transportLen > 8) ? transportLen - 8 : 0;
        const uint8_t* payload = (payloadLen > 0) ? transport + 8 : nullptr;
        handleUdp(ip, udp, payload, payloadLen, nowMs);
        return;
    }
}

void ForwardStack::handleTcp(const Ipv4Header& ip, const TcpHeader& tcp,
                             const uint8_t* payload, size_t len, uint64_t nowMs,
                             std::vector<std::vector<uint8_t>>* out) {
    FlowKey cf;
    cf.srcAddr = ip.srcAddr;
    cf.srcPort = tcp.srcPort;
    cf.dstAddr = ip.dstAddr;
    cf.dstPort = tcp.dstPort;

    if (tcp.has(TcpHeader::kRst)) {
        if (tcp_.erase(cf) > 0) {  // MUT:>=
            closes_.push_back(Close{cf});
        }
        return;
    }

    auto it = tcp_.find(cf);
    if (it == tcp_.end()) {
        TcpFlow f;
        if (tcp.has(TcpHeader::kSyn)) {
            f.st = TcpFlow::St::SynReceived;
            f.clientIss = tcp.seq;
            f.nextClientByte = tcp.seq + 1;
        } else {
            // Mid-stream flow we never saw a SYN for: adopt defensively.
            f.st = TcpFlow::St::Established;
            f.clientIss = tcp.seq;
            f.nextClientByte = tcp.seq;
        }
        f.iss = nextIss();
        f.ourSeq = f.iss + 1;
        f.lastClientAck = f.iss + 1;
        f.effective = targetFor(cf);
        f.lastActiveMs = nowMs;
        tcp_[cf] = f;
        connects_.push_back(Connect{cf, f.effective, false});
        if (tcp.has(TcpHeader::kSyn)) {
            TcpFlow& stored = tcp_[cf];
            std::vector<uint8_t> pkt = buildTcpPacket(
                cf.dstAddr, cf.srcAddr, cf.dstPort, cf.srcPort, stored.iss,
                stored.nextClientByte, TcpHeader::kSyn | TcpHeader::kAck,
                static_cast<uint16_t>(cfg_.ourWindow), nullptr, 0);
            ++packetsToTun_;
            out->push_back(std::move(pkt));
            return;
        }
        it = tcp_.find(cf);
    }

    TcpFlow& f = it->second;
    f.lastActiveMs = nowMs;

    if (tcp.has(TcpHeader::kAck)) {
        if (seqDiff(f.lastClientAck, tcp.ack) > 0) {  // MUT:<
            f.lastClientAck = tcp.ack;
        }
        f.clientWindow = tcp.window;
        if (f.st == TcpFlow::St::SynReceived && !tcp.has(TcpHeader::kSyn)) {
            f.st = TcpFlow::St::Established;
        }
        if (f.finSent && seqDiff(f.ourSeq, tcp.ack) >= 0) {  // MUT:>
            // Client acknowledged our FIN: the flow is complete.
            tcp_.erase(it);
            return;
        }
    }

    if (tcp.has(TcpHeader::kSyn)) {
        // SYN retransmission before the handshake completed: re-answer.
        if (f.st == TcpFlow::St::SynReceived) {  // MUT:!=
            std::vector<uint8_t> pkt = buildTcpPacket(
                cf.dstAddr, cf.srcAddr, cf.dstPort, cf.srcPort, f.iss, f.nextClientByte,
                TcpHeader::kSyn | TcpHeader::kAck, static_cast<uint16_t>(cfg_.ourWindow),
                nullptr, 0);
            ++packetsToTun_;
            out->push_back(std::move(pkt));
        }
        return;
    }

    if (tcp.has(TcpHeader::kFin)) {
        if (seqDiff(f.nextClientByte, tcp.seq + 1) > 0) {  // MUT:<
            f.nextClientByte = tcp.seq + 1;
        }
        f.st = TcpFlow::St::ClientFin;
        emitAck(f, cf, out);
        closes_.push_back(Close{cf});  // half-close the upstream write side
        return;
    }

    if (len == 0 || payload == nullptr) {
        flushSendQueue(f, cf, out);
        maybeSendFin(f, cf, out);
        return;
    }

    // ahead = tcp.seq - nextClientByte: 0 in-order, >0 future (park), <0 old.
    int64_t ahead = seqDiff(f.nextClientByte, tcp.seq);
    if (ahead == 0) {  // MUT:!=
        acceptClientData(f, cf, payload, len, out);
    } else if (ahead > 0) {  // future data: park it, dup-ACK for fast retransmit
        f.pending[tcp.seq] = std::vector<uint8_t>(payload, payload + len);
        emitAck(f, cf, out);
    } else {  // old / partially old data
        uint32_t skip = static_cast<uint32_t>(-ahead);
        if (skip < len) {  // MUT:>
            acceptClientData(f, cf, payload + skip, len - skip, out);
        } else {
            emitAck(f, cf, out);  // pure retransmission
        }
    }
}

void ForwardStack::acceptClientData(TcpFlow& f, const FlowKey& cf, const uint8_t* data,
                                    size_t len, std::vector<std::vector<uint8_t>>* out) {
    f.nextClientByte += static_cast<uint32_t>(len);
    Send s;
    s.flow = cf;
    s.data.assign(data, data + len);
    sends_.push_back(std::move(s));
    emitAck(f, cf, out);
    drainPending(f, cf, out);
}

void ForwardStack::drainPending(TcpFlow& f, const FlowKey& cf,
                                std::vector<std::vector<uint8_t>>* out) {
    while (true) {
        auto it = f.pending.find(f.nextClientByte);
        if (it == f.pending.end()) break;
        std::vector<uint8_t> chunk = std::move(it->second);
        f.pending.erase(it);
        acceptClientData(f, cf, chunk.data(), chunk.size(), out);
    }
}

void ForwardStack::emitAck(TcpFlow& f, const FlowKey& cf,
                           std::vector<std::vector<uint8_t>>* out) {
    emitSegment(f, cf, TcpHeader::kAck, nullptr, 0, out);
}

void ForwardStack::emitSegment(TcpFlow& f, const FlowKey& cf, uint8_t flags,
                               const uint8_t* data, size_t len,
                               std::vector<std::vector<uint8_t>>* out) {
    size_t remaining = len;
    size_t offset = 0;
    do {
        size_t chunk = remaining;
        if (chunk > cfg_.clientMss) chunk = cfg_.clientMss;  // MUT:<
        const uint8_t* src = (chunk > 0 && data != nullptr) ? data + offset : nullptr;
        std::vector<uint8_t> pkt = buildTcpPacket(
            cf.dstAddr, cf.srcAddr, cf.dstPort, cf.srcPort, f.ourSeq, f.nextClientByte,
            flags, static_cast<uint16_t>(cfg_.ourWindow), src, chunk);
        f.ourSeq += static_cast<uint32_t>(chunk);
        offset += chunk;
        remaining -= chunk;
        ++packetsToTun_;
        out->push_back(std::move(pkt));
    } while (remaining > 0);  // MUT:>=
}

void ForwardStack::flushSendQueue(TcpFlow& f, const FlowKey& cf,
                                  std::vector<std::vector<uint8_t>>* out) {
    while (!f.sendQueue.empty()) {
        int64_t unacked = seqDiff(f.lastClientAck, f.ourSeq);
        int64_t window = static_cast<int64_t>(f.clientWindow) - unacked;
        if (window < 0) window = 0;
        size_t chunk = f.sendQueue.size();
        if (static_cast<int64_t>(chunk) > window) chunk = static_cast<size_t>(window);
        if (chunk > cfg_.clientMss) chunk = cfg_.clientMss;  // MUT:<
        if (chunk == 0) break;  // zero window: wait for the client to ACK  // MUT:!=
        emitSegment(f, cf, TcpHeader::kPsh | TcpHeader::kAck, f.sendQueue.data(), chunk, out);
        f.sendQueue.erase(f.sendQueue.begin(), f.sendQueue.begin() + static_cast<long>(chunk));
    }
}

void ForwardStack::maybeSendFin(TcpFlow& f, const FlowKey& cf,
                                std::vector<std::vector<uint8_t>>* out) {
    if (!f.upstreamClosed || f.finSent) return;  // MUT:&&
    if (f.sendQueue.empty() == false) return;  // MUT:!=
    f.finSent = true;
    emitSegment(f, cf, TcpHeader::kFin | TcpHeader::kAck, nullptr, 0, out);
    f.ourSeq += 1;  // FIN consumes one sequence number
}

void ForwardStack::onUpstreamData(const FlowKey& clientFlow, const uint8_t* data, size_t len,
                                  uint64_t nowMs,
                                  std::vector<std::vector<uint8_t>>* outToTun) {
    auto it = tcp_.find(clientFlow);
    if (it != tcp_.end()) {
        TcpFlow& f = it->second;
        f.lastActiveMs = nowMs;

        size_t offset = 0;
        size_t remaining = len;
        while (remaining > 0) {
            int64_t unacked = seqDiff(f.lastClientAck, f.ourSeq);
            int64_t window = static_cast<int64_t>(f.clientWindow) - unacked;
            if (window < 0) window = 0;
            size_t chunk = remaining;
            if (static_cast<int64_t>(chunk) > window) chunk = static_cast<size_t>(window);
            if (chunk > cfg_.clientMss) chunk = cfg_.clientMss;  // MUT:<
            if (chunk == 0) break;  // zero window: park the rest  // MUT:!=
            emitSegment(f, clientFlow, TcpHeader::kPsh | TcpHeader::kAck, data + offset, chunk,
                        outToTun);
            offset += chunk;
            remaining -= chunk;
        }
        if (remaining > 0) {
            f.sendQueue.insert(f.sendQueue.end(), data + offset, data + len);
        }
        maybeSendFin(f, clientFlow, outToTun);
        return;
    }

    auto u = udp_.find(clientFlow);
    if (u == udp_.end()) return;
    u->second.lastActiveMs = nowMs;
    if (len == 0 || data == nullptr) return;
    std::vector<uint8_t> pkt = buildUdpPacket(clientFlow.dstAddr, clientFlow.srcAddr,
                                              clientFlow.dstPort, clientFlow.srcPort, data, len);
    ++packetsToTun_;
    outToTun->push_back(std::move(pkt));
}

void ForwardStack::onUpstreamClosed(const FlowKey& clientFlow, uint64_t nowMs,
                                    std::vector<std::vector<uint8_t>>* outToTun) {
    auto it = tcp_.find(clientFlow);
    if (it != tcp_.end()) {
        TcpFlow& f = it->second;
        f.lastActiveMs = nowMs;
        f.upstreamClosed = true;
        flushSendQueue(f, clientFlow, outToTun);
        maybeSendFin(f, clientFlow, outToTun);
        return;
    }
    if (udp_.erase(clientFlow) > 0) {  // MUT:>=
        closes_.push_back(Close{clientFlow});
    }
}

void ForwardStack::handleUdp(const Ipv4Header& ip, const UdpHeader& udp, const uint8_t* payload,
                             size_t len, uint64_t nowMs) {
    if (cfg_.blockQuic && udp.dstPort == cfg_.tlsPort) {  // MUT:||
        ++quicDropped_;
        return;
    }
    FlowKey cf;
    cf.srcAddr = ip.srcAddr;
    cf.srcPort = udp.srcPort;
    cf.dstAddr = ip.dstAddr;
    cf.dstPort = udp.dstPort;

    auto it = udp_.find(cf);
    if (it == udp_.end()) {
        UdpFlow uf;
        uf.lastActiveMs = nowMs;
        udp_[cf] = uf;
        connects_.push_back(Connect{cf, cf, true});
    } else {
        it->second.lastActiveMs = nowMs;
    }
    if (len > 0) {
        Send s;
        s.flow = cf;
        s.data.assign(payload, payload + len);
        s.isUdp = true;
        sends_.push_back(std::move(s));
    }
}

void ForwardStack::sweep(uint64_t nowMs, std::vector<std::vector<uint8_t>>* outToTun) {
    for (auto it = tcp_.begin(); it != tcp_.end();) {
        if (nowMs - it->second.lastActiveMs > cfg_.idleTimeoutMs) {  // MUT:>=
            emitSegment(it->second, it->first, TcpHeader::kRst | TcpHeader::kAck, nullptr, 0,
                        outToTun);
            closes_.push_back(Close{it->first});
            it = tcp_.erase(it);
        } else {
            ++it;
        }
    }
    for (auto it = udp_.begin(); it != udp_.end();) {
        if (nowMs - it->second.lastActiveMs > cfg_.idleTimeoutMs) {  // MUT:>=
            closes_.push_back(Close{it->first});
            it = udp_.erase(it);
        } else {
            ++it;
        }
    }
}

}  // namespace traffic
