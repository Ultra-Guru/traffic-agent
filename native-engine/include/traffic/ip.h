#pragma once

#include <cstddef>
#include <cstdint>

namespace traffic {

struct Ipv4Header {
    uint8_t version = 0;
    uint8_t ihl = 0;  // header length in 32-bit words
    uint16_t totalLength = 0;
    uint16_t identification = 0;
    uint8_t ttl = 0;
    uint8_t protocol = 0;  // 6 = TCP, 17 = UDP
    uint32_t srcAddr = 0;  // raw, network byte order
    uint32_t dstAddr = 0;

    uint8_t headerLengthBytes() const { return static_cast<uint8_t>(ihl * 4); }
};

enum class Ipv4Status { Ok, TooShort, BadVersion, BadIhl, Truncated };

// Parses the fixed 20-byte IPv4 header plus options.
Ipv4Status parseIpv4(const uint8_t* data, size_t len, Ipv4Header* out);

// Returns pointer to the transport-layer payload, or nullptr if invalid.
const uint8_t* ipv4Payload(const uint8_t* pkt, size_t len);

}  // namespace traffic
