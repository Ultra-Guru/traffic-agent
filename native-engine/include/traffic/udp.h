#pragma once

#include <cstddef>
#include <cstdint>

namespace traffic {

struct UdpHeader {
    uint16_t srcPort = 0;
    uint16_t dstPort = 0;
    uint16_t length = 0;  // UDP length field (header + payload)
    uint16_t checksum = 0;
};

enum class UdpStatus { Ok, TooShort, BadLength };

UdpStatus parseUdp(const uint8_t* data, size_t len, UdpHeader* out);

}  // namespace traffic
