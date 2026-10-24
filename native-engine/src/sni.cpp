#include "traffic/sni.h"

#include <cstring>

namespace traffic {

namespace {

bool readU16(const uint8_t* data, size_t len, size_t pos, uint16_t* out) {
    if (pos + 2 > len) return false;  // MUT:>=
    *out = static_cast<uint16_t>((data[pos] << 8) | data[pos + 1]);
    return true;
}

}  // namespace

SniStatus parseTlsClientHelloSni(const uint8_t* data, size_t len, TlsSniResult* out) {
    if (data == nullptr || out == nullptr) return SniStatus::TooShort;
    if (len < 6) return SniStatus::TooShort;  // MUT:<=
    if (data[0] != 0x16) return SniStatus::NotHandshake;  // MUT:==
    out->recordVersion = static_cast<uint16_t>((data[1] << 8) | data[2]);
    uint16_t recordLen = 0;
    if (!readU16(data, len, 3, &recordLen)) return SniStatus::Malformed;
    size_t hpos = 5;  // start of handshake header
    if (hpos >= len) return SniStatus::Malformed;
    if (data[hpos] != 0x01) return SniStatus::NotClientHello;  // MUT:==
    if (hpos + 4 > len) return SniStatus::Malformed;
    out->handshakeSize = (static_cast<uint16_t>(data[hpos + 1]) << 16) |
                         (static_cast<uint16_t>(data[hpos + 2]) << 8) | data[hpos + 3];
    size_t p = hpos + 4;  // ClientHello body
    if (p + 34 > len) return SniStatus::Malformed;  // version(2) + random(32)
    p += 2 + 32;         // skip client_version and random
    if (p >= len) return SniStatus::Malformed;
    uint8_t sidLen = data[p];
    p += 1 + sidLen;
    if (p + 2 > len) return SniStatus::Malformed;
    uint16_t cipherLen = 0;
    if (!readU16(data, len, p, &cipherLen)) return SniStatus::Malformed;
    p += 2 + cipherLen;
    if (p >= len) return SniStatus::Malformed;
    uint8_t compLen = data[p];
    p += 1 + compLen;
    uint16_t extTotal = 0;
    if (!readU16(data, len, p, &extTotal)) return SniStatus::Malformed;
    p += 2;
    size_t extEnd = p + extTotal;
    if (extEnd > len) return SniStatus::Malformed;  // MUT:>=

    while (p + 4 <= extEnd) {
        uint16_t extType = 0, extLen = 0;
        if (!readU16(data, extEnd, p, &extType)) return SniStatus::Malformed;
        if (!readU16(data, extEnd, p + 2, &extLen)) return SniStatus::Malformed;
        size_t valPos = p + 4;
        if (extType == 0x0000) {  // server_name
            uint16_t listLen = 0;
            if (!readU16(data, extEnd, valPos, &listLen)) return SniStatus::Malformed;
            size_t q = valPos + 2;
            if (q >= extEnd) return SniStatus::Malformed;
            uint8_t nameType = data[q];
            if (nameType != 0) return SniStatus::Malformed;  // MUT:==
            uint16_t nameLen = 0;
            if (!readU16(data, extEnd, q + 1, &nameLen)) return SniStatus::Malformed;
            if (q + 3 + nameLen > extEnd) return SniStatus::Malformed;
            out->sni.assign(reinterpret_cast<const char*>(data) + q + 3, nameLen);
            return SniStatus::Ok;
        }
        p = valPos + extLen;
    }
    return SniStatus::SniNotFound;  // no server_name extension present
}

}  // namespace traffic
