#pragma once

#include <cstddef>
#include <cstdint>

namespace traffic {

struct QuicInfo {
    bool longHeader = false;
    uint32_t version = 0;
    bool versionNegotiation = false;
};

enum class QuicStatus { Ok, TooShort, NotQuic };

// Detects QUIC from a UDP payload: long header (0x80 set) carries a 4-byte
// version; version 0 means version negotiation. Short header must have the
// fixed bit (0x40) set.
QuicStatus detectQuic(const uint8_t* data, size_t len, QuicInfo* out);

}  // namespace traffic
