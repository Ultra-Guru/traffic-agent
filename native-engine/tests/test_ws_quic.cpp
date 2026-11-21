#include "traffic/quic.h"
#include "traffic/ws.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(ws_parses_masked_text_frame) {
    // fin=1, opcode=text, mask=1, len=5, then mask key + payload
    Bytes b = {0x81, 0x85, 0x11, 0x22, 0x33, 0x44, 'h', 'e', 'l', 'l', 'o'};
    WsFrameInfo f{};
    TA_CHECK_EQ(parseWsFrame(b.data(), b.size(), &f), WsStatus::Ok);
    TA_CHECK(f.fin);
    TA_CHECK(f.masked);
    TA_CHECK_EQ(f.opcode, kWsText);
    TA_CHECK_EQ(f.payloadLength, static_cast<uint64_t>(5));
    TA_CHECK_EQ(f.headerLength, static_cast<size_t>(6));
    TA_CHECK_ST(wsOpcodeName(f.opcode), "TEXT");
}

TA_TEST(ws_parses_extended_length) {
    // len7=126 -> 16-bit extended length = 300
    Bytes b = {0x82, 0x7E, 0x01, 0x2C};
    b.insert(b.end(), 300, 0x00);
    WsFrameInfo f{};
    TA_CHECK_EQ(parseWsFrame(b.data(), b.size(), &f), WsStatus::Ok);
    TA_CHECK_EQ(f.opcode, kWsBinary);
    TA_CHECK_EQ(f.payloadLength, static_cast<uint64_t>(300));
    TA_CHECK_EQ(f.headerLength, static_cast<size_t>(4));
}

TA_TEST(ws_opcode_names) {
    TA_CHECK_ST(wsOpcodeName(kWsClose), "CLOSE");
    TA_CHECK_ST(wsOpcodeName(kWsPing), "PING");
    TA_CHECK_ST(wsOpcodeName(kWsPong), "PONG");
    TA_CHECK_ST(wsOpcodeName(kWsContinuation), "CONTINUATION");
    TA_CHECK_ST(wsOpcodeName(0x7), "UNKNOWN");
}

TA_TEST(ws_rejects_short) {
    Bytes b = {0x81};
    WsFrameInfo f{};
    TA_CHECK_EQ(parseWsFrame(b.data(), b.size(), &f), WsStatus::TooShort);
}

TA_TEST(ws_accepts_two_byte_frame) {
    // exactly 2 bytes: minimal header, zero-length text frame
    Bytes b = {0x81, 0x00};
    WsFrameInfo f{};
    TA_CHECK_EQ(parseWsFrame(b.data(), b.size(), &f), WsStatus::Ok);
    TA_CHECK(f.fin);
    TA_CHECK_EQ(f.opcode, kWsText);
    TA_CHECK_EQ(f.payloadLength, static_cast<uint64_t>(0));
    TA_CHECK_EQ(f.headerLength, static_cast<size_t>(2));
}

TA_TEST(ws_accepts_small_64bit_extended_length) {
    // len7=127 -> 64-bit length field holding a small value (5)
    Bytes b = {0x82, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 'h', 'e', 'l', 'l', 'o'};
    WsFrameInfo f{};
    TA_CHECK_EQ(parseWsFrame(b.data(), b.size(), &f), WsStatus::Ok);
    TA_CHECK_EQ(f.payloadLength, static_cast<uint64_t>(5));
    TA_CHECK_EQ(f.headerLength, static_cast<size_t>(10));
}

TA_TEST(quic_detects_long_header_v1) {
    Bytes b = {0xC0, 0x00, 0x00, 0x00, 0x01, 0x08};
    QuicInfo q{};
    TA_CHECK_EQ(detectQuic(b.data(), b.size(), &q), QuicStatus::Ok);
    TA_CHECK(q.longHeader);
    TA_CHECK_EQ(q.version, 1u);
    TA_CHECK(!q.versionNegotiation);
}

TA_TEST(quic_accepts_five_byte_minimum) {
    // exactly 5 bytes: long header byte + version
    Bytes b = {0xC0, 0x00, 0x00, 0x00, 0x01};
    QuicInfo q{};
    TA_CHECK_EQ(detectQuic(b.data(), b.size(), &q), QuicStatus::Ok);
    TA_CHECK(q.longHeader);
    TA_CHECK_EQ(q.version, 1u);
}

TA_TEST(quic_detects_version_negotiation) {
    Bytes b = {0xC0, 0x00, 0x00, 0x00, 0x00, 0x08};
    QuicInfo q{};
    TA_CHECK_EQ(detectQuic(b.data(), b.size(), &q), QuicStatus::Ok);
    TA_CHECK(q.versionNegotiation);
}

TA_TEST(quic_short_header_requires_fixed_bit) {
    Bytes ok = {0x40, 0x01, 0x02, 0x03, 0x04, 0x05};
    QuicInfo q{};
    TA_CHECK_EQ(detectQuic(ok.data(), ok.size(), &q), QuicStatus::Ok);
    TA_CHECK(!q.longHeader);

    Bytes bad = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05};  // fixed bit clear
    TA_CHECK_EQ(detectQuic(bad.data(), bad.size(), &q), QuicStatus::NotQuic);
}

TA_TEST(quic_rejects_short_input) {
    Bytes b = {0xC0, 0x00, 0x00, 0x00};
    QuicInfo q{};
    TA_CHECK_EQ(detectQuic(b.data(), b.size(), &q), QuicStatus::TooShort);
}

