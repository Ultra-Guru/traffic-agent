#include "traffic/pcapng.h"
#include "traffic/pcapng_write.h"

#include <cstdio>
#include <cstring>
#include <vector>

#include "test_framework.hpp"

using namespace traffic;

namespace {

std::vector<uint8_t> readFile(const char* path) {
    std::FILE* f = std::fopen(path, "rb");
    if (f == nullptr) return {};
    std::fseek(f, 0, SEEK_END);
    long n = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);
    std::vector<uint8_t> out(static_cast<size_t>(n));
    if (n > 0 && std::fread(out.data(), 1, static_cast<size_t>(n), f) != static_cast<size_t>(n)) {
        out.clear();
    }
    std::fclose(f);
    return out;
}

uint32_t le32(const std::vector<uint8_t>& b, size_t pos) {
    return static_cast<uint32_t>(b[pos]) | (static_cast<uint32_t>(b[pos + 1]) << 8) |
           (static_cast<uint32_t>(b[pos + 2]) << 16) | (static_cast<uint32_t>(b[pos + 3]) << 24);
}

// Minimal block walker: {type, bodyStart, bodyLen (excl. type/len/trailing)}.
struct BlockView {
    uint32_t type = 0;
    size_t start = 0;
    size_t bodyStart = 0;
    size_t bodyLen = 0;
    uint32_t total = 0;
};

std::vector<BlockView> walkBlocks(const std::vector<uint8_t>& b) {
    std::vector<BlockView> out;
    size_t pos = 0;
    while (pos + 8 <= b.size()) {
        BlockView v;
        v.type = le32(b, pos);
        v.total = le32(b, pos + 4);
        if (v.total < 12 || pos + v.total > b.size()) break;
        v.start = pos;
        v.bodyStart = pos + 8;
        v.bodyLen = v.total - 12;
        out.push_back(v);
        pos += v.total;
    }
    return out;
}

}  // namespace

TA_TEST(pcapng_shb_layout_and_byte_order_magic) {
    const char* path = "/tmp/ta_test_ng1.pcapng";
    auto w = PcapNgWriter::open(path, 0xFFFF, PcapNgWriter::kLinkTypeRaw, "ta-unit");
    TA_CHECK(w != nullptr);
    TA_CHECK(w->isOpen());
    w->close();

    auto b = readFile(path);
    auto blocks = walkBlocks(b);
    TA_CHECK_EQ(blocks.size(), static_cast<size_t>(2));  // SHB + IDB

    // SHB: type, byte-order magic, version 1.0, trailing length repeats.
    TA_CHECK_EQ(blocks[0].type, 0x0A0D0D0Au);
    TA_CHECK_EQ(le32(b, blocks[0].bodyStart), 0x1A2B3C4Du);
    TA_CHECK_EQ(b[blocks[0].bodyStart + 4], 1);  // major
    TA_CHECK_EQ(b[blocks[0].bodyStart + 6], 0);  // minor
    TA_CHECK_EQ(le32(b, blocks[0].start + blocks[0].total - 4), blocks[0].total);

    // IDB: LINKTYPE_RAW, snaplen 0xFFFF, if_tsresol option = 6.
    TA_CHECK_EQ(blocks[1].type, 0x00000001u);
    size_t idb = blocks[1].bodyStart;
    TA_CHECK_EQ(b[idb], 101);            // linktype low byte (RAW)
    TA_CHECK_EQ(b[idb + 2], 0);          // reserved
    TA_CHECK_EQ(le32(b, idb + 4), 0xFFFFu);  // snaplen
    // Option: if_tsresol (code 9), length 1, value 6.
    TA_CHECK_EQ(b[idb + 8], 9);
    TA_CHECK_EQ(b[idb + 9], 0);
    TA_CHECK_EQ(b[idb + 10], 1);
    TA_CHECK_EQ(b[idb + 12], 6);  // 10^-6 = microseconds
    std::remove(path);
}

