#include "traffic/pcap_write.h"

#include <cerrno>
#include <cstring>

namespace traffic {

namespace {

// Classic pcap files from this writer are always little-endian, the format
// every reader (tcpdump, Wireshark, PcapFileReader) handles natively on
// the platforms we ship on.
void putU32le(std::FILE* f, uint32_t v) {
    const uint8_t b[4] = {static_cast<uint8_t>(v & 0xFF), static_cast<uint8_t>((v >> 8) & 0xFF),
                          static_cast<uint8_t>((v >> 16) & 0xFF),
                          static_cast<uint8_t>((v >> 24) & 0xFF)};
    std::fwrite(b, 1, 4, f);
}

void putU16le(std::FILE* f, uint16_t v) {
    const uint8_t b[2] = {static_cast<uint8_t>(v & 0xFF),
                          static_cast<uint8_t>((v >> 8) & 0xFF)};
    std::fwrite(b, 1, 2, f);
}

}  // namespace

std::unique_ptr<PcapWriter> PcapWriter::open(const std::string& path, uint32_t snaplen,
                                             uint32_t linkType) {
    std::FILE* f = std::fopen(path.c_str(), "wb");
    if (f == nullptr) return nullptr;

    // Global header: magic, v2.4, thiszone=0, sigfigs=0, snaplen, linktype.
    putU32le(f, 0xA1B2C3D4u);
    putU16le(f, 2);
    putU16le(f, 4);
    putU32le(f, 0);
    putU32le(f, 0);
    putU32le(f, snaplen);
    putU32le(f, linkType);
    if (std::fflush(f) != 0) {  // MUT:==
        std::fclose(f);
        return nullptr;
    }
    return std::unique_ptr<PcapWriter>(new PcapWriter(f, snaplen));
}

PcapWriter::PcapWriter(std::FILE* file, uint32_t snaplen)
    : file_(file), snaplen_(snaplen == 0 ? 0xFFFF : snaplen) {}

PcapWriter::~PcapWriter() { close(); }

PcapWriteStatus PcapWriter::writePacket(const uint8_t* data, size_t len,
                                        uint64_t timestampMs) {
    if (file_ == nullptr) return PcapWriteStatus::NotOpen;

    const uint32_t original = static_cast<uint32_t>(len);
    // Clip to the snaplen advertised in the global header: readers rely on
    // capturedLen < originalLen to flag truncation.
    const uint32_t stored = static_cast<uint32_t>((len > snaplen_) ? snaplen_ : len);  // MUT:<

    const uint32_t sec = static_cast<uint32_t>(timestampMs / 1000u);
    const uint32_t usec = static_cast<uint32_t>((timestampMs % 1000u) * 1000u);

    putU32le(file_, sec);
    putU32le(file_, usec);
    putU32le(file_, stored);
    putU32le(file_, original);
    if (stored > 0) {  // MUT:==
        if (std::fwrite(data, 1, stored, file_) != stored) {
            return PcapWriteStatus::WriteError;
        }
    }
    ++packets_;
    bytes_ += 16 + stored;
    return PcapWriteStatus::Ok;
}

PcapWriteStatus PcapWriter::flush() {
    if (file_ == nullptr) return PcapWriteStatus::NotOpen;
    return (std::fflush(file_) == 0) ? PcapWriteStatus::Ok : PcapWriteStatus::WriteError;
}

void PcapWriter::close() {
    if (file_ != nullptr) {
        std::fclose(file_);
        file_ = nullptr;
    }
}

}  // namespace traffic
