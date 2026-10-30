#include "traffic/engine.h"

#include <cstdlib>
#include <cstring>

#include "traffic/body.h"
#include "traffic/dns.h"
#include "traffic/hpack.h"
#include "traffic/http2.h"
#include "traffic/quic.h"
#include "traffic/sni.h"
#include "traffic/tls.h"
#include "traffic/udp.h"

namespace traffic {

namespace {

const size_t kHelloBufCap = 8192;
const char kH2Preface[] = "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n";

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

FlowKey reverseOf(const FlowKey& k) {
    FlowKey r;
    r.srcAddr = k.dstAddr;
    r.srcPort = k.dstPort;
    r.dstAddr = k.srcAddr;
    r.dstPort = k.srcPort;
    return r;
}

// True when the probe could still grow into any of the recognized stream
// openers (method, "HTTP/1.", the h2 preface or a TLS record).
bool couldStillMatch(const uint8_t* p, size_t n) {
    if (n == 0) return true;
    static const char* kOpeners[] = {"GET ",     "POST ",  "HEAD ",  "PUT ",   "DELETE ",
                                     "OPTIONS ", "PATCH ", "TRACE ", "CONNECT", "HTTP/1.",
                                     kH2Preface};
    if (p[0] == 0x16 && n < 2) return true;  // TLS record version byte pending
    for (const char* o : kOpeners) {
        size_t m = std::strlen(o);
        if (m >= n && std::memcmp(p, o, n) == 0) return true;
    }
    return false;
}

std::string truncateText(std::string s, size_t maxLen) {
    if (s.size() > maxLen) s.resize(maxLen);
    return s;
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
        key.srcPort = udp.srcPort;
        key.dstPort = udp.dstPort;
        if (udp.dstPort == 443 && payloadLen > 0) {
            QuicInfo qi{};
            if (detectQuic(payload, payloadLen, &qi) == QuicStatus::Ok) {
                EngineEvent ev;
                ev.kind = EngineEvent::Kind::QuicDetected;
                ev.flow = key;
                ev.timestampMs = timestampMs;
                ev.numeric = static_cast<int32_t>(qi.version);
                events_.push_back(ev);
            }
        }
        if ((udp.srcPort == 53 || udp.dstPort == 53) && payloadLen >= 12) {  // MUT:&&
            handleDns(key, udp.srcPort, udp.dstPort, payload, payloadLen, timestampMs);
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
    auto it = convByFlow_.find(flow);
    if (it != convByFlow_.end()) {
        it->second->req.stop();
        it->second->resp.stop();
    }
}

Engine::Conversation* Engine::conversationFor(const FlowKey& flow) {
    auto it = convByFlow_.find(flow);
    if (it != convByFlow_.end()) return it->second.get();
    FlowKey rev = reverseOf(flow);
    it = convByFlow_.find(rev);
    if (it != convByFlow_.end()) return it->second.get();
    auto conv = std::make_shared<Conversation>();
    Conversation* raw = conv.get();
    convByFlow_[flow] = conv;
    convByFlow_[rev] = std::move(conv);
    return raw;
}

void Engine::classify(const FlowKey& flow, const uint8_t* data, size_t len, uint64_t ts) {
    Conversation& c = *conversationFor(flow);
    if (c.probeLen < sizeof(c.probe)) {  // MUT:>=
        size_t take = len;
        if (take > sizeof(c.probe) - c.probeLen) take = sizeof(c.probe) - c.probeLen;
        std::memcpy(c.probe + c.probeLen, data, take);
        c.probeLen += take;
    }
    const uint8_t* p = c.probe;
    size_t n = c.probeLen;

    // TLS record layer: ClientHello (or ServerHello) starts with 16 03 xx.
    if (n >= 2 && p[0] == 0x16 && p[1] == 0x03) {  // MUT:&&
        c.kind = Conversation::Kind::Tls;
        c.clientKnown = true;
        c.clientFlow = flow;
        feedTls(c, true, data, len, ts);
        return;
    }
    // HTTP/2 client preface ("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n").
    if (n >= 14 && startsWith(p, n, "PRI * HTTP/2.0")) {  // MUT:<
        c.kind = Conversation::Kind::H2;
        c.clientKnown = true;
        c.clientFlow = flow;
        c.h2PrefaceConsumed = 0;
        feedH2(c, true, data, len, ts);
        return;
    }
    if (looksLikeHttpMethod(p, n)) {
        c.kind = Conversation::Kind::Http;
        c.clientKnown = true;
        c.clientFlow = flow;
        feedHttp(c, true, data, len, ts);
        return;
    }
    if (n >= 7 && startsWith(p, n, "HTTP/1.")) {  // response direction first
        c.kind = Conversation::Kind::Http;
        c.clientKnown = true;
        c.clientFlow = reverseOf(flow);
        feedHttp(c, false, data, len, ts);
        return;
    }
    if (n < sizeof(c.probe) && couldStillMatch(p, n)) return;  // wait for more bytes
    c.kind = Conversation::Kind::Skip;
}

void Engine::inspect(const FlowKey& flow, const uint8_t* data, size_t len, uint64_t ts) {
    if (data == nullptr || len == 0) return;
    Conversation* c = conversationFor(flow);
    if (c == nullptr) return;
    if (c->kind == Conversation::Kind::Unknown) {
        classify(flow, data, len, ts);
        return;
    }
    switch (c->kind) {
        case Conversation::Kind::Tls:
            feedTls(*c, flow == c->clientFlow, data, len, ts);
            break;
        case Conversation::Kind::H2:
            feedH2(*c, flow == c->clientFlow, data, len, ts);
            break;
        case Conversation::Kind::Http:
            feedHttp(*c, flow == c->clientFlow, data, len, ts);
            break;
        case Conversation::Kind::Unknown:
        case Conversation::Kind::Skip:
            break;
    }
}

void Engine::feedTls(Conversation& c, bool clientSide, const uint8_t* data, size_t len,
                     uint64_t ts) {
    if (!clientSide) return;  // server side: certificates and friends, no MITM here
    if (c.sniDone && c.ja3Done) return;
    if (c.helloBuf.size() < kHelloBufCap) {
        size_t take = len;
        if (take > kHelloBufCap - c.helloBuf.size()) take = kHelloBufCap - c.helloBuf.size();
        c.helloBuf.insert(c.helloBuf.end(), data, data + take);
    }
    if (!c.sniDone) {
        TlsSniResult res{};
        if (parseTlsClientHelloSni(c.helloBuf.data(), c.helloBuf.size(), &res) == SniStatus::Ok) {
            c.sniDone = true;  // MUT:!
            EngineEvent ev;
            ev.kind = EngineEvent::Kind::TlsSniDetected;
            ev.flow = c.clientFlow;
            ev.timestampMs = ts;
            ev.text = res.sni;
            events_.push_back(std::move(ev));
        }
    }
    if (!c.ja3Done) {
        ClientHelloInfo chi{};
        if (parseTlsClientHello(c.helloBuf.data(), c.helloBuf.size(), &chi) == TlsStatus::Ok) {
            c.ja3Done = true;
            EngineEvent ev;
            ev.kind = EngineEvent::Kind::TlsJa3Detected;
            ev.flow = c.clientFlow;
            ev.timestampMs = ts;
            ev.text = chi.sni + "|" + chi.ja3Md5;
            events_.push_back(std::move(ev));
        }
    }
}

void Engine::feedHttp(Conversation& c, bool clientSide, const uint8_t* data, size_t len,
                      uint64_t ts) {
    (void)ts;
    if (c.ws.active) {
        // Past the 101 upgrade: every byte in both directions is a websocket
        // frame stream, not HTTP anymore.
        feedWs(c, clientSide, data, len, lastTs_);
        return;
    }
    if (clientSide) {
        c.req.feed(data, len, lastTs_);
        auto msgs = c.req.takeMessages();
        for (Http1Message& m : msgs) {
            EngineEvent ev;
            ev.kind = EngineEvent::Kind::Http1RequestDetected;
            ev.flow = c.clientFlow;
            ev.timestampMs = m.timestampMs;
            ev.text = m.request.method + " " + m.request.target;
            ev.numeric = static_cast<int32_t>(m.request.contentLength);
            events_.push_back(std::move(ev));
            if (m.request.method == "HEAD" || m.request.method == "CONNECT") {
                c.resp.setNextResponseBodiless();
            }
            c.pendingRequests.push_back(std::move(m));
        }
    } else {
        c.resp.feed(data, len, lastTs_);
        drainParserMessages(c, lastTs_);
    }
    if (c.resp.upgradeDetected() && !c.ws.active) {
        // 101 Switching Protocols: a websocket tunnel begins here. The server
        // often piggybacks the first frames on the very same TCP segment.
        c.req.stop();
        c.ws.active = true;
        std::vector<uint8_t> leftover = c.resp.takeUpgradeLeftover();
        if (!leftover.empty()) {
            feedWs(c, false, leftover.data(), leftover.size(), lastTs_);
        }
    }
}

// Websocket frame stream: reassemble complete messages per direction and
// surface each as a WsMessageDetected event (direction, opcode, size and a
// printable preview; close frames carry their status code).
void Engine::feedWs(Conversation& c, bool clientSide, const uint8_t* data, size_t len,
                    uint64_t ts) {
    WsMessageAssembler& assembler = clientSide ? c.ws.c2s : c.ws.s2c;
    assembler.feed(data, len);
    for (WsMessage& m : assembler.takeMessages()) {
        std::string text = clientSide ? "c>s " : "s>c ";
        text += wsOpcodeName(m.opcode);
        text += " " + std::to_string(m.payload.size()) + "B ";
        if (m.opcode == kWsClose && m.payload.size() >= 2) {
            uint16_t code = static_cast<uint16_t>((m.payload[0] << 8) | m.payload[1]);
            text += std::to_string(code);
        } else {
            size_t preview = m.payload.size() < 64 ? m.payload.size() : 64;
            for (size_t i = 0; i < preview; ++i) {
                uint8_t b = m.payload[i];
                text.push_back(b >= 0x20 && b < 0x7F ? static_cast<char>(b) : '.');
            }
        }
        EngineEvent ev;
        ev.kind = EngineEvent::Kind::WsMessageDetected;
        ev.flow = c.clientFlow;
        ev.timestampMs = ts;
        ev.text = truncateText(std::move(text), 96);
        ev.numeric = static_cast<int32_t>(m.payload.size() & 0x7FFFFFFFu);
        events_.push_back(std::move(ev));
    }
}

void Engine::drainParserMessages(Conversation& c, uint64_t ts) {
    (void)ts;
    auto msgs = c.resp.takeMessages();
    for (Http1Message& m : msgs) {
        EngineEvent ev;
        ev.kind = EngineEvent::Kind::Http1ResponseDetected;
        ev.flow = c.clientFlow;
        ev.timestampMs = m.timestampMs;
        ev.text = std::to_string(m.response.status) + " " + m.response.reason;
        ev.numeric = static_cast<int32_t>(m.response.contentLength);
        events_.push_back(std::move(ev));

        if (c.pendingRequests.empty()) continue;
        Http1Message reqM = std::move(c.pendingRequests.front());
        c.pendingRequests.erase(c.pendingRequests.begin());

        HttpExchangeRecord rec;
        rec.flow = c.clientFlow;
        rec.timestampMs = m.timestampMs;
        rec.request = reqM.request;
        rec.response = m.response;
        rec.requestBody = std::move(reqM.body);
        rec.responseBody = m.body;
        rec.truncated = reqM.truncated || m.truncated;
        std::string enc = m.response.headers.get("content-encoding");
        std::string ctype = m.response.headers.get("content-type");
        std::vector<uint8_t> decoded;
        if (decompressBody(m.body.data(), m.body.size(), enc, &decoded)) {
            rec.responseDecoded = std::move(decoded);
            rec.responseMime = sniffMime(rec.responseDecoded.data(),
                                        rec.responseDecoded.size(), ctype);
        } else {
            rec.responseMime = sniffMime(rec.responseBody.data(), rec.responseBody.size(), ctype);
        }
        exchanges_.push_back(std::move(rec));

        if (reqM.request.method == "CONNECT" && m.response.status / 100 == 2) {
            // CONNECT tunnel established: stop parsing both directions.
            c.req.stop();
            c.resp.stop();
        }
    }
    if (c.pendingRequests.size() > 64) {
        c.pendingRequests.erase(c.pendingRequests.begin(),
                                c.pendingRequests.begin() + 32);  // unbounded pairing guard
    }
}

void Engine::emitHttp2HeaderList(Conversation& c, uint32_t streamId,
                                 const std::vector<HpackHeader>& headers, uint64_t ts) {
    std::string text;
    for (const HpackHeader& h : headers) {
        if (text.size() >= 256) break;
        if (!text.empty()) text.push_back(' ');
        text += h.name + " " + h.value;
    }
    EngineEvent ev;
    ev.kind = EngineEvent::Kind::Http2HeadersDetected;
    ev.flow = c.clientFlow;
    ev.timestampMs = ts;
    ev.text = truncateText(std::move(text), 256);
    ev.numeric = static_cast<int32_t>(streamId);
    events_.push_back(std::move(ev));
}

void Engine::emitHttp2Headers(Conversation& c, uint32_t streamId, const uint8_t* block, size_t len,
                              uint64_t ts) {
    std::vector<HpackHeader> headers;
    size_t consumed = 0;
    if (decodeHpack(block, len, &headers, &consumed) != HpackStatus::Ok) return;
    emitHttp2HeaderList(c, streamId, headers, ts);
}

// Renders one assembled HTTP/2 stream as a classic HttpExchangeRecord so the
// whole HTTP/1 pipeline (exports, session list, MITM-less analysis) works for
// h2 traffic unchanged.
void Engine::emitH2Exchange(Conversation& c, const H2StreamRecord& rec, uint64_t ts) {
    HttpExchangeRecord out;
    out.flow = c.clientFlow;
    out.timestampMs = ts;
    out.protocol = "HTTP2";

    for (const HpackHeader& h : rec.request.headers) {
        if (h.name == ":method") {
            out.request.method = h.value;
        } else if (h.name == ":path") {
            out.request.target = h.value;
        } else if (h.name == ":authority") {
            out.request.headers.entries.emplace_back("Host", h.value);
        } else if (!h.name.empty() && h.name[0] != ':') {
            out.request.headers.entries.push_back({h.name, h.value});
        }
    }
    out.request.version = "HTTP/2";
    out.request.contentLength = rec.request.data.size();
    out.requestBody = rec.request.data;

    for (const HpackHeader& h : rec.response.headers) {
        if (h.name == ":status") {
            out.response.status = static_cast<int>(strtol(h.value.c_str(), nullptr, 10));
        } else if (!h.name.empty() && h.name[0] != ':') {
            out.response.headers.entries.push_back({h.name, h.value});
        }
    }
    for (const HpackHeader& h : rec.trailers) {
        out.response.headers.entries.push_back({h.name, h.value});
    }
    out.response.version = "HTTP/2";
    out.response.contentLength = rec.response.data.size();
    out.responseBody = rec.response.data;
    out.truncated = rec.request.truncated || rec.response.truncated;

    std::string enc = out.response.headers.get("content-encoding");
    std::string ctype = out.response.headers.get("content-type");
    std::vector<uint8_t> decoded;
    if (decompressBody(out.responseBody.data(), out.responseBody.size(), enc, &decoded)) {
        out.responseDecoded = std::move(decoded);
        out.responseMime =
            sniffMime(out.responseDecoded.data(), out.responseDecoded.size(), ctype);
    } else {
        out.responseMime = sniffMime(out.responseBody.data(), out.responseBody.size(), ctype);
    }
    exchanges_.push_back(std::move(out));

    if (rec.isGrpc) {
        int emitted = 0;
        for (const GrpcMessage& m : rec.grpcMessages) {
            if (emitted++ >= 16) break;
            std::string preview;
            for (uint8_t b : m.preview) {
                preview.push_back(b >= 0x20 && b < 0x7F ? static_cast<char>(b) : '.');
            }
            EngineEvent ev;
            ev.kind = EngineEvent::Kind::GrpcMessageDetected;
            ev.flow = c.clientFlow;
            ev.timestampMs = ts;
            ev.text = truncateText("grpc " + std::string(m.compressed ? "gz " : "") +
                                       std::to_string(m.length) + "B " + preview,
                                   128);
            ev.numeric = static_cast<int32_t>(rec.streamId);
            events_.push_back(std::move(ev));
        }
    }
}

void Engine::feedH2(Conversation& c, bool clientSide, const uint8_t* data, size_t len, uint64_t ts) {
    Conversation::H2Dir& d = c.h2[clientSide ? 0 : 1];
    if (clientSide) {
        // Strip the 24-byte connection preface before the first frame.
        size_t skip = 0;
        while (c.h2PrefaceConsumed < sizeof(kH2Preface) - 1 && skip < len) {
            if (data[skip] != static_cast<uint8_t>(kH2Preface[c.h2PrefaceConsumed])) {
                c.h2PrefaceConsumed = sizeof(kH2Preface) - 1;  // broken: stop looking  // MUT:!=
                break;
            }
            ++skip;
            ++c.h2PrefaceConsumed;
        }
        if (c.h2PrefaceConsumed < sizeof(kH2Preface) - 1) return;  // preface still incomplete
        data += skip;
        len -= skip;
    }
    if (len == 0) return;
    d.buf.insert(d.buf.end(), data, data + len);

    size_t pos = 0;
    while (pos + 9 <= d.buf.size()) {
        const uint8_t* b = d.buf.data() + pos;
        uint32_t flen = (static_cast<uint32_t>(b[0]) << 16) | (static_cast<uint32_t>(b[1]) << 8) |
                        b[2];
        uint8_t type = b[3];
        uint8_t flags = b[4];
        uint32_t sid = (static_cast<uint32_t>(b[5]) << 24) |
                       (static_cast<uint32_t>(b[6]) << 16) |
                       (static_cast<uint32_t>(b[7]) << 8) | b[8];
        sid &= 0x7FFFFFFFu;
        if (flen > (1u << 20)) {  // sanity cap: hostile or mid-stream garbage
            d.buf.clear();
            return;
        }
        if (pos + 9 + flen > d.buf.size()) break;  // incomplete frame
        const uint8_t* payload = b + 9;
        size_t payloadLen = flen;

        // Stream-level reassembly (HEADERS/CONTINUATION/DATA/RST/GOAWAY).
        c.h2Streams.onFrame(clientSide, type, flags, sid, payload, payloadLen);

        if (type == 0) {  // DATA: byte accounting
            size_t counted = payloadLen;
            if ((flags & kH2FlagPadded) != 0 && payloadLen > 0) {
                size_t pad = payload[0];
                counted = (payloadLen > pad + 1) ? payloadLen - pad - 1 : 0;
            }
            c.h2StreamBytes[sid] += counted;
        }
        // SETTINGS / WINDOW_UPDATE / PING / ...: skipped by length
        pos += 9 + flen;
    }
    if (pos > 0) {
        d.buf.erase(d.buf.begin(), d.buf.begin() + static_cast<std::ptrdiff_t>(pos));
    }

    // Header-block events (stateful HPACK results) keep the old text format.
    for (const auto& hb : c.h2Streams.takeDecodedHeaders()) {
        emitHttp2HeaderList(c, hb.streamId, hb.headers, ts);
    }
    // Completed streams become regular exchanges.
    for (const auto& rec : c.h2Streams.takeCompleted()) {
        emitH2Exchange(c, rec, ts);
    }
}

void Engine::handleDns(const FlowKey& flow, uint32_t srcPort, uint32_t dstPort,
                       const uint8_t* payload, size_t len, uint64_t ts) {
    (void)srcPort;
    (void)dstPort;
    DnsMessage dm{};
    if (parseDnsResponse(payload, len, &dm) != DnsStatus::Ok) return;
    if (dm.questions.empty()) return;
    const std::string& qname = dm.questions[0].name;
    bool isResponse = (dm.flags & 0x8000u) != 0;
    std::string text;
    if (!isResponse || dm.answers.empty()) {
        text = qname + "?";
    } else {
        text = qname + " " + dnsTypeMnemonic(dm.answers[0].type) + " " + dm.answers[0].rdataText;
        for (size_t i = 1; i < dm.answers.size() && i < 3; ++i) {
            const DnsAnswer& a = dm.answers[i];
            text += "; " + dnsTypeMnemonic(a.type) + " " + a.rdataText;
        }
    }
    EngineEvent ev;
    ev.kind = EngineEvent::Kind::DnsMessageParsed;
    ev.flow = flow;
    ev.timestampMs = ts;
    ev.text = truncateText(std::move(text), 256);
    events_.push_back(std::move(ev));
}

}  // namespace traffic
