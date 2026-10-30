#include "traffic/engine.h"
#include "traffic/export_lines.h"
#include "traffic/http2.h"
#include "traffic/http2flow.h"

#include <cstring>

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

// Feeds a client->server payload into the engine through synthetic TCP/IP.
void feedC2S(Engine& e, const Bytes& payload, uint32_t baseSeq = 1000) {
    uint32_t seq = baseSeq;
    size_t off = 0;
    while (off < payload.size()) {
        size_t take = std::min<size_t>(1400, payload.size() - off);
        Bytes seg = tcpSegment(seq, 0x18, Bytes(payload.begin() + off, payload.begin() + off + take));
        // rewrite ports: c2s 50000 -> 443
        putU16(seg, 0, 50000);
        putU16(seg, 2, 443);
        Bytes pkt = ipv4(seg);
        e.feedPacket(pkt.data(), pkt.size(), 1000);
        seq += static_cast<uint32_t>(take);
        off += take;
    }
}

void feedS2C(Engine& e, const Bytes& payload, uint32_t baseSeq = 5000) {
    // Reverse of builders' ipv4(): src 142.250.10.20:443 -> dst 192.168.1.10:50000.
    uint32_t seq = baseSeq;
    size_t off = 0;
    while (off < payload.size()) {
        size_t take = std::min<size_t>(1400, payload.size() - off);
        Bytes seg = tcpSegment(seq, 0x18, Bytes(payload.begin() + off, payload.begin() + off + take));
        putU16(seg, 0, 443);
        putU16(seg, 2, 50000);
        Bytes pkt = ipv4(seg);
        // swap addresses so the flow is server -> client
        std::swap(pkt[12], pkt[16]);
        std::swap(pkt[13], pkt[17]);
        std::swap(pkt[14], pkt[18]);
        std::swap(pkt[15], pkt[19]);
        e.feedPacket(pkt.data(), pkt.size(), 1000);
        seq += static_cast<uint32_t>(take);
        off += take;
    }
}

const std::string* findHeader(const std::vector<HpackHeader>& headers, const std::string& name) {
    for (const auto& h : headers) {
        if (h.name == name) return &h.value;
    }
    return nullptr;
}

}  // namespace

TA_TEST(h2flow_assembles_request_response_pair) {
    H2StreamTracker t;
    // Client HEADERS: :method GET, :path /a, :authority example.com (plain literals)
    Bytes block = encodeHpack({{":method", "GET"},
                               {":path", "/a"},
                               {":authority", "example.com"},
                               {"user-agent", "ta-test"}});
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, block.data(),
              block.size());
    // Server HEADERS: :status 200, content-type text/plain
    Bytes rblock = encodeHpack({{":status", "200"}, {"content-type", "text/plain"}});
    t.onFrame(false, kH2Headers, kH2FlagEndHeaders, 1, rblock.data(), rblock.size());
    TA_CHECK_EQ(t.openStreams(), static_cast<size_t>(1));
    // Server DATA + END_STREAM
    Bytes body = str("hello");
    t.onFrame(false, kH2Data, kH2FlagEndStream, 1, body.data(), body.size());

    auto completed = t.takeCompleted();
    TA_CHECK_EQ(completed.size(), static_cast<size_t>(1));
    const H2StreamRecord& rec = completed[0];
    TA_CHECK_EQ(rec.streamId, 1u);
    TA_CHECK(rec.responseDone);
    TA_CHECK_ST(*findHeader(rec.request.headers, ":method"), "GET");
    TA_CHECK_ST(*findHeader(rec.request.headers, ":path"), "/a");
    TA_CHECK_ST(*findHeader(rec.response.headers, ":status"), "200");
    TA_CHECK_EQ(rec.response.data.size(), static_cast<size_t>(5));
    TA_CHECK(std::memcmp(rec.response.data.data(), "hello", 5) == 0);
    TA_CHECK(!rec.isGrpc);
    TA_CHECK_EQ(t.openStreams(), static_cast<size_t>(0));
}

