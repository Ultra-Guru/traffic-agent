#include "traffic/export_lines.h"

#include <cstdio>

namespace traffic {

namespace {

// JSON string escaping for the SessionCodec subset: control characters and
// non-ASCII bytes are emitted as \u00XX so binary bodies survive the round
// trip through Kotlin's UTF-16 strings unharmed.
void appendJsonString(std::string* out, const std::string& s) {
    out->push_back('"');
    for (char c : s) {
        const uint8_t b = static_cast<uint8_t>(c);
        switch (c) {
            case '"': out->append("\\\""); break;
            case '\\': out->append("\\\\"); break;
            case '\n': out->append("\\n"); break;
            case '\r': out->append("\\r"); break;
            case '\t': out->append("\\t"); break;
            case '\b': out->append("\\b"); break;
            case '\f': out->append("\\f"); break;
            default:
                if (b < 0x20 || b > 0x7E) {  // MUT:<
                    char buf[8];
                    std::snprintf(buf, sizeof(buf), "\\u%04x", b);
                    out->append(buf);
                } else {
                    out->push_back(c);
                }
        }
    }
    out->push_back('"');
}

void appendIpPort(std::string* out, uint32_t addr, uint16_t port) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u.%u.%u.%u:%u", (addr >> 24) & 0xFFu,
                  (addr >> 16) & 0xFFu, (addr >> 8) & 0xFFu, addr & 0xFFu, port);
    out->append(buf);
}

const char* kindName(EngineEvent::Kind k) {
    switch (k) {
        case EngineEvent::Kind::TcpReset: return "rst";
        case EngineEvent::Kind::TlsSniDetected: return "sni";
        case EngineEvent::Kind::Http1RequestDetected: return "http1req";
        case EngineEvent::Kind::Http1ResponseDetected: return "http1resp";
        case EngineEvent::Kind::QuicDetected: return "quic";
        case EngineEvent::Kind::Http2HeadersDetected: return "h2";
        case EngineEvent::Kind::TlsJa3Detected: return "ja3";
        case EngineEvent::Kind::DnsMessageParsed: return "dns";
    }
    return "unknown";
}

// Header map rendering; duplicate names are repeated (later value wins on
// the Kotlin side, mirroring MutableHeaders.lowercased() semantics).
void appendHeaderObject(std::string* out, const Http1Headers& headers) {
    out->push_back('{');
    bool first = true;
    for (const auto& kv : headers.entries) {
        if (!first) out->push_back(',');
        first = false;
        appendJsonString(out, kv.first);
        out->push_back(':');
        appendJsonString(out, kv.second);
    }
    out->push_back('}');
}

// Bodies are byte vectors; escape through the same string path.
std::string bodyToString(const std::vector<uint8_t>& body) {
    return std::string(body.begin(), body.end());
}

}  // namespace

std::string engineEventToLine(const EngineEvent& ev) {
    std::string out;
    out.append(kindName(ev.kind));
    out.push_back('\t');
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%llu", static_cast<unsigned long long>(ev.timestampMs));
    out.append(buf);
    out.push_back('\t');
    appendIpPort(&out, ev.flow.srcAddr, ev.flow.srcPort);
    out.push_back('\t');
    appendIpPort(&out, ev.flow.dstAddr, ev.flow.dstPort);
    out.push_back('\t');
    out.append(ev.text);  // SNI / "GET /path" / DNS answers: no raw tabs
    out.push_back('\t');
    std::snprintf(buf, sizeof(buf), "%d", ev.numeric);
    out.append(buf);
    return out;
}

std::string exchangeToJsonLine(const HttpExchangeRecord& rec, uint64_t id) {
    std::string out = "{";
    char buf[32];

    out.append("\"id\":");
    std::snprintf(buf, sizeof(buf), "%llu", static_cast<unsigned long long>(id));
    out.append(buf);

    out.append(",\"ts\":");
    std::snprintf(buf, sizeof(buf), "%llu", static_cast<unsigned long long>(rec.timestampMs));
    out.append(buf);

    std::string host = rec.request.headers.get("Host");
    if (host.empty()) {
        // Fall back to the server address so the row stays identifiable.
        std::snprintf(buf, sizeof(buf), "%u.%u.%u.%u", (rec.flow.dstAddr >> 24) & 0xFFu,
                      (rec.flow.dstAddr >> 16) & 0xFFu, (rec.flow.dstAddr >> 8) & 0xFFu,
                      rec.flow.dstAddr & 0xFFu);
        host = buf;
    }
    out.append(",\"host\":");
    appendJsonString(&out, host);

    out.append(",\"path\":");
    appendJsonString(&out, rec.request.target);

    out.append(",\"method\":");
    appendJsonString(&out, rec.request.method);

    out.append(",\"status\":");
    if (rec.response.status == 0) {  // MUT:!=
        out.append("null");
    } else {
        std::snprintf(buf, sizeof(buf), "%d", rec.response.status);
        out.append(buf);
    }

    out.append(",\"reqHeaders\":");
    appendHeaderObject(&out, rec.request.headers);

    out.append(",\"respHeaders\":");
    appendHeaderObject(&out, rec.response.headers);

    out.append(",\"reqBody\":");
    appendJsonString(&out, bodyToString(rec.requestBody));

    // Prefer the decoded body (gzip/deflate) — that is what a human inspects.
    out.append(",\"respBody\":");
    if (!rec.responseDecoded.empty()) {
        appendJsonString(&out, bodyToString(rec.responseDecoded));
    } else {
        appendJsonString(&out, bodyToString(rec.responseBody));
    }

    out.append(",\"up\":");
    std::snprintf(buf, sizeof(buf), "%llu",
                  static_cast<unsigned long long>(rec.request.headerEnd +
                                                  rec.requestBody.size()));
    out.append(buf);

    out.append(",\"down\":");
    std::snprintf(buf, sizeof(buf), "%llu",
                  static_cast<unsigned long long>(rec.response.headerEnd +
                                                  rec.responseBody.size()));
    out.append(buf);

    out.append(",\"protocol\":\"HTTP1\",\"uid\":null}");
    return out;
}

}  // namespace traffic
