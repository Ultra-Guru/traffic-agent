#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

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

// Long-header packet types (RFC 9000 section 17.2).
enum class QuicLongType {
    Initial = 0x00,
    ZeroRtt = 0x01,
    Handshake = 0x02,
    Retry = 0x03,
};

// Deep walk of a QUIC long header (the plaintext part; payload stays
// encrypted). Covers Initial / 0-RTT / Handshake / Retry variants.
struct QuicLongHeader {
    QuicLongType type = QuicLongType::Initial;
    uint32_t version = 0;
    uint8_t packetNumberLength = 0;      // 1..4 bytes
    std::vector<uint8_t> dcid;           // <= 20 bytes
    std::vector<uint8_t> scid;           // <= 20 bytes
    // Initial packets only:
    std::vector<uint8_t> token;          // may be empty
    uint64_t payloadLength = 0;          // varint, may exceed the buffer
    // Retry packets only:
    std::vector<uint8_t> originalDcid;   // retry's ODCID field
};

enum class QuicParseStatus {
    Ok,
    TooShort,
    NotLongHeader,
    BadCidLength,
    BadVarint,
    Truncated,
};

// RFC 9000 section 16 QUIC variable-length integer. Reads one varint from
// data[off..len); on success stores the value and the new offset.
QuicParseStatus quicReadVarint(const uint8_t* data, size_t len, size_t* off, uint64_t* value);

// Parses the cleartext portion of a QUIC long header packet.
QuicParseStatus parseQuicLongHeader(const uint8_t* data, size_t len, QuicLongHeader* out);

// Human-readable version tag: "v1", "v2", "draft-29", "Q050", "mvfst", or
// "0x%08x" for unknown values.
std::string quicVersionName(uint32_t version);

}  // namespace traffic
