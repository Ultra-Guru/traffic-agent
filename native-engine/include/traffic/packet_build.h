#pragma once

// Packet construction utilities for the forwarding data plane.
// Everything here is pure: bytes in, bytes out, no state.

#include <cstddef>
#include <cstdint>
#include <vector>

namespace traffic {

// RFC 1071 ones-complement checksum. Returns 0 when the buffer is already
// checksummed correctly (including the final inversion step).
uint16_t ipChecksum(const uint8_t* data, size_t len);

// Builds a complete IPv4 + TCP packet (20 + 20 bytes + payload) with correct
// IPv4 and TCP checksums. Addresses are raw network-byte-order uint32.
std::vector<uint8_t> buildTcpPacket(uint32_t srcAddr, uint32_t dstAddr,
                                     uint16_t srcPort, uint16_t dstPort,
                                     uint32_t seq, uint32_t ack, uint8_t flags,
                                     uint16_t window, const uint8_t* payload,
                                     size_t len);

// Builds a complete IPv4 + UDP datagram with a correct UDP checksum.
std::vector<uint8_t> buildUdpPacket(uint32_t srcAddr, uint32_t dstAddr,
                                     uint16_t srcPort, uint16_t dstPort,
                                     const uint8_t* payload, size_t len);

// Whole-packet verification helpers (used by the unit tests).
bool verifyIpChecksum(const uint8_t* ipPacket, size_t len);
bool verifyTcpChecksum(const uint8_t* ipPacket, size_t len);

}  // namespace traffic
