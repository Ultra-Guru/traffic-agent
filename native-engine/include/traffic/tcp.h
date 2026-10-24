#pragma once

#include <cstddef>
#include <cstdint>

namespace traffic {

struct TcpHeader {
    uint16_t srcPort = 0;
    uint16_t dstPort = 0;
    uint32_t seq = 0;
    uint32_t ack = 0;
    uint8_t dataOffset = 0;  // 32-bit words
    uint8_t flags = 0;
    uint16_t window = 0;
    uint16_t checksum = 0;

    static constexpr uint8_t kFin = 0x01;
    static constexpr uint8_t kSyn = 0x02;
    static constexpr uint8_t kRst = 0x04;
    static constexpr uint8_t kPsh = 0x08;
    static constexpr uint8_t kAck = 0x10;

    uint8_t headerLengthBytes() const { return static_cast<uint8_t>(dataOffset * 4); }
    bool has(uint8_t f) const { return (flags & f) != 0; }
};

enum class TcpStatus { Ok, TooShort, BadOffset };

TcpStatus parseTcp(const uint8_t* data, size_t len, TcpHeader* out);

// Byte offset of the TCP payload within the segment (== header length).
size_t tcpPayloadOffset(const TcpHeader& h);

}  // namespace traffic