TA_TEST(pcapng_epb_roundtrip_through_reader) {
    const char* path = "/tmp/ta_test_ng2.pcapng";
    auto w = PcapNgWriter::open(path, 0xFFFF, PcapNgWriter::kLinkTypeRaw);
    TA_CHECK(w != nullptr);

    std::vector<uint8_t> pkt(20, 0xAB);
    pkt[0] = 0x45;  // plausible IPv4 start
    TA_CHECK_EQ(w->writePacket(pkt.data(), pkt.size(), 1700000123ull),
                PcapWriteStatus::Ok);  // ts = 1700000.123 s
    std::vector<uint8_t> pkt2 = {0x45, 0x00, 0x00, 0x03};
    TA_CHECK_EQ(w->writePacket(pkt2.data(), pkt2.size(), 1700000456ull), PcapWriteStatus::Ok);
    TA_CHECK_EQ(w->packetsWritten(), static_cast<uint64_t>(2));
    w->close();

    // Our own reader must parse it back identically (microseconds -> ns).
    auto b = readFile(path);
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(b.data(), b.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(recs[0].data.size(), static_cast<size_t>(20));
    TA_CHECK(recs[0].data[0] == 0x45);
    TA_CHECK_EQ(recs[0].timestampNs, 1700000123ull * 1000000ull);
    TA_CHECK_EQ(recs[1].data.size(), static_cast<size_t>(4));
    TA_CHECK_EQ(recs[1].timestampNs, 1700000456ull * 1000000ull);
    std::remove(path);
}

TA_TEST(pcapng_snaplen_clips_and_reports_original) {
    const char* path = "/tmp/ta_test_ng3.pcapng";
    auto w = PcapNgWriter::open(path, 32, PcapNgWriter::kLinkTypeRaw);
    TA_CHECK(w != nullptr);
    std::vector<uint8_t> pkt(100, 0x42);
    TA_CHECK_EQ(w->writePacket(pkt.data(), pkt.size(), 5000), PcapWriteStatus::Ok);
    w->close();

    auto b = readFile(path);
    auto blocks = walkBlocks(b);
    TA_CHECK_EQ(blocks.size(), static_cast<size_t>(3));
    TA_CHECK_EQ(blocks[2].type, 0x00000006u);  // EPB
    size_t epb = blocks[2].bodyStart;
    size_t caplenPos = epb + 12;             // ifid(4) + tsHi(4) + tsLo(4)
    TA_CHECK_EQ(le32(b, caplenPos), 32u);    // captured
    TA_CHECK_EQ(le32(b, caplenPos + 4), 100u);  // original
    // Total: 12 + ifid4+ts8+caplen4+origlen4 + pad4(32)=32 => 12 + 20 + 32 = 64.
    TA_CHECK_EQ(blocks[2].total, 64u);

    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(b.data(), b.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(recs[0].data.size(), static_cast<size_t>(32));
    std::remove(path);
}

TA_TEST(pcapng_pads_short_packets_to_32_bits) {
    const char* path = "/tmp/ta_test_ng4.pcapng";
    auto w = PcapNgWriter::open(path, 0xFFFF, PcapNgWriter::kLinkTypeEthernet);
    TA_CHECK(w != nullptr);
    std::vector<uint8_t> pkt5 = {1, 2, 3, 4, 5};
    TA_CHECK_EQ(w->writePacket(pkt5.data(), pkt5.size(), 1), PcapWriteStatus::Ok);
    w->close();

    auto b = readFile(path);
    auto blocks = walkBlocks(b);
    TA_CHECK_EQ(blocks.size(), static_cast<size_t>(3));
    TA_CHECK_EQ(blocks[2].type, 0x00000006u);
    // EPB total: 12 + 20 + pad4(5)=8 => 40.
    TA_CHECK_EQ(blocks[2].total, 40u);
    size_t dataStart = blocks[2].bodyStart + 20;
    // The 3 padding bytes after the 5 data bytes are zeros.
    TA_CHECK_EQ(b[dataStart + 5], 0);
    TA_CHECK_EQ(b[dataStart + 6], 0);
    TA_CHECK_EQ(b[dataStart + 7], 0);

    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(b.data(), b.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(recs[0].data.size(), static_cast<size_t>(5));
    std::remove(path);
}

TA_TEST(pcapng_not_open_after_close) {
    const char* path = "/tmp/ta_test_ng5.pcapng";
    auto w = PcapNgWriter::open(path);
    TA_CHECK(w != nullptr);
    w->close();
    TA_CHECK(!w->isOpen());
    uint8_t byte = 1;
    TA_CHECK_EQ(w->writePacket(&byte, 1, 0), PcapWriteStatus::NotOpen);
    TA_CHECK_EQ(w->flush(), PcapWriteStatus::NotOpen);
    std::remove(path);
}

TA_TEST(pcapng_open_failure_returns_null) {
    auto w = PcapNgWriter::open("/nonexistent-dir/ta.pcapng");
    TA_CHECK(w == nullptr);
}