TA_TEST(h2flow_stateful_hpack_across_blocks) {
    H2StreamTracker t;
    // Block 1 (stream 1): literal-with-incremental-indexing inserts
    // "x-custom: v1" into the dynamic table (first dynamic entry == index 62).
    Bytes b1;
    b1.push_back(0x40);  // literal with incremental indexing, new name
    b1.push_back(8);
    b1.insert(b1.end(), {'x', '-', 'c', 'u', 's', 't', 'o', 'm'});
    b1.push_back(2);
    b1.insert(b1.end(), {'v', '1'});
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, b1.data(), b1.size());

    // Block 2 (stream 3): indexed field 62 references the dynamic entry.
    Bytes b2;
    b2.push_back(0x80 | 62);  // indexed header field, index 62 (single byte, 62 < 127)
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 3, b2.data(), b2.size());

    auto blocks = t.takeDecodedHeaders();
    TA_CHECK_EQ(blocks.size(), static_cast<size_t>(2));
    TA_CHECK_ST(*findHeader(blocks[1].headers, "x-custom"), "v1");

    // Sanity: stateless decodeHpack cannot resolve index 62 on its own.
    std::vector<HpackHeader> solo;
    size_t consumed = 0;
    TA_CHECK(decodeHpack(b2.data(), b2.size(), &solo, &consumed) != HpackStatus::Ok);
}

TA_TEST(h2flow_strips_priority_and_padding) {
    H2StreamTracker t;
    // HEADERS with PRIORITY (5 bytes stream dependency) on stream 1.
    Bytes block = encodeHpack({{":method", "POST"}, {":path", "/upload"}});
    Bytes payload;
    payload.insert(payload.end(), {0x00, 0x00, 0x00, 0x01, 0x10});  // dep=1, weight=16
    payload.insert(payload.end(), block.begin(), block.end());
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagPriority, 1, payload.data(),
              payload.size());

    // DATA with 4 bytes of padding around "abcd": pad length byte + data + pad.
    Bytes data;
    data.push_back(4);
    data.insert(data.end(), {'a', 'b', 'c', 'd'});
    data.insert(data.end(), {0, 0, 0, 0});
    t.onFrame(true, kH2Data, kH2FlagPadded, 1, data.data(), data.size());

    auto blocks = t.takeDecodedHeaders();
    TA_CHECK_EQ(blocks.size(), static_cast<size_t>(1));
    TA_CHECK_ST(*findHeader(blocks[0].headers, ":path"), "/upload");

    // Stream not completed yet (no server END_STREAM).
    TA_CHECK_EQ(t.takeCompleted().size(), static_cast<size_t>(0));
    // Flush via RST_STREAM and inspect request data.
    Bytes rst(4, 0);
    t.onFrame(false, 0x3, 0, 1, rst.data(), rst.size());
    auto completed = t.takeCompleted();
    TA_CHECK_EQ(completed.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(completed[0].request.data.size(), static_cast<size_t>(4));
    TA_CHECK(std::memcmp(completed[0].request.data.data(), "abcd", 4) == 0);
}

TA_TEST(h2flow_grpc_stream_with_trailers) {
    H2StreamTracker t;
    Bytes reqBlock = encodeHpack({{":method", "POST"},
                                  {":path", "/helloworld.Greeter/SayHello"},
                                  {":authority", "grpc.example.com"},
                                  {"content-type", "application/grpc"}});
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders, 1, reqBlock.data(), reqBlock.size());

    Bytes respBlock = encodeHpack({{":status", "200"}, {"content-type", "application/grpc"}});
    t.onFrame(false, kH2Headers, kH2FlagEndHeaders, 1, respBlock.data(), respBlock.size());

    // Two gRPC messages: "hello" and "worl" + a truncated tail.
    Bytes msg1 = buildGrpcMessage(str("hello"));
    Bytes msg2 = buildGrpcMessage(str("world"));
    Bytes data;
    data.insert(data.end(), msg1.begin(), msg1.end());
    data.insert(data.end(), msg2.begin(), msg2.end());
    t.onFrame(false, kH2Data, 0, 1, data.data(), data.size());

    // Trailers: HEADERS with END_STREAM carrying grpc-status.
    Bytes trailerBlock = encodeHpack({{"grpc-status", "0"}, {"grpc-message", "ok"}});
    t.onFrame(false, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, trailerBlock.data(),
              trailerBlock.size());

    auto completed = t.takeCompleted();
    TA_CHECK_EQ(completed.size(), static_cast<size_t>(1));
    const H2StreamRecord& rec = completed[0];
    TA_CHECK(rec.isGrpc);
    TA_CHECK_EQ(rec.grpcMessages.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(rec.grpcMessages[0].length, 5u);
    TA_CHECK(std::memcmp(rec.grpcMessages[0].preview.data(), "hello", 5) == 0);
    TA_CHECK(!rec.grpcMessages[0].compressed);
    TA_CHECK_EQ(rec.grpcMessages[1].length, 5u);
    TA_CHECK_ST(rec.grpcStatus, "0");
    TA_CHECK(findHeader(rec.trailers, "grpc-status") != nullptr);
}