// ---------------- message assembler ----------------

namespace {

Bytes wsFrameBytes(bool fin, uint8_t opcode, const Bytes& payload, bool mask = false,
                   uint8_t maskKey = 0x00) {
    Bytes f;
    f.push_back(static_cast<uint8_t>((fin ? 0x80u : 0x00u) | opcode));
    f.push_back(static_cast<uint8_t>((mask ? 0x80u : 0x00u) | (payload.size() & 0x7Fu)));
    if (mask) {
        // 4 mask bytes: use the same key repeated for the test
        for (int i = 0; i < 4; ++i) f.push_back(maskKey);
        for (size_t i = 0; i < payload.size(); ++i) {
            f.push_back(static_cast<uint8_t>(payload[i] ^ maskKey));
        }
    } else {
        f.insert(f.end(), payload.begin(), payload.end());
    }
    return f;
}

}  // namespace

TA_TEST(ws_decode_unmasks_payload) {
    Bytes plain = {'H', 'e', 'l', 'l', 'o'};
    auto f = wsFrameBytes(true, kWsText, plain, true, 0x37);
    WsFrameInfo info{};
    std::vector<uint8_t> out;
    TA_CHECK_EQ(decodeWsFrame(f.data(), f.size(), &info, &out), WsStatus::Ok);
    TA_CHECK(info.masked);
    TA_CHECK(info.fin);
    TA_CHECK_EQ(info.opcode, kWsText);
    TA_CHECK(out == plain);
    TA_CHECK_ST(std::string(out.begin(), out.end()), "Hello");
}

TA_TEST(ws_decode_frame_split_across_feeds) {
    Bytes plain = {'a', 'b', 'c'};
    auto f = wsFrameBytes(true, kWsBinary, plain);
    std::vector<uint8_t> out;
    WsFrameInfo info{};
    TA_CHECK_EQ(decodeWsFrame(f.data(), 2, &info, &out), WsStatus::TooShort);
    TA_CHECK_EQ(decodeWsFrame(f.data(), f.size(), &info, &out), WsStatus::Ok);
    TA_CHECK(out == plain);
}

TA_TEST(ws_assembler_joins_fragments) {
    WsMessageAssembler asm1;
    auto f1 = wsFrameBytes(false, kWsText, {'H', 'e'});
    auto f2 = wsFrameBytes(true, kWsContinuation, {'l', 'l', 'o'});
    asm1.feed(f1.data(), f1.size());
    auto early = asm1.takeMessages();
    TA_CHECK_EQ(early.size(), static_cast<size_t>(0));
    asm1.feed(f2.data(), f2.size());
    auto msgs = asm1.takeMessages();
    TA_CHECK_EQ(msgs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(msgs[0].opcode, kWsText);
    TA_CHECK_ST(std::string(msgs[0].payload.begin(), msgs[0].payload.end()), "Hello");
}

TA_TEST(ws_assembler_control_frame_interleaves_fragments) {
    WsMessageAssembler a;
    auto f1 = wsFrameBytes(false, kWsText, {'1', '2'});
    auto ping = wsFrameBytes(true, kWsPing, {'p'});
    auto f2 = wsFrameBytes(true, kWsContinuation, {'3'});
    a.feed(f1.data(), f1.size());
    a.feed(ping.data(), ping.size());
    auto mid = a.takeMessages();
    TA_CHECK_EQ(mid.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(mid[0].opcode, kWsPing);
    a.feed(f2.data(), f2.size());
    auto done = a.takeMessages();
    TA_CHECK_EQ(done.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(done[0].opcode, kWsText);
    TA_CHECK_ST(std::string(done[0].payload.begin(), done[0].payload.end()), "123");
}

TA_TEST(ws_assembler_byte_by_byte_feed) {
    WsMessageAssembler a;
    auto f = wsFrameBytes(true, kWsText, {'o', 'k'});
    for (size_t i = 0; i < f.size(); ++i) {
        a.feed(f.data() + i, 1);
    }
    auto msgs = a.takeMessages();
    TA_CHECK_EQ(msgs.size(), static_cast<size_t>(1));
    TA_CHECK_ST(std::string(msgs[0].payload.begin(), msgs[0].payload.end()), "ok");
}

TA_TEST(ws_assembler_masks_are_stripped) {
    WsMessageAssembler a;
    auto f = wsFrameBytes(true, kWsText, {'s', 'e', 'c', 'r', 'e', 't'}, true, 0xAB);
    a.feed(f.data(), f.size());
    auto msgs = a.takeMessages();
    TA_CHECK_EQ(msgs.size(), static_cast<size_t>(1));
    TA_CHECK_ST(std::string(msgs[0].payload.begin(), msgs[0].payload.end()), "secret");
}

TA_TEST(ws_assembler_close_frame_short_cuts_fragmentation) {
    WsMessageAssembler a;
    auto f1 = wsFrameBytes(false, kWsText, {'x'});
    auto close = wsFrameBytes(true, kWsClose, {0x03, 0xE8});  // 1008
    a.feed(f1.data(), f1.size());
    a.feed(close.data(), close.size());
    auto msgs = a.takeMessages();
    bool hasClose = false;
    for (auto& m : msgs) {
        if (m.opcode == kWsClose) hasClose = true;
    }
    TA_CHECK(hasClose);
}
