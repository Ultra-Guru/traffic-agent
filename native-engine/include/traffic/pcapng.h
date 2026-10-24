#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace traffic {

struct PcapngRecord {
    uint32_t interfaceId = 0;
    uint64_t timestampNs = 0;
    std::vector<uint8_t> data;  // captured packet bytes (link-layer frame)
};

enum class PcapngStatus { Ok, TooShort, BadByteOrderMagic, BadBlockLength, Unknown };

// Minimal pcapng reader (RFC "PCAP Next Generation Dump File Format"):
// SHB (endianness via byte-order magic), IDB (link type + ts resolution),
// EPB, SPB; ISB and unknown blocks are skipped by length. Both little and
// big endian files are supported.
PcapngStatus parsePcapng(const uint8_t* data, size_t len, std::vector<PcapngRecord>* records);

}  // namespace traffic
