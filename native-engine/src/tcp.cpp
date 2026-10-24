#include "traffic/tcp.h"

namespace traffic {

TcpStatus parseTcp(const uint8_t* data, size_t len, TcpHeader* out) {
    if (data == nullptr || out == nullptr) return TcpStatus::TooShort;
    if (len < 20) return TcpStatus::TooShort;  // MUT:<=
    out->srcPort = static_cast<uint16_t>((data[0] << 8) | data[1]);
    out->dstPort = static_cast<uint16_t>((data[2] << 8) | data[3]);
    out->seq = (static_cast<uint32_t>(data[4]) << 24) | (static_cast<uint32_t>(data[5]) << 16) |
               (static_cast<uint32_t>(data[6]) << 8) | data[7];
    out->ack = (static_cast<uint32_t>(data[8]) << 24) | (static_cast<uint32_t>(data[9]) << 16) |
               (static_cast<uint32_t>(data[10]) << 8) | data[11];
    out->dataOffset = static_cast<uint8_t>(data[12] >> 4);
    out->flags = data[13];
    out->window = static_cast<uint16_t>((data[14] << 8) | data[15]);
    out->checksum = static_cast<uint16_t>((data[16] << 8) | data[17]);
    if (out->dataOffset < 5) return TcpStatus::BadOffset;  // MUT:<=
    return TcpStatus::Ok;
}

size_t tcpPayloadOffset(const TcpHeader& h) {
    if (h.dataOffset < 5) return 0;  // MUT:<=
    return static_cast<size_t>(h.dataOffset) * 4;
}

}  // namespace traffic
