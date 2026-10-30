// PcapWriter tests: on-disk byte layout of the classic pcap format plus
// the failure paths (bad path, double close, clipping).

#include "traffic/pcap_write.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "test_framework.hpp"

namespace {

std::vector<uint8_t> readFile(const std::string& path) {
    std::FILE* f = std::fopen(path.c_str(), "rb");
    if (f == nullptr) return {};
    std::vector<uint8_t> out;
    uint8_t buf[4096];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) {
        out.insert(out.end(), buf, buf + n);
    }
    std::fclose(f);
    return out;
}

uint32_t u32le(const std::vector<uint8_t>& b, size_t off) {
    return static_cast<uint32_t>(b[off]) | (static_cast<uint32_t>(b[off + 1]) << 8) |
           (static_cast<uint32_t>(b[off + 2]) << 16) | (static_cast<uint32_t>(b[off + 3]) << 24);
}

TA_TEST(pcap_write_global_header) {
    const std::string path = "/tmp/ta_pcap_test_global.pcap";
    std::remove(path.c_str());
    auto w = traffic::PcapWriter::open(path, 0xFFFF, traffic::PcapWriter::kLinkTypeRaw);
    TA_CHECK(w != nullptr);
    TA_CHECK(w->isOpen());
    w->close();
    TA_CHECK(!w->isOpen());

    const auto bytes = readFile(path);
    TA_CHECK_EQ(bytes.size(), 24u);
    // 0xa1b2c3d4 stored little-endian: d4 c3 b2 a1.
    TA_CHECK_EQ(bytes[0], 0xD4);
    TA_CHECK_EQ(bytes[1], 0xC3);
    TA_CHECK_EQ(bytes[2], 0xB2);
    TA_CHECK_EQ(bytes[3], 0xA1);
    TA_CHECK_EQ(u32le(bytes, 4), 2u | (4u << 16));  // major=2, minor=4
    TA_CHECK_EQ(u32le(bytes, 8), 0u);   // thiszone
    TA_CHECK_EQ(u32le(bytes, 12), 0u);  // sigfigs
    TA_CHECK_EQ(u32le(bytes, 16), 0xFFFFu);  // snaplen
    TA_CHECK_EQ(u32le(bytes, 20), 101u);   // LINKTYPE_RAW
}

TA_TEST(pcap_write_records_roundtrip) {
    const std::string path = "/tmp/ta_pcap_test_records.pcap";
    std::remove(path.c_str());
    auto w = traffic::PcapWriter::open(path);
    std::vector<uint8_t> pkt1 = {0x45, 0x00, 0x00, 0x28, 0x11, 0x22, 0x33, 0x44};
    std::vector<uint8_t> pkt2(64, 0xAB);
    TA_CHECK(w->writePacket(pkt1.data(), pkt1.size(), 1700000000123ull) ==
             traffic::PcapWriteStatus::Ok);
    TA_CHECK(w->writePacket(pkt2.data(), pkt2.size(), 1700000000999ull) ==
             traffic::PcapWriteStatus::Ok);
    TA_CHECK_EQ(w->packetsWritten(), 2u);
    w->close();

    const auto bytes = readFile(path);
    // 24 global + 16 + 8 + 16 + 64
    TA_CHECK_EQ(bytes.size(), 24u + 16u + 8u + 16u + 64u);

    // Record 1: ts 1700000000.123000
    TA_CHECK_EQ(u32le(bytes, 24), 1700000000u);
    TA_CHECK_EQ(u32le(bytes, 28), 123000u);
    TA_CHECK_EQ(u32le(bytes, 32), 8u);   // captured
    TA_CHECK_EQ(u32le(bytes, 36), 8u);   // original
    TA_CHECK_EQ(std::memcmp(bytes.data() + 40, pkt1.data(), pkt1.size()), 0);

    // Record 2: ts 1700000000.999000
    size_t off = 24 + 16 + 8;
    TA_CHECK_EQ(u32le(bytes, off), 1700000000u);
    TA_CHECK_EQ(u32le(bytes, off + 4), 999000u);
    TA_CHECK_EQ(u32le(bytes, off + 8), 64u);
    TA_CHECK_EQ(bytes[off + 16], 0xAB);
}

TA_TEST(pcap_write_snaplen_clipping) {
    const std::string path = "/tmp/ta_pcap_test_clip.pcap";
    std::remove(path.c_str());
    auto w = traffic::PcapWriter::open(path, 16);  // tiny snaplen
    std::vector<uint8_t> big(100, 0x42);
    TA_CHECK(w->writePacket(big.data(), big.size(), 5) == traffic::PcapWriteStatus::Ok);
    w->close();

    const auto bytes = readFile(path);
    TA_CHECK_EQ(bytes.size(), 24u + 16u + 16u);
    TA_CHECK_EQ(u32le(bytes, 24 + 8), 16u);    // captured clipped
    TA_CHECK_EQ(u32le(bytes, 24 + 12), 100u);  // original preserved
    TA_CHECK_EQ(bytes[24 + 16], 0x42);
    TA_CHECK_EQ(bytes.back(), 0x42);
}

TA_TEST(pcap_write_zero_length_packet) {
    const std::string path = "/tmp/ta_pcap_test_zero.pcap";
    std::remove(path.c_str());
    auto w = traffic::PcapWriter::open(path);
    TA_CHECK(w->writePacket(nullptr, 0, 1000) == traffic::PcapWriteStatus::Ok);
    TA_CHECK_EQ(w->packetsWritten(), 1u);
    w->close();

    const auto bytes = readFile(path);
    TA_CHECK_EQ(bytes.size(), 24u + 16u);
    TA_CHECK_EQ(u32le(bytes, 24), 1u);   // 1000 ms -> sec 1
    TA_CHECK_EQ(u32le(bytes, 28), 0u);   // usec 0
    TA_CHECK_EQ(u32le(bytes, 32), 0u);   // captured len 0
    TA_CHECK_EQ(u32le(bytes, 36), 0u);   // original len 0
}

TA_TEST(pcap_write_after_close_rejected) {
    const std::string path = "/tmp/ta_pcap_test_closed.pcap";
    std::remove(path.c_str());
    auto w = traffic::PcapWriter::open(path);
    w->close();
    uint8_t one = 1;
    TA_CHECK(w->writePacket(&one, 1, 0) == traffic::PcapWriteStatus::NotOpen);
    TA_CHECK(w->flush() == traffic::PcapWriteStatus::NotOpen);
    // Double close is idempotent.
    w->close();
}

TA_TEST(pcap_write_unwritable_path) {
    auto w = traffic::PcapWriter::open("/nonexistent-dir/ta/definitely/missing.pcap");
    TA_CHECK(w == nullptr);
}

TA_TEST(pcap_write_flush_keeps_file_open) {
    const std::string path = "/tmp/ta_pcap_test_flush.pcap";
    std::remove(path.c_str());
    auto w = traffic::PcapWriter::open(path);
    std::vector<uint8_t> pkt = {0x45, 0x00};
    TA_CHECK(w->writePacket(pkt.data(), pkt.size(), 1) == traffic::PcapWriteStatus::Ok);
    TA_CHECK(w->flush() == traffic::PcapWriteStatus::Ok);
    TA_CHECK(w->isOpen());
    // File already visible with flushed content before close.
    const auto bytes = readFile(path);
    TA_CHECK_EQ(bytes.size(), 24u + 16u + 2u);
    w->close();
}

}  // namespace
