#pragma once

// Classic libpcap dump writer (基建四「存」的 PCAP 导出面).
//
// Emits exactly what PcapFileReader (core-capture) and Wireshark/tcpdump
// consume: a 24-byte little-endian global header (magic 0xa1b2c3d4, v2.4,
// snaplen, linktype) followed by per-packet records
// [tsSec][tsUsec][capturedLen][originalLen][bytes].
//
// The Android VpnService records every raw IPv4 packet it reads from the
// TUN fd, so the default link type is LINKTYPE_RAW (101): one record = one
// IPv4 datagram, no Ethernet header in between.

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <string>

namespace traffic {

enum class PcapWriteStatus { Ok, NotOpen, WriteError };

class PcapWriter {
public:
    // LINKTYPE_RAW: the record payload is a raw IPv4 datagram (TUN output).
    static constexpr uint32_t kLinkTypeRaw = 101;
    // LINKTYPE_ETHERNET: the record payload is a full Ethernet frame.
    static constexpr uint32_t kLinkTypeEthernet = 1;

    // Opens (truncating) [path] and writes the global header. Returns
    // nullptr when the file cannot be created. Snaplen caps the stored
    // bytes per record; the original length is always preserved.
    static std::unique_ptr<PcapWriter> open(const std::string& path,
                                            uint32_t snaplen = 0xFFFF,
                                            uint32_t linkType = kLinkTypeRaw);

    ~PcapWriter();

    PcapWriter(const PcapWriter&) = delete;
    PcapWriter& operator=(const PcapWriter&) = delete;

    // Appends one record. [timestampMs] is split into sec/usec; packets
    // longer than snaplen are clipped (capturedLen < originalLen), which
    // readers surface as a truncation hint.
    PcapWriteStatus writePacket(const uint8_t* data, size_t len, uint64_t timestampMs);

    // Flushes buffered stdio output; safe to call while capturing.
    PcapWriteStatus flush();

    // Idempotent; the destructor flushes and closes as well.
    void close();

    uint64_t packetsWritten() const { return packets_; }
    uint64_t bytesWritten() const { return bytes_; }
    bool isOpen() const { return file_ != nullptr; }

private:
    explicit PcapWriter(std::FILE* file, uint32_t snaplen);

    std::FILE* file_ = nullptr;
    uint32_t snaplen_ = 0xFFFF;
    uint64_t packets_ = 0;
    uint64_t bytes_ = 0;
};

}  // namespace traffic
