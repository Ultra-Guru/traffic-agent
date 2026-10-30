#include "traffic/engine.h"
#include "traffic/quic.h"

#include <cstring>

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

// RFC 9000 section 16 varint encodings: 2-bit length prefix.
Bytes varint(uint64_t v) {
    Bytes b;
    if (v < 64) {
        b.push_back(static_cast<uint8_t>(v));
    } else if (v < 16384) {
        b.push_back(static_cast<uint8_t>(0x40u | (v >> 8)));
        b.push_back(static_cast<uint8_t>(v & 0xffu));
    } else if (v < 1073741824) {
        b.push_back(static_cast<uint8_t>(0x80u | (v >> 24)));
        b.push_back(static_cast<uint8_t>((v >> 16) & 0xffu));
        b.push_back(static_cast<uint8_t>((v >> 8) & 0xffu));
        b.push_back(static_cast<uint8_t>(v & 0xffu));
    } else {
        b.push_back(static_cast<uint8_t>(0xc0u | (v >> 56)));
        for (int i = 7; i >= 0; --i) {
            b.push_back(static_cast<uint8_t>((v >> (i * 8)) & 0xffu));
        }
    }
    return b;
}

// Builds a long-header Initial packet (cleartext portion only).
Bytes quicInitial(uint32_t version, const Bytes& dcid, const Bytes& scid,
                  const Bytes& token, uint64_t payloadLen, uint8_t pnLen = 1,
                  size_t trailingBytes = 64) {
    Bytes p;
    // First byte: 0x80 long header | 0x40 fixed | type Initial(0) | pn len-1.
    p.push_back(static_cast<uint8_t>(0xc0u | (pnLen - 1u)));
    pushU32(p, version);
    p.push_back(static_cast<uint8_t>(dcid.size()));
    p.insert(p.end(), dcid.begin(), dcid.end());
    p.push_back(static_cast<uint8_t>(scid.size()));
    p.insert(p.end(), scid.begin(), scid.end());
    Bytes tok = varint(token.size());
    p.insert(p.end(), tok.begin(), tok.end());
    p.insert(p.end(), token.begin(), token.end());
    Bytes len = varint(payloadLen);
    p.insert(p.end(), len.begin(), len.end());
    // packet number + encrypted bytes (placeholder for structure tests).
    for (uint8_t i = 0; i < pnLen; ++i) p.push_back(0x11);
    for (size_t i = 0; i < trailingBytes; ++i) p.push_back(0xAB);
    return p;
}

}  // namespace

// ---------------- varint ----------------

TA_TEST(quic_varint_all_widths) {
    const uint8_t one[1] = {0x25};           // 0b00100101 -> 37
    const uint8_t two[2] = {0x7b, 0xbd};     // 0b01111011 -> 15293
    const uint8_t four[4] = {0x9d, 0x7f, 0x3e, 0x7d};  // 494878333
    const uint8_t eight[8] = {0xc2, 0x19, 0x7c, 0x5e, 0xff, 0x14, 0xe8, 0x8c};

    size_t off = 0;
    uint64_t v = 0;
    TA_CHECK_EQ(quicReadVarint(one, sizeof(one), &off, &v), QuicParseStatus::Ok);
    TA_CHECK_EQ(v, 37u);
    TA_CHECK_EQ(off, 1u);

    off = 0;
    TA_CHECK_EQ(quicReadVarint(two, sizeof(two), &off, &v), QuicParseStatus::Ok);
    TA_CHECK_EQ(v, 15293u);
    TA_CHECK_EQ(off, 2u);

    off = 0;
    TA_CHECK_EQ(quicReadVarint(four, sizeof(four), &off, &v), QuicParseStatus::Ok);
    TA_CHECK_EQ(v, 494878333u);
    TA_CHECK_EQ(off, 4u);

    off = 0;
    TA_CHECK_EQ(quicReadVarint(eight, sizeof(eight), &off, &v), QuicParseStatus::Ok);
    TA_CHECK_EQ(v, 151288809941952652ull);
    TA_CHECK_EQ(off, 8u);
}

TA_TEST(quic_varint_rejects_truncated) {
    // Claims a 4-byte varint (0x9d prefix) but only 3 bytes remain.
    const uint8_t four[3] = {0x9d, 0x7f, 0x3e};
    size_t off = 0;
    uint64_t v = 0;
    TA_CHECK_EQ(quicReadVarint(four, sizeof(four), &off, &v), QuicParseStatus::Truncated);
    TA_CHECK_EQ(off, 0u);  // offset untouched on failure
}

TA_TEST(quic_varint_rejects_empty) {
    size_t off = 0;
    uint64_t v = 0;
    TA_CHECK_EQ(quicReadVarint(nullptr, 0, &off, &v), QuicParseStatus::TooShort);
}

// ---------------- long header ----------------

TA_TEST(quic_long_header_initial_fields) {
    const Bytes dcid = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    const Bytes scid = {0xA0, 0xA1};
    Bytes pkt = quicInitial(0x00000001u, dcid, scid, Bytes{}, 1200, 2);

    QuicLongHeader lh{};
    TA_CHECK_EQ(parseQuicLongHeader(pkt.data(), pkt.size(), &lh), QuicParseStatus::Ok);
    TA_CHECK(lh.type == QuicLongType::Initial);
    TA_CHECK_EQ(lh.version, 0x00000001u);
    TA_CHECK_EQ(lh.packetNumberLength, 2u);
    TA_CHECK(lh.dcid == dcid);
    TA_CHECK(lh.scid == scid);
    TA_CHECK(lh.token.empty());
    TA_CHECK_EQ(lh.payloadLength, 1200u);
    TA_CHECK(lh.originalDcid.empty());
}

