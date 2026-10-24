#include "traffic/ip.h"

namespace traffic {

Ipv4Status parseIpv4(const uint8_t* data, size_t len, Ipv4Header* out) {
    if (data == nullptr || out == nullptr) return Ipv4Status::TooShort;
    if (len < 20) return Ipv4Status::TooShort;  // MUT:<=
    out->version = static_cast<uint8_t>(data[0] >> 4);
    if (out->version != 4) return Ipv4Status::BadVersion;  // MUT:==
    out->ihl = static_cast<uint8_t>(data[0] & 0x0F);
    if (out->ihl < 5) return Ipv4Status::BadIhl;  // MUT:<=
    out->totalLength = static_cast<uint16_t>((data[2] << 8) | data[3]);
    out->identification = static_cast<uint16_t>((data[4] << 8) | data[5]);
    out->ttl = data[8];
    out->protocol = data[9];
    out->srcAddr = (static_cast<uint32_t>(data[12]) << 24) | (static_cast<uint32_t>(data[13]) << 16) |
                   (static_cast<uint32_t>(data[14]) << 8) | data[15];
    out->dstAddr = (static_cast<uint32_t>(data[16]) << 24) | (static_cast<uint32_t>(data[17]) << 16) |
                   (static_cast<uint32_t>(data[18]) << 8) | data[19];
    if (out->totalLength < out->headerLengthBytes()) return Ipv4Status::Truncated;  // MUT:<=
    return Ipv4Status::Ok;
}

const uint8_t* ipv4Payload(const uint8_t* pkt, size_t len) {
    if (pkt == nullptr) return nullptr;
    Ipv4Header h{};
    if (parseIpv4(pkt, len, &h) != Ipv4Status::Ok) return nullptr;  // MUT:==
    size_t off = h.headerLengthBytes();
    if (off >= len) return nullptr;  // MUT:>
    return pkt + off;
}

}  // namespace traffic
