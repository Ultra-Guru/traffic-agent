#include "traffic/engine.h"
#include "traffic/export_lines.h"
#include "traffic/ws.h"

#include <cstring>

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

// Feeds a client->server payload into the engine through synthetic TCP/IP,
// advancing the sequence number; returns the next seq to use.
uint32_t feedC2S(Engine& e, const Bytes& payload, uint32_t baseSeq) {
    uint32_t seq = baseSeq;
    size_t off = 0;
    while (off < payload.size()) {
        size_t take = std::min<size_t>(1400, payload.size() - off);
        Bytes seg = tcpSegment(seq, 0x18, Bytes(payload.begin() + off, payload.begin() + off + take));
        putU16(seg, 0, 50000);
        putU16(seg, 2, 80);
        Bytes pkt = ipv4(seg);
        e.feedPacket(pkt.data(), pkt.size(), 1000);
        seq += static_cast<uint32_t>(take);
        off += take;
    }
    return seq;
}

uint32_t feedS2C(Engine& e, const Bytes& payload, uint32_t baseSeq) {
    uint32_t seq = baseSeq;
    size_t off = 0;
    while (off < payload.size()) {
        size_t take = std::min<size_t>(1400, payload.size() - off);
        Bytes seg = tcpSegment(seq, 0x18, Bytes(payload.begin() + off, payload.begin() + off + take));
        putU16(seg, 0, 80);
        putU16(seg, 2, 50000);
        Bytes pkt = ipv4(seg);
        std::swap(pkt[12], pkt[16]);
        std::swap(pkt[13], pkt[17]);
        std::swap(pkt[14], pkt[18]);
        std::swap(pkt[15], pkt[19]);
        e.feedPacket(pkt.data(), pkt.size(), 1000);
        seq += static_cast<uint32_t>(take);
        off += take;
    }
    return seq;
}

// A websocket session with per-direction sequence tracking.
struct WsSession {
    Engine e;
    uint32_t cSeq = 1000;
    uint32_t sSeq = 5000;

    void c2s(const Bytes& b) { cSeq = feedC2S(e, b, cSeq); }
    void s2c(const Bytes& b) { sSeq = feedS2C(e, b, sSeq); }
};

// A masked client text frame (RFC 6455: clients MUST mask).
Bytes maskedTextFrame(const std::string& text, uint8_t opcode = kWsText, bool fin = true) {
    Bytes f;
    f.push_back(static_cast<uint8_t>((fin ? 0x80 : 0x00) | opcode));
    const uint8_t mask[4] = {0x11, 0x22, 0x33, 0x44};
    if (text.size() < 126) {
        f.push_back(static_cast<uint8_t>(0x80 | text.size()));
    } else {
        f.push_back(static_cast<uint8_t>(0x80 | 126));
        f.push_back(static_cast<uint8_t>((text.size() >> 8) & 0xFF));
        f.push_back(static_cast<uint8_t>(text.size() & 0xFF));
    }
    f.insert(f.end(), mask, mask + 4);
    for (size_t i = 0; i < text.size(); ++i) {
        f.push_back(static_cast<uint8_t>(text[i]) ^ mask[i % 4]);
    }
    return f;
}

// An unmasked server frame (servers MUST NOT mask).
Bytes serverFrame(const Bytes& payload, uint8_t opcode = kWsText, bool fin = true) {
    Bytes f;
    f.push_back(static_cast<uint8_t>((fin ? 0x80 : 0x00) | opcode));
    if (payload.size() < 126) {
        f.push_back(static_cast<uint8_t>(payload.size()));
    } else {
        f.push_back(126);
        f.push_back(static_cast<uint8_t>((payload.size() >> 8) & 0xFF));
        f.push_back(static_cast<uint8_t>(payload.size() & 0xFF));
    }
    f.insert(f.end(), payload.begin(), payload.end());
    return f;
}

const char* kUpgradeReq =
    "GET /chat HTTP/1.1\r\n"
    "Host: ws.example.com\r\n"
    "Upgrade: websocket\r\n"
    "Connection: Upgrade\r\n"
    "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
    "Sec-WebSocket-Version: 13\r\n"
    "\r\n";

const char* kUpgradeResp =
    "HTTP/1.1 101 Switching Protocols\r\n"
    "Upgrade: websocket\r\n"
    "Connection: Upgrade\r\n"
    "Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n"
    "\r\n";

std::vector<const EngineEvent*> wsEvents(const Engine& e) {
    std::vector<const EngineEvent*> out;
    for (const auto& ev : e.events()) {
        if (ev.kind == EngineEvent::Kind::WsMessageDetected) out.push_back(&ev);
    }
    return out;
}

}  // namespace

