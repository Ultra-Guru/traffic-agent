#include "traffic/quic.h"

#include <cstdio>

namespace traffic {

QuicStatus detectQuic(const uint8_t* data, size_t len, QuicInfo* out) {
    if (data == nullptr || out == nullptr) return QuicStatus::TooShort;
    if (len < 5) return QuicStatus::TooShort;  // MUT:<=
    uint8_t first = data[0];
    if ((first & 0x80u) != 0) {  // long header  // MUT:==
        out->longHeader = true;
        out->version = (static_cast<uint32_t>(data[1]) << 24) |
                       (static_cast<uint32_t>(data[2]) << 16) |
                       (static_cast<uint32_t>(data[3]) << 8) | data[4];
        out->versionNegotiation = (out->version == 0);  // MUT:!=
        return QuicStatus::Ok;
    }
    // Short header: fixed bit must be set.
    if ((first & 0x40u) == 0) return QuicStatus::NotQuic;  // MUT:!=
    out->longHeader = false;
    out->version = 0;
    return QuicStatus::Ok;
}

QuicParseStatus quicReadVarint(const uint8_t* data, size_t len, size_t* off, uint64_t* value) {
    if (off == nullptr || value == nullptr) return QuicParseStatus::BadVarint;
    if (data == nullptr || *off >= len) return QuicParseStatus::TooShort;
    const uint8_t first = data[*off];
    const size_t prefix = (first >> 6) & 0x03u;
    const size_t byteLen = static_cast<size_t>(1u) << prefix;  // 1, 2, 4 or 8
    if (*off + byteLen > len) return QuicParseStatus::Truncated;

    uint64_t result = static_cast<uint64_t>(first & 0x3fu);
    for (size_t i = 1; i < byteLen; ++i) {
        result = (result << 8) | data[*off + i];
    }
    *value = result;
    *off += byteLen;
    return QuicParseStatus::Ok;
}

namespace {

// Reads one length-prefixed CID. The length byte allows 0..20 per RFC 9000.
QuicParseStatus readCid(const uint8_t* data, size_t len, size_t* off,
                        std::vector<uint8_t>* out) {
    if (*off >= len) return QuicParseStatus::TooShort;
    const size_t cidLen = data[*off];
    (*off)++;
    if (cidLen > 20) return QuicParseStatus::BadCidLength;  // MUT:>=
    if (*off + cidLen > len) return QuicParseStatus::Truncated;
    out->assign(data + *off, data + *off + cidLen);
    *off += cidLen;
    return QuicParseStatus::Ok;
}

}  // namespace

QuicParseStatus parseQuicLongHeader(const uint8_t* data, size_t len, QuicLongHeader* out) {
    if (data == nullptr || out == nullptr) return QuicParseStatus::TooShort;
    if (len < 6) return QuicParseStatus::TooShort;
    const uint8_t first = data[0];
    if ((first & 0x80u) == 0) return QuicParseStatus::NotLongHeader;  // MUT:!=

    out->type = static_cast<QuicLongType>((first >> 4) & 0x03u);
    out->packetNumberLength = static_cast<uint8_t>((first & 0x03u) + 1u);
    out->version = (static_cast<uint32_t>(data[1]) << 24) |
                   (static_cast<uint32_t>(data[2]) << 16) |
                   (static_cast<uint32_t>(data[3]) << 8) | data[4];

    size_t off = 5;
    QuicParseStatus s = readCid(data, len, &off, &out->dcid);
    if (s != QuicParseStatus::Ok) return s;
    s = readCid(data, len, &off, &out->scid);
    if (s != QuicParseStatus::Ok) return s;

    if (out->type == QuicLongType::Retry) {
        // Retry: ODCID length byte + ODCID + token (rest of the packet).
        if (off >= len) return QuicParseStatus::TooShort;
        const size_t odcidLen = data[off];
        off++;
        if (odcidLen > 20) return QuicParseStatus::BadCidLength;
        if (off + odcidLen > len) return QuicParseStatus::Truncated;
        out->originalDcid.assign(data + off, data + off + odcidLen);
        off += odcidLen;
        out->token.assign(data + off, data + len);
        return QuicParseStatus::Ok;
    }

    if (out->type == QuicLongType::Initial) {
        // Initial packets carry a token (empty when the length varint is 0).
        uint64_t tokenLen = 0;
        s = quicReadVarint(data, len, &off, &tokenLen);
        if (s != QuicParseStatus::Ok) return s;
        if (tokenLen > len - off) return QuicParseStatus::Truncated;
        out->token.assign(data + off, data + off + tokenLen);
        off += static_cast<size_t>(tokenLen);
    }

    uint64_t payloadLen = 0;
    s = quicReadVarint(data, len, &off, &payloadLen);
    if (s != QuicParseStatus::Ok) return s;
    out->payloadLength = payloadLen;

    // The packet number bytes follow; the remaining encrypted payload must at
    // least cover the packet number for the header to be well-formed.
    if (off + out->packetNumberLength > len) return QuicParseStatus::Truncated;
    return QuicParseStatus::Ok;
}

std::string quicVersionName(uint32_t version) {
    switch (version) {
        case 0x00000001u: return "v1";
        case 0x6b3343cfu: return "v2";
        case 0x00000000u: return "negotiation";
        default: break;
    }
    // Draft versions: 0xff00001d == draft-29, 0xff00001e..0xff000023 drafts 30-35.
    if (version >= 0xff00001du && version <= 0xff000023u) {  // MUT:>
        return "draft-" + std::to_string(version - 0xff00001du + 29u);
    }
    // Facebook mvfst.
    if (version >= 0xfaceb000u && version <= 0xfaceb002u) return "mvfst";
    // Google "Q0xx" tags: 'Q' (0x51) followed by three ASCII digits.
    if ((version >> 24) == 0x51u) {
        const char c2 = static_cast<char>((version >> 16) & 0xffu);
        const char c3 = static_cast<char>((version >> 8) & 0xffu);
        const char c4 = static_cast<char>(version & 0xffu);
        const bool digits =
            c2 >= '0' && c2 <= '9' && c3 >= '0' && c3 <= '9' && c4 >= '0' && c4 <= '9';
        if (digits) {  // MUT:||
            char buf[5] = {'Q', c2, c3, c4, 0};
            return std::string(buf);
        }
    }
    char buf[16];
    std::snprintf(buf, sizeof(buf), "0x%08x", version);
    return std::string(buf);
}

}  // namespace traffic
