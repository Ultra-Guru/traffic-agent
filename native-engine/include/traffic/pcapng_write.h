#pragma once

// pcapng dump writer (the modern companion to the classic pcap writer).
//
// Emits a minimal-but-standards-compliant pcapng file: one Section Header
// Block carrying the byte-order magic and an shb_userappl option, one
// Interface Description Block with if_tsresol = 6 (microsecond resolution),
// then Enhanced Packet Blocks with data padded to the 32-bit boundary.
// Wireshark/tcpdump and our own parsePcapng() reader accept the result.
//
// Block layout reference: "PCAP Next Generation Dump File Format" spec.

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <string>

#include "pcap_write.h"

namespace traffic {

class PcapNgWriter {
public:
    // LINKTYPE_RAW: the record payload is a raw IPv4 datagram (TUN output).
    static constexpr uint16_t kLinkTypeRaw = 101;
    // LINKTYPE_ETHERNET: the record payload is a full Ethernet frame.
    static constexpr uint16_t kLinkTypeEthernet = 1;

    // Opens (truncating) [path] and writes SHB + IDB. Returns nullptr when
    // the file cannot be created. Timestamps are stored with microsecond
    // resolution (if_tsresol = 6); [snaplen] clips stored bytes per packet.
    static std::unique_ptr<PcapNgWriter> open(const std::string& path,
                                              uint32_t snaplen = 0xFFFF,
                                              uint16_t linkType = kLinkTypeRaw,
                                              const std::string& appName = "traffic-agent");

    ~PcapNgWriter();

    PcapNgWriter(const PcapNgWriter&) = delete;
    PcapNgWriter& operator=(const PcapNgWriter&) = delete;

    // Appends one Enhanced Packet Block. [timestampMs] is converted to the
    // 64-bit timestamp unit chosen in the IDB (microseconds).
    PcapWriteStatus writePacket(const uint8_t* data, size_t len, uint64_t timestampMs);

    PcapWriteStatus flush();

    // Idempotent; the destructor flushes and closes as well.
    void close();

    uint64_t packetsWritten() const { return packets_; }
    uint64_t bytesWritten() const { return bytes_; }
    bool isOpen() const { return file_ != nullptr; }

private:
    explicit PcapNgWriter(std::FILE* file, uint32_t snaplen);

    std::FILE* file_ = nullptr;
    uint32_t snaplen_ = 0xFFFF;
    uint64_t packets_ = 0;
    uint64_t bytes_ = 0;
};

}  // namespace traffic