TA_TEST(h2flow_grpc_split_handles_incomplete_tail) {
    std::vector<GrpcMessage> msgs;
    Bytes data;
    Bytes full = buildGrpcMessage(str("abcdefg"));  // 7 + 5 = 12 bytes
    data.insert(data.end(), full.begin(), full.begin() + 9);  // chop 3 bytes off
    splitGrpcMessages(data, &msgs);
    TA_CHECK_EQ(msgs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(msgs[0].length, 7u);
    TA_CHECK(msgs[0].truncated);
    TA_CHECK_EQ(msgs[0].preview.size(), static_cast<size_t>(4));  // 9 - 5 prefix

    // Empty and prefix-only inputs produce nothing.
    std::vector<GrpcMessage> none;
    splitGrpcMessages(Bytes(), &none);
    TA_CHECK_EQ(none.size(), static_cast<size_t>(0));
    splitGrpcMessages(Bytes{0x00, 0x00, 0x00}, &none);
    TA_CHECK_EQ(none.size(), static_cast<size_t>(0));
}

TA_TEST(h2flow_goaway_flushes_open_streams) {
    H2StreamTracker t;
    Bytes block = encodeHpack({{":method", "GET"}, {":path", "/a"}});
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, block.data(),
              block.size());
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 3, block.data(),
              block.size());
    TA_CHECK_EQ(t.openStreams(), static_cast<size_t>(2));

    Bytes goaway(8, 0);  // last-stream-id 0 + error code 0
    t.onFrame(false, kH2Goaway, 0, 0, goaway.data(), goaway.size());
    TA_CHECK_EQ(t.openStreams(), static_cast<size_t>(0));
    auto completed = t.takeCompleted();
    TA_CHECK_EQ(completed.size(), static_cast<size_t>(2));
    TA_CHECK(completed[0].responseDone);
    TA_CHECK(completed[1].responseDone);
}

TA_TEST(h2flow_data_cap_sets_truncated) {
    H2StreamTracker t;
    Bytes block = encodeHpack({{":method", "POST"}, {":path", "/big"}});
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders, 1, block.data(), block.size());
    t.onFrame(false, kH2Headers, kH2FlagEndHeaders, 1,
              encodeHpack({{":status", "200"}}).data(), 6);
    // 700 KiB x 2 = 1.4 MiB > 1 MiB cap.
    Bytes chunk(700 * 1024, 'x');
    t.onFrame(false, kH2Data, 0, 1, chunk.data(), chunk.size());
    t.onFrame(false, kH2Data, 0, 1, chunk.data(), chunk.size());
    Bytes fin;
    t.onFrame(false, kH2Data, kH2FlagEndStream, 1, fin.data(), 0);

    auto completed = t.takeCompleted();
    TA_CHECK_EQ(completed.size(), static_cast<size_t>(1));
    TA_CHECK(completed[0].response.truncated);
    TA_CHECK_EQ(completed[0].response.data.size(), H2StreamTracker::kMaxDataBytes);
}

TA_TEST(h2flow_continuation_frames_join) {
    H2StreamTracker t;
    Bytes block = encodeHpack({{":method", "GET"},
                               {":path", "/continuation"},
                               {"x-long-header", std::string(64, 'z')}});
    size_t split = 10;  // first fragment: 10 bytes, rest via CONTINUATION
    Bytes frag1(block.begin(), block.begin() + split);
    Bytes frag2(block.begin() + split, block.end());
    t.onFrame(true, kH2Headers, 0, 1, frag1.data(), frag1.size());
    TA_CHECK_EQ(t.takeDecodedHeaders().size(), static_cast<size_t>(0));
    t.onFrame(true, 0x9, kH2FlagEndHeaders, 1, frag2.data(), frag2.size());

    auto blocks = t.takeDecodedHeaders();
    TA_CHECK_EQ(blocks.size(), static_cast<size_t>(1));
    TA_CHECK_ST(*findHeader(blocks[0].headers, ":path"), "/continuation");
    TA_CHECK_EQ(blocks[0].headers.size(), static_cast<size_t>(3));
}

