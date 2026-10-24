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

TA_TEST(quic_detects_long_header_v1) {
    Bytes b = {0xC0, 0x00, 0x00, 0x00, 0x01, 0x08};
    QuicInfo q{};
    TA_CHECK_EQ(detectQuic(b.data(), b.size(), &q), QuicStatus::Ok);
    TA_CHECK(q.longHeader);
    TA_CHECK_EQ(q.version, 1u);
    TA_CHECK(!q.versionNegotiation);
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
