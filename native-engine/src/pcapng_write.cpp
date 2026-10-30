#include "traffic/pcapng_write.h"

#include <cstring>
#include <vector>

namespace traffic {

namespace {

// pcapng block types (spec section 3.1 and friends).
constexpr uint32_t kBlockShb = 0x0A0D0D0Au;
constexpr uint32_t kBlockIdb = 0x00000001u;
constexpr uint32_t kBlockEpb = 0x00000006u;
constexpr uint32_t kByteOrderMagic = 0x1A2B3C4Du;

// Option codes.
constexpr uint16_t kOptEndOfOpt = 0;
constexpr uint16_t kOptIfTsresol = 9;
constexpr uint16_t kOptShbUserAppl = 4;

size_t pad4(size_t n) { return (n + 3u) & ~static_cast<size_t>(3u); }

void appendU16(std::vector<uint8_t>* out, uint16_t v) {
    out->push_back(static_cast<uint8_t>(v & 0xFF));
    out->push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
}

void appendU32(std::vector<uint8_t>* out, uint32_t v) {
    out->push_back(static_cast<uint8_t>(v & 0xFF));
    out->push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
    out->push_back(static_cast<uint8_t>((v >> 16) & 0xFF));
    out->push_back(static_cast<uint8_t>((v >> 24) & 0xFF));
}

void appendU64(std::vector<uint8_t>* out, uint64_t v) {
    appendU32(out, static_cast<uint32_t>(v & 0xFFFFFFFFu));
    appendU32(out, static_cast<uint32_t>((v >> 32) & 0xFFFFFFFFu));
}

// Appends one option (code + padded length + value); caller adds endofopt.
void appendOption(std::vector<uint8_t>* out, uint16_t code, const uint8_t* value, size_t len) {
    appendU16(out, code);
    appendU16(out, static_cast<uint16_t>(len));
    size_t before = out->size();
    out->insert(out->end(), value, value + len);
    out->resize(pad4(out->size()));
    (void)before;
}

// A block is emitted as: type, total length, body, [padding], total length.
// The body vector must already contain everything between the two length
// fields, padded per the spec's per-block rules.
bool writeBlock(std::FILE* f, uint32_t type, const std::vector<uint8_t>& body) {
    uint32_t total = static_cast<uint32_t>(12 + body.size());  // 4+4+body+4
    if (std::fwrite(&type, 4, 1, f) != 1) return false;
    if (std::fwrite(&total, 4, 1, f) != 1) return false;
    if (!body.empty() && std::fwrite(body.data(), body.size(), 1, f) != 1) return false;
    if (std::fwrite(&total, 4, 1, f) != 1) return false;
    return true;
}

}  // namespace

std::unique_ptr<PcapNgWriter> PcapNgWriter::open(const std::string& path, uint32_t snaplen,
                                                 uint16_t linkType,
                                                 const std::string& appName) {
    std::FILE* f = std::fopen(path.c_str(), "wb");
    if (f == nullptr) return nullptr;

    // --- Section Header Block ---
    std::vector<uint8_t> shb;
    appendU32(&shb, kByteOrderMagic);
    appendU16(&shb, 1);  // major
    appendU16(&shb, 0);  // minor
    appendU64(&shb, 0xFFFFFFFFFFFFFFFFull);  // section length: unspecified
    appendOption(&shb, kOptShbUserAppl,
                 reinterpret_cast<const uint8_t*>(appName.data()), appName.size());
    appendU16(&shb, kOptEndOfOpt);
    appendU16(&shb, 0);
    if (!writeBlock(f, kBlockShb, shb)) {
        std::fclose(f);
        return nullptr;
    }

    // --- Interface Description Block ---
    std::vector<uint8_t> idb;
    appendU16(&idb, linkType);
    appendU16(&idb, 0);  // reserved
    appendU32(&idb, snaplen == 0 ? 0xFFFF : snaplen);
    const uint8_t tsresol = 6;  // 10^-6: microseconds
    appendOption(&idb, kOptIfTsresol, &tsresol, 1);
    appendU16(&idb, kOptEndOfOpt);
    appendU16(&idb, 0);
    if (!writeBlock(f, kBlockIdb, idb)) {
        std::fclose(f);
        return nullptr;
    }

    if (std::fflush(f) != 0) {
        std::fclose(f);
        return nullptr;
    }
    return std::unique_ptr<PcapNgWriter>(new PcapNgWriter(f, snaplen));
}

PcapNgWriter::PcapNgWriter(std::FILE* file, uint32_t snaplen)
    : file_(file), snaplen_(snaplen == 0 ? 0xFFFF : snaplen) {}

PcapNgWriter::~PcapNgWriter() { close(); }

PcapWriteStatus PcapNgWriter::writePacket(const uint8_t* data, size_t len,
                                          uint64_t timestampMs) {
    if (file_ == nullptr) return PcapWriteStatus::NotOpen;

    const uint32_t original = static_cast<uint32_t>(len);
    const uint32_t stored = static_cast<uint32_t>((len > snaplen_) ? snaplen_ : len);

    // 64-bit timestamp in IDB units: microseconds.
    const uint64_t tsUs = timestampMs * 1000u;

    std::vector<uint8_t> body;
    body.reserve(20 + pad4(stored));
    appendU32(&body, 0);  // interface id
    appendU32(&body, static_cast<uint32_t>((tsUs >> 32) & 0xFFFFFFFFu));
    appendU32(&body, static_cast<uint32_t>(tsUs & 0xFFFFFFFFu));
    appendU32(&body, stored);
    appendU32(&body, original);
    size_t dataStart = body.size();
    body.resize(body.size() + pad4(stored), 0);
    if (stored > 0) {
        std::memcpy(body.data() + dataStart, data, stored);  // MUT:==
    }

    if (!writeBlock(file_, kBlockEpb, body)) return PcapWriteStatus::WriteError;
    ++packets_;
    bytes_ += 12 + body.size();
    return PcapWriteStatus::Ok;
}

PcapWriteStatus PcapNgWriter::flush() {
    if (file_ == nullptr) return PcapWriteStatus::NotOpen;
    return (std::fflush(file_) == 0) ? PcapWriteStatus::Ok : PcapWriteStatus::WriteError;
}

void PcapNgWriter::close() {
    if (file_ != nullptr) {
        std::fclose(file_);
        file_ = nullptr;
    }
}

}  // namespace traffic