TA_TEST(h2flow_engine_end_to_end_produces_http2_exchange) {
    Engine e;
    Bytes pre = str("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n");
    Bytes settings = h2Frame(kH2Settings, 0, 0, {0x00, 0x03, 0x00, 0x00, 0x00, 0x10});

    Bytes reqBlock = encodeHpack({{":method", "POST"},
                                  {":path", "/v1/echo"},
                                  {":authority", "h2.example.com"},
                                  {"content-type", "application/grpc"}});
    Bytes reqHeaders = h2Frame(kH2Headers, kH2FlagEndHeaders, 1, reqBlock);
    Bytes grpcData = buildGrpcMessage(str("ping"));
    Bytes dataFrame = h2Frame(kH2Data, kH2FlagEndStream, 1, grpcData);

    Bytes client;
    client.insert(client.end(), pre.begin(), pre.end());
    client.insert(client.end(), settings.begin(), settings.end());
    client.insert(client.end(), reqHeaders.begin(), reqHeaders.end());
    client.insert(client.end(), dataFrame.begin(), dataFrame.end());
    feedC2S(e, client);

    Bytes respBlock = encodeHpack({{":status", "200"}, {"content-type", "application/grpc"}});
    Bytes respHeaders = h2Frame(kH2Headers, kH2FlagEndHeaders, 1, respBlock);
    Bytes respData = h2Frame(kH2Data, 0, 1, buildGrpcMessage(str("pong")));
    Bytes trailerBlock = encodeHpack({{"grpc-status", "0"}});
    Bytes trailers = h2Frame(kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, trailerBlock);
    Bytes server;
    server.insert(server.end(), settings.begin(), settings.end());
    server.insert(server.end(), respHeaders.begin(), respHeaders.end());
    server.insert(server.end(), respData.begin(), respData.end());
    server.insert(server.end(), trailers.begin(), trailers.end());
    feedS2C(e, server);

    TA_CHECK_EQ(e.exchanges().size(), static_cast<size_t>(1));
    const HttpExchangeRecord& rec = e.exchanges()[0];
    TA_CHECK_ST(rec.protocol, "HTTP2");
    TA_CHECK_ST(rec.request.method, "POST");
    TA_CHECK_ST(rec.request.target, "/v1/echo");
    TA_CHECK_ST(rec.request.headers.get("Host"), "h2.example.com");
    TA_CHECK_EQ(rec.response.status, 200);
    TA_CHECK_ST(rec.response.version, "HTTP/2");
    // grpc-status trailer landed in the response headers.
    TA_CHECK_ST(rec.response.headers.get("grpc-status"), "0");

    bool sawGrpcEvent = false;
    bool sawH2Event = false;
    for (const auto& ev : e.events()) {
        if (ev.kind == EngineEvent::Kind::GrpcMessageDetected) {
            sawGrpcEvent = true;
            TA_CHECK(ev.text.find("4B") != std::string::npos);
            TA_CHECK_EQ(ev.numeric, 1);
        }
        if (ev.kind == EngineEvent::Kind::Http2HeadersDetected) sawH2Event = true;
    }
    TA_CHECK(sawGrpcEvent);
    TA_CHECK(sawH2Event);
}

TA_TEST(h2flow_exchange_json_line_protocol_field) {
    H2StreamTracker t;
    Bytes block = encodeHpack({{":method", "GET"}, {":path", "/"}, {":authority", "x.y"}});
    t.onFrame(true, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, block.data(),
              block.size());
    Bytes rblock = encodeHpack({{":status", "204"}});
    t.onFrame(false, kH2Headers, kH2FlagEndHeaders | kH2FlagEndStream, 1, rblock.data(),
              rblock.size());
    auto completed = t.takeCompleted();
    TA_CHECK_EQ(completed.size(), static_cast<size_t>(1));

    Engine e;
    e.feedPacket(nullptr, 0, 0);  // no-op, just to touch the API
    // Build an exchange line via the record through the engine helper by
    // constructing the record through a full engine feed (simpler: reuse the
    // emit path indirectly is complex; test the JSON field directly).
    HttpExchangeRecord rec;
    rec.protocol = "HTTP2";
    std::string line = exchangeToJsonLine(rec, 7);
    TA_CHECK(line.find("\"protocol\":\"HTTP2\"") != std::string::npos);
    TA_CHECK(line.find("\"id\":7") != std::string::npos);

    HttpExchangeRecord h1rec;
    std::string h1line = exchangeToJsonLine(h1rec, 8);
    TA_CHECK(h1line.find("\"protocol\":\"HTTP1\"") != std::string::npos);
}
