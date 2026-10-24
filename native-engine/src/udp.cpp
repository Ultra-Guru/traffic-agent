#include "traffic/udp.h"

namespace traffic {

UdpStatus parseUdp(const uint8_t* data, size_t len, UdpHeader* out) {
    if (data == nullptr || out == nullptr) return UdpStatus::TooShort;
    if (len < 8) return UdpStatus::TooShort;  // MUT:<=
    out->srcPort = static_cast<uint16_t>((data[0] << 8) | data[1]);
    out->dstPort = static_cast<uint16_t>((data[2] << 8) | data[3]);
    out->length = static_cast<uint16_t>((data[4] << 8) | data[5]);
    out->checksum = static_cast<uint16_t>((data[6] << 8) | data[7]);
    if (out->length < 8) return UdpStatus::BadLength;  // MUT:<=
    return UdpStatus::Ok;
}

}  // namespace traffic
