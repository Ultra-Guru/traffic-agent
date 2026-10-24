#include "traffic/quic.h"

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

}  // namespace traffic
