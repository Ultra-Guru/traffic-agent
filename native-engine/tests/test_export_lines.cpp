// export_lines tests: EngineEvent pipe-lines and HttpExchangeRecord JSONL
// must match the SessionCodec wire format consumed by core-capture.

#include "traffic/export_lines.h"

#include <cstring>
#include <string>
#include <vector>

#include "test_framework.hpp"

namespace {

traffic::EngineEvent makeEvent(traffic::EngineEvent::Kind kind, uint32_t srcAddr,
                               uint16_t srcPort, uint32_t dstAddr, uint16_t dstPort,
                               uint64_t ts, const std::string& text, int32_t numeric) {
    traffic::EngineEvent ev;
    ev.kind = kind;
    ev.flow.srcAddr = srcAddr;
    ev.flow.srcPort = srcPort;
    ev.flow.dstAddr = dstAddr;
    ev.flow.dstPort = dstPort;
    ev.timestampMs = ts;
    ev.text = text;
    ev.numeric = numeric;
    return ev;
}

TA_TEST(event_line_sni) {
    auto ev = makeEvent(traffic::EngineEvent::Kind::TlsSniDetected, 0x0A0B0C0Du, 44444,
                        0x01020304u, 443, 1700000000123ull, "api.example.com", 0);
    const std::string line = traffic::engineEventToLine(ev);
    TA_CHECK(line == "sni\t1700000000123\t10.11.12.13:44444\t1.2.3.4:443\tapi.example.com\t0");
}

TA_TEST(event_line_ja3_and_dns) {
    auto ja3 = makeEvent(traffic::EngineEvent::Kind::TlsJa3Detected, 0x0A0B0C0Du, 51515,
                         0x01020304u, 443, 42, "api.example.com|21d2e3024b63e0bac86dd07f7fb8c2bf",
                         0);
    TA_CHECK(traffic::engineEventToLine(ja3).find("ja3\t42\t") == 0);
    TA_CHECK(traffic::engineEventToLine(ja3).find("21d2e3024b63e0bac86dd07f7fb8c2bf") !=
             std::string::npos);

    auto dns = makeEvent(traffic::EngineEvent::Kind::DnsMessageParsed, 0x0A0B0C0Du, 53,
                         0x0A0B0C0Du, 55555, 7, "example.com A 93.184.216.34", 1);
    const std::string line = traffic::engineEventToLine(dns);
    TA_CHECK(line.find("dns\t7\t") == 0);
    TA_CHECK(line.find("example.com A 93.184.216.34\t1") != std::string::npos);
}

TA_TEST(event_line_kinds_covered) {
    struct Row {
        traffic::EngineEvent::Kind kind;
        const char* name;
    };
    const Row rows[] = {
        {traffic::EngineEvent::Kind::TcpReset, "rst"},
        {traffic::EngineEvent::Kind::TlsSniDetected, "sni"},
        {traffic::EngineEvent::Kind::Http1RequestDetected, "http1req"},
        {traffic::EngineEvent::Kind::Http1ResponseDetected, "http1resp"},
        {traffic::EngineEvent::Kind::QuicDetected, "quic"},
        {traffic::EngineEvent::Kind::Http2HeadersDetected, "h2"},
        {traffic::EngineEvent::Kind::TlsJa3Detected, "ja3"},
        {traffic::EngineEvent::Kind::DnsMessageParsed, "dns"},
    };
    for (const auto& r : rows) {
        auto ev = makeEvent(r.kind, 0, 0, 0, 0, 0, "", 0);
        const std::string line = traffic::engineEventToLine(ev);
        TA_CHECK(line.compare(0, std::strlen(r.name), r.name) == 0);
        // Always six tab-separated fields.
        size_t tabs = 0;
        for (char c : line) tabs += (c == '\t') ? 1 : 0;
        TA_CHECK_EQ(tabs, 5u);
    }
}

TA_TEST(exchange_json_minimal_fields) {
    traffic::HttpExchangeRecord rec;
    rec.flow.srcAddr = 0x0A0B0C0Du;
    rec.flow.srcPort = 44444;
    rec.flow.dstAddr = 0x5B060606u;  // 91.6.6.6
    rec.flow.dstPort = 80;
    rec.timestampMs = 1700000000999ull;
    rec.request.method = "GET";
    rec.request.target = "/repos?x=1";
    rec.request.version = "HTTP/1.1";
    rec.request.headers.entries.push_back({"Host", "api.example.com"});
    rec.request.headerEnd = 96;
    rec.response.version = "HTTP/1.1";
    rec.response.status = 200;
    rec.response.reason = "OK";
    rec.response.headers.entries.push_back({"Content-Type", "application/json"});
    rec.response.headerEnd = 128;
    rec.responseBody = {'{', '}', '\n'};
    rec.responseMime = "application/json";

    const std::string json = traffic::exchangeToJsonLine(rec, 7);
    TA_CHECK(json.find("\"id\":7") != std::string::npos);
    TA_CHECK(json.find("\"ts\":1700000000999") != std::string::npos);
    TA_CHECK(json.find("\"host\":\"api.example.com\"") != std::string::npos);
    TA_CHECK(json.find("\"path\":\"/repos?x=1\"") != std::string::npos);
    TA_CHECK(json.find("\"method\":\"GET\"") != std::string::npos);
    TA_CHECK(json.find("\"status\":200") != std::string::npos);
    TA_CHECK(json.find("\"reqHeaders\":{\"Host\":\"api.example.com\"}") != std::string::npos);
    TA_CHECK(json.find("\"respHeaders\":{\"Content-Type\":\"application/json\"}") !=
             std::string::npos);
    // Trailing \n in the body must be escaped, not literal.
    TA_CHECK(json.find("\"respBody\":\"{}\\n\"") != std::string::npos);
    TA_CHECK(json.find("\"up\":96") != std::string::npos);
    TA_CHECK(json.find("\"down\":131") != std::string::npos);  // 128 + 3 body
    TA_CHECK(json.find("\"protocol\":\"HTTP1\"") != std::string::npos);
    TA_CHECK(json.find("\"uid\":null") != std::string::npos);
}

TA_TEST(exchange_json_missing_host_falls_back_to_dst_ip) {
    traffic::HttpExchangeRecord rec;
    rec.flow.dstAddr = 0x5B060606u;  // 91.6.6.6
    rec.request.method = "POST";
    rec.request.target = "/t";
    rec.response.status = 0;  // no response seen yet
    const std::string json = traffic::exchangeToJsonLine(rec, 1);
    TA_CHECK(json.find("\"host\":\"91.6.6.6\"") != std::string::npos);
    TA_CHECK(json.find("\"status\":null") != std::string::npos);
}

TA_TEST(exchange_json_escapes_binary_body) {
    traffic::HttpExchangeRecord rec;
    rec.request.method = "GET";
    rec.request.target = "/bin";
    rec.request.headers.entries.push_back({"Host", "h"});
    rec.responseBody = {0x00, 0x01, 0x7F, 0x80, 0xFF, '"', '\\'};
    const std::string json = traffic::exchangeToJsonLine(rec, 2);
    TA_CHECK(json.find("\\u0000\\u0001\\u007f\\u0080\\u00ff\\\"\\\\") != std::string::npos);
}

TA_TEST(exchange_json_prefers_decoded_response_body) {
    traffic::HttpExchangeRecord rec;
    rec.request.method = "GET";
    rec.request.target = "/";
    rec.request.headers.entries.push_back({"Host", "h"});
    rec.responseBody = {0x1F, 0x8B};              // gzip magic, opaque
    rec.responseDecoded = {'o', 'k'};             // decoded wins
    const std::string json = traffic::exchangeToJsonLine(rec, 3);
    TA_CHECK(json.find("\"respBody\":\"ok\"") != std::string::npos);
    TA_CHECK(json.find("\\u001f") == std::string::npos);
}

}  // namespace