TA_TEST(quic_long_header_initial_with_token) {
    const Bytes token = {0xDE, 0xAD, 0xBE, 0xEF, 0x01};
    Bytes pkt = quicInitial(0xff00001du, Bytes{0x11}, Bytes{}, token, 40, 4);

    QuicLongHeader lh{};
    TA_CHECK_EQ(parseQuicLongHeader(pkt.data(), pkt.size(), &lh), QuicParseStatus::Ok);
    TA_CHECK(lh.type == QuicLongType::Initial);
    TA_CHECK(lh.token == token);
    TA_CHECK_EQ(lh.version, 0xff00001du);
}

TA_TEST(quic_long_header_rejects_short) {
    Bytes pkt = quicInitial(1, Bytes{}, Bytes{}, Bytes{}, 10);
    QuicLongHeader lh{};
    TA_CHECK_EQ(parseQuicLongHeader(pkt.data(), 3, &lh), QuicParseStatus::TooShort);
    TA_CHECK_EQ(parseQuicLongHeader(nullptr, pkt.size(), &lh), QuicParseStatus::TooShort);
}

TA_TEST(quic_long_header_rejects_cid_overflow) {
    // DCID length byte of 21 exceeds the RFC 9000 maximum of 20.
    Bytes p;
    p.push_back(0xc0);
    pushU32(p, 1);
    p.push_back(21);
    for (int i = 0; i < 21; ++i) p.push_back(0);
    QuicLongHeader lh{};
    TA_CHECK_EQ(parseQuicLongHeader(p.data(), p.size(), &lh), QuicParseStatus::BadCidLength);
}

TA_TEST(quic_long_header_rejects_truncated_packet_number) {
    // pn length 4 but the packet is cut right after the payload length.
    Bytes pkt = quicInitial(1, Bytes{0x01}, Bytes{0x02}, Bytes{}, 5, 4, 8);
    pkt.resize(pkt.size() - 10);  // drop the payload + 2 of the 4 pn bytes
    QuicLongHeader lh{};
    TA_CHECK_EQ(parseQuicLongHeader(pkt.data(), pkt.size(), &lh), QuicParseStatus::Truncated);
}

TA_TEST(quic_long_header_rejects_short_header_input) {
    // 0-RTT protected packet form uses the short header bit pattern.
    Bytes p = {0x40, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00};
    QuicLongHeader lh{};
    TA_CHECK_EQ(parseQuicLongHeader(p.data(), p.size(), &lh), QuicParseStatus::NotLongHeader);
}

TA_TEST(quic_long_header_packet_number_lengths) {
    for (uint8_t pnLen = 1; pnLen <= 4; ++pnLen) {
        Bytes pkt = quicInitial(0x00000001u, Bytes{0x9A}, Bytes{}, Bytes{}, 100, pnLen);
        QuicLongHeader lh{};
        TA_CHECK_EQ(parseQuicLongHeader(pkt.data(), pkt.size(), &lh), QuicParseStatus::Ok);
        TA_CHECK_EQ(lh.packetNumberLength, pnLen);
    }
}

// ---------------- version naming ----------------

TA_TEST(quic_version_names) {
    TA_CHECK_ST(quicVersionName(0x00000001u), "v1");
    TA_CHECK_ST(quicVersionName(0x6b3343cfu), "v2");
    TA_CHECK_ST(quicVersionName(0x00000000u), "negotiation");
    TA_CHECK_ST(quicVersionName(0xff00001du), "draft-29");
    TA_CHECK_ST(quicVersionName(0xff000023u), "draft-35");
    TA_CHECK_ST(quicVersionName(0xfaceb000u), "mvfst");
    TA_CHECK_ST(quicVersionName(0x51303530u), "Q050");
    TA_CHECK_ST(quicVersionName(0x12345678u), "0x12345678");
}

// ---------------- engine integration ----------------

TA_TEST(quic_engine_emits_initial_event) {
    // A UDP:443 datagram carrying a long-header Initial must produce both
    // QuicDetected and QuicInitialDetected events through the engine.
    Engine engine;
    const Bytes dcid = {0xC0, 0xFF, 0xEE};
    Bytes payload = quicInitial(0x00000001u, dcid, Bytes{}, Bytes{}, 30, 1, 16);
    Bytes ip = ipv4(udpDatagram(54321, 443, payload), 17);
    engine.feedPacket(ip.data(), ip.size(), 1000);

    bool sawDetect = false;
    bool sawInitial = false;
    std::string initialText;
    for (const EngineEvent& ev : engine.events()) {
        if (ev.kind == EngineEvent::Kind::QuicDetected) sawDetect = true;
        if (ev.kind == EngineEvent::Kind::QuicInitialDetected) {
            sawInitial = true;
            initialText = ev.text;
        }
    }
    TA_CHECK(sawDetect);
    TA_CHECK(sawInitial);
    // text = "v1|c0ffee"
    TA_CHECK_ST(initialText, "v1|c0ffee");
}

TA_TEST(quic_engine_short_header_no_initial_event) {
    Engine engine;
    // Short header (0x40 fixed bit, no version): detection only, no Initial.
    Bytes payload = {0x40, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};
    Bytes ip = ipv4(udpDatagram(50000, 443, payload), 17);
    engine.feedPacket(ip.data(), ip.size(), 1000);

    bool sawInitial = false;
    for (const EngineEvent& ev : engine.events()) {
        if (ev.kind == EngineEvent::Kind::QuicInitialDetected) sawInitial = true;
    }
    TA_CHECK(!sawInitial);
}