TA_TEST(ws_tunnel_upgrade_then_frames_both_directions) {
    WsSession s;
    s.c2s(str(kUpgradeReq));
    s.s2c(str(kUpgradeResp));

    // The upgrade exchange itself is a normal 101 record.
    TA_CHECK_EQ(s.e.exchanges().size(), static_cast<size_t>(1));
    TA_CHECK_EQ(s.e.exchanges()[0].response.status, 101);
    TA_CHECK_EQ(wsEvents(s.e).size(), static_cast<size_t>(0));

    s.c2s(maskedTextFrame("hello server"));
    s.s2c(serverFrame(str("hi client")));

    auto evs = wsEvents(s.e);
    TA_CHECK_EQ(evs.size(), static_cast<size_t>(2));
    TA_CHECK_ST(evs[0]->text, "c>s TEXT 12B hello server");
    TA_CHECK_ST(evs[1]->text, "s>c TEXT 9B hi client");
}

TA_TEST(ws_tunnel_piggybacked_first_frame) {
    WsSession s;
    s.c2s(str(kUpgradeReq));
    // 101 head + first server frame in the SAME TCP segment.
    Bytes resp = str(kUpgradeResp);
    Bytes first = serverFrame(str("welcome"));
    resp.insert(resp.end(), first.begin(), first.end());
    s.s2c(resp);

    auto evs = wsEvents(s.e);
    TA_CHECK_EQ(evs.size(), static_cast<size_t>(1));
    TA_CHECK_ST(evs[0]->text, "s>c TEXT 7B welcome");
}

TA_TEST(ws_tunnel_close_code_and_ping_pong) {
    WsSession s;
    s.c2s(str(kUpgradeReq));
    s.s2c(str(kUpgradeResp));

    s.s2c(serverFrame(str("ping!"), kWsPing));
    s.c2s(maskedTextFrame("pong!", kWsPong));
    // Close frame: 2-byte status 1000 (normal closure), from the client.
    s.c2s(maskedTextFrame(std::string("\x03\xE8", 2), kWsClose));

    auto evs = wsEvents(s.e);
    TA_CHECK_EQ(evs.size(), static_cast<size_t>(3));
    TA_CHECK_ST(evs[0]->text, "s>c PING 5B ping!");
    TA_CHECK_ST(evs[1]->text, "c>s PONG 5B pong!");
    TA_CHECK_ST(evs[2]->text, "c>s CLOSE 2B 1000");
}

TA_TEST(ws_tunnel_fragmented_message_joins) {
    WsSession s;
    s.c2s(str(kUpgradeReq));
    s.s2c(str(kUpgradeResp));

    // Fragmented server text message: "hello " (no FIN) + "world" (FIN).
    s.s2c(serverFrame(str("hello "), kWsText, false));
    s.s2c(serverFrame(str("world"), kWsContinuation, true));

    auto evs = wsEvents(s.e);
    TA_CHECK_EQ(evs.size(), static_cast<size_t>(1));
    TA_CHECK_ST(evs[0]->text, "s>c TEXT 11B hello world");
}

TA_TEST(ws_tunnel_binary_preview_escapes_unprintable) {
    WsSession s;
    s.c2s(str(kUpgradeReq));
    s.s2c(str(kUpgradeResp));

    Bytes bin = {0x00, 0x01, 0x02, 'A', 0xFF, 'B'};
    s.s2c(serverFrame(bin, kWsBinary));

    auto evs = wsEvents(s.e);
    TA_CHECK_EQ(evs.size(), static_cast<size_t>(1));
    TA_CHECK_ST(evs[0]->text, "s>c BINARY 6B ...A.B");
    TA_CHECK_EQ(evs[0]->numeric, 6);
}

TA_TEST(ws_tunnel_uses_16bit_extended_length) {
    WsSession s;
    s.c2s(str(kUpgradeReq));
    s.s2c(str(kUpgradeResp));

    // 300-byte payload needs the 16-bit extended length form (126).
    std::string big(300, 'x');
    Bytes frame;
    frame.push_back(0x81);
    frame.push_back(126);
    frame.push_back(static_cast<uint8_t>((300 >> 8) & 0xFF));
    frame.push_back(static_cast<uint8_t>(300 & 0xFF));
    frame.insert(frame.end(), big.begin(), big.end());
    s.s2c(frame);

    auto evs = wsEvents(s.e);
    TA_CHECK_EQ(evs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(evs[0]->numeric, 300);
    // Preview is capped at 64 printable chars.
    TA_CHECK(evs[0]->text.find("300B") != std::string::npos);
    TA_CHECK(evs[0]->text.size() < 80);
}

TA_TEST(ws_event_line_renders_in_tsv) {
    EngineEvent ev;
    ev.kind = EngineEvent::Kind::WsMessageDetected;
    ev.timestampMs = 1234;
    ev.text = "c>s TEXT 5B hello";
    ev.numeric = 5;
    std::string line = engineEventToLine(ev);
    TA_CHECK(line.find("ws\t1234\t") == 0);
    TA_CHECK(line.find("c>s TEXT 5B hello\t5") != std::string::npos);
}
