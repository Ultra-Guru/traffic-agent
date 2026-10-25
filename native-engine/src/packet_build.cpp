#include "traffic/packet_build.h"

#include <cstring>

#include "traffic/ip.h"
#include "traffic/tcp.h"

namespace traffic {

namespace {

void putU16(std::vector<uint8_t>& b, size_t pos, uint16_t v) {
    b[pos] = static_cast<uint8_t>(v >> 8);
    b[pos + 1] = static_cast<uint8_t>(v & 0xFF);
}

void putU32(std::vector<uint8_t>& b, size_t pos, uint32_t v) {
    b[pos] = static_cast<uint8_t>(v >> 24);
    b[pos + 1] = static_cast<uint8_t>((v >> 16) & 0xFF);
    b[pos + 2] = static_cast<uint8_t>((v >> 8) & 0xFF);
    b[pos + 3] = static_cast<uint8_t>(v & 0xFF);
}

}  // namespace

uint16_t ipChecksum(const uint8_t* data, size_t len) {
    uint32_t sum = 0;
    size_t i = 0;
    while (i + 1 < len) {
        sum += static_cast<uint32_t>(data[i]) << 8 | data[i + 1];
        i += 2;
    }
    if (i < len) {
        sum += static_cast<uint32_t>(data[i]) << 8;
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<uint16_t>(~sum & 0xFFFF);
}

std::vector<uint8_t> buildTcpPacket(uint32_t srcAddr, uint32_t dstAddr,
                                     uint16_t srcPort, uint16_t dstPort,
                                     uint32_t seq, uint32_t ack, uint8_t flags,
                                     uint16_t window, const uint8_t* payload,
                                     size_t len) {
    const size_t kTcpHeader = 20;
    const size_t kIpHeader = 20;
    std::vector<uint8_t> pkt(kIpHeader + kTcpHeader + len, 0);

    // IPv4 header
    pkt[0] = 0x45;  // version 4, IHL 5
    putU16(pkt, 2, static_cast<uint16_t>(kIpHeader + kTcpHeader + len));
    putU16(pkt, 4, 0x0001);  // identification
    pkt[8] = 64;             // TTL
    pkt[9] = 6;               // protocol TCP
    putU32(pkt, 12, srcAddr);
    putU32(pkt, 16, dstAddr);
    putU16(pkt, 10, ipChecksum(pkt.data(), kIpHeader));  // header checksum

    // TCP header
    const size_t t = kIpHeader;
    putU16(pkt, t + 0, srcPort);
    putU16(pkt, t + 2, dstPort);
    putU32(pkt, t + 4, seq);
    putU32(pkt, t + 8, ack);
    pkt[t + 12] = 0x50;  // data offset 5 << 4
    pkt[t + 13] = flags;
    putU16(pkt, t + 14, window);
    if (len > 0 && payload != nullptr) {
        std::memcpy(pkt.data() + kIpHeader + kTcpHeader, payload, len);
    }

    // TCP checksum over pseudo header + segment.
    std::vector<uint8_t> pseudo(12 + kTcpHeader + len, 0);
    putU32(pseudo, 0, srcAddr);
    putU32(pseudo, 4, dstAddr);
    pseudo[8] = 0;
    pseudo[9] = 6;
    putU16(pseudo, 10, static_cast<uint16_t>(kTcpHeader + len));
    std::memcpy(pseudo.data() + 12, pkt.data() + kIpHeader, kTcpHeader + len);
    putU16(pkt, t + 16, ipChecksum(pseudo.data(), pseudo.size()));
    return pkt;
}

std::vector<uint8_t> buildUdpPacket(uint32_t srcAddr, uint32_t dstAddr,
                                     uint16_t srcPort, uint16_t dstPort,
                                     const uint8_t* payload, size_t len) {
    const size_t kUdpHeader = 8;
    const size_t kIpHeader = 20;
    std::vector<uint8_t> pkt(kIpHeader + kUdpHeader + len, 0);

    pkt[0] = 0x45;
    putU16(pkt, 2, static_cast<uint16_t>(kIpHeader + kUdpHeader + len));
    putU16(pkt, 4, 0x0002);
    pkt[8] = 64;
    pkt[9] = 17;  // UDP
    putU32(pkt, 12, srcAddr);
    putU32(pkt, 16, dstAddr);
    putU16(pkt, 10, ipChecksum(pkt.data(), kIpHeader));

    const size_t u = kIpHeader;
    putU16(pkt, u + 0, srcPort);
    putU16(pkt, u + 2, dstPort);
    putU16(pkt, u + 4, static_cast<uint16_t>(kUdpHeader + len));

    if (len > 0 && payload != nullptr) {
        std::memcpy(pkt.data() + kIpHeader + kUdpHeader, payload, len);
    }

    std::vector<uint8_t> pseudo(12 + kUdpHeader + len, 0);
    putU32(pseudo, 0, srcAddr);
    putU32(pseudo, 4, dstAddr);
    pseudo[8] = 0;
    pseudo[9] = 17;
    putU16(pseudo, 10, static_cast<uint16_t>(kUdpHeader + len));
    std::memcpy(pseudo.data() + 12, pkt.data() + kIpHeader, kUdpHeader + len);
    putU16(pkt, u + 6, ipChecksum(pseudo.data(), pseudo.size()));
    return pkt;
}

bool verifyIpChecksum(const uint8_t* ipPacket, size_t len) {
    if (len < 20) return false;
    // Sum of the whole header must fold to 0xFFFF so the inverted sum is 0.
    return ipChecksum(ipPacket, 20) == 0;  // MUT:!=
}

bool verifyTcpChecksum(const uint8_t* ipPacket, size_t len) {
    if (len < 40) return false;  // MUT:<=
    Ipv4Header ip{};
    if (parseIpv4(ipPacket, len, &ip) != Ipv4Status::Ok) return false;
    if (ip.protocol != 6) return false;  // MUT:==
    size_t transportLen = len - static_cast<size_t>(ip.headerLengthBytes());
    if (transportLen < 20) return false;  // MUT:<=
    const uint8_t* seg = ipPacket + ip.headerLengthBytes();

    std::vector<uint8_t> pseudo(12 + transportLen, 0);
    putU32(pseudo, 0, ip.srcAddr);
    putU32(pseudo, 4, ip.dstAddr);
    pseudo[8] = 0;
    pseudo[9] = 6;
    putU16(pseudo, 10, static_cast<uint16_t>(transportLen));
    std::memcpy(pseudo.data() + 12, seg, transportLen);
    return ipChecksum(pseudo.data(), pseudo.size()) == 0;  // MUT:!=
}

}  // namespace traffic
