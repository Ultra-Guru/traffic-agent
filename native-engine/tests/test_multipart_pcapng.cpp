#include "traffic/multipart.h"
#include "traffic/pcapng.h"

#include <string>
#include <vector>

#include "test_framework.hpp"

using namespace traffic;

namespace {

std::vector<uint8_t> strB(const std::string& s) { return std::vector<uint8_t>(s.begin(), s.end()); }

std::string toStr(const std::vector<uint8_t>& b) { return std::string(b.begin(), b.end()); }

}  // namespace

// ---------------- multipart ----------------

TA_TEST(multipart_two_fields_and_a_file) {
    std::string body =
        "--BOUND\r\n"
        "Content-Disposition: form-data; name=\"field1\"\r\n"
        "\r\n"
        "value1\r\n"
        "--BOUND\r\n"
        "Content-Disposition: form-data; name=\"upload\"; filename=\"a.txt\"\r\n"
        "Content-Type: text/plain\r\n"
        "\r\n"
        "file content here\r\n"
        "--BOUND--\r\n";
    std::vector<MultipartPart> parts;
    TA_CHECK_EQ(
        parseMultipart(strB(body).data(), body.size(),
                       "multipart/form-data; boundary=BOUND", &parts),
        MultipartStatus::Ok);
    TA_CHECK_EQ(parts.size(), static_cast<size_t>(2));
    TA_CHECK_ST(parts[0].name, "field1");
    TA_CHECK_ST(parts[0].filename, "");
    TA_CHECK_ST(toStr(parts[0].body), "value1");
    TA_CHECK_ST(parts[1].name, "upload");
    TA_CHECK_ST(parts[1].filename, "a.txt");
    TA_CHECK_ST(parts[1].contentType, "text/plain");
    TA_CHECK_ST(toStr(parts[1].body), "file content here");
}

TA_TEST(multipart_quoted_boundary_and_lf_lines) {
    std::string body =
        "--qBoUnDaRy\n"
        "Content-Disposition: form-data; name=k\n"
        "\n"
        "v\n"
        "--qBoUnDaRy--\n";
    std::vector<MultipartPart> parts;
    TA_CHECK_EQ(parseMultipart(strB(body).data(), body.size(),
                               "multipart/form-data; boundary=\"qBoUnDaRy\"", &parts),
                MultipartStatus::Ok);
    TA_CHECK_EQ(parts.size(), static_cast<size_t>(1));
    TA_CHECK_ST(parts[0].name, "k");
    TA_CHECK_ST(toStr(parts[0].body), "v");
}

TA_TEST(multipart_binary_body_bytes_preserved) {
    std::string body;
    body += "--B\r\nContent-Disposition: form-data; name=f\r\n\r\n";
    body += std::string("\x00\x01\x02\xFF\xFE", 5);
    body += "\r\n--B--\r\n";
    std::vector<MultipartPart> parts;
    TA_CHECK_EQ(parseMultipart(strB(body).data(), body.size(), "multipart/form-data; boundary=B",
                               &parts),
               MultipartStatus::Ok);
    TA_CHECK_EQ(parts.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(parts[0].body.size(), static_cast<size_t>(5));
    TA_CHECK_EQ(parts[0].body[0], 0x00);
    TA_CHECK_EQ(parts[0].body[3], 0xFF);
}

TA_TEST(multipart_missing_boundary_param) {
    std::vector<MultipartPart> parts;
    std::string body = "--x\r\n\r\n\r\n--x--\r\n";
    TA_CHECK_EQ(parseMultipart(strB(body).data(), body.size(), "multipart/form-data", &parts),
                MultipartStatus::NoBoundary);
}

TA_TEST(multipart_no_final_terminator_rejected) {
    std::string body = "--B\r\nContent-Disposition: form-data; name=f\r\n\r\nv\r\n";
    std::vector<MultipartPart> parts;
    TA_CHECK_EQ(parseMultipart(strB(body).data(), body.size(), "multipart/form-data; boundary=B",
                               &parts),
               MultipartStatus::Malformed);
}

// ---------------- pcapng ----------------

namespace {

void putU16le(std::vector<uint8_t>& b, uint16_t v) {
    b.push_back(static_cast<uint8_t>(v & 0xFF));
    b.push_back(static_cast<uint8_t>(v >> 8));
}
void putU32le(std::vector<uint8_t>& b, uint32_t v) {
    b.push_back(static_cast<uint8_t>(v & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 16) & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 24) & 0xFF));
}
void putU32be(std::vector<uint8_t>& b, uint32_t v) {
    b.push_back(static_cast<uint8_t>((v >> 24) & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 16) & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

std::vector<uint8_t> shbLe() {
    std::vector<uint8_t> f;
    putU32le(f, 0x0A0D0D0A);  // SHB block type
    putU32le(f, 28);          // total length
    putU32le(f, 0x1A2B3C4D);  // byte-order magic (LE bytes: 4D 3C 2B 1A)
    putU16le(f, 1);           // major
    putU16le(f, 0);           // minor
    for (int i = 0; i < 8; ++i) f.push_back(0xFF);  // section length = -1
    putU32le(f, 28);          // trailing length
    return f;
}

std::vector<uint8_t> idbLe(uint8_t tsresol) {
    std::vector<uint8_t> f;
    putU32le(f, 1);  // IDB type
    putU32le(f, 28);
    putU16le(f, 1);  // link type ethernet
    putU16le(f, 0);  // reserved
    putU32le(f, 0);  // snaplen
    putU16le(f, 9);  // option: if_tsresol
    putU16le(f, 1);
    f.push_back(tsresol);
    f.push_back(0);
    f.push_back(0);
    f.push_back(0);  // pad option value to 4 bytes
    putU32le(f, 28);
    return f;
}

std::vector<uint8_t> epbLe(const std::vector<uint8_t>& packet, uint32_t tsHi, uint32_t tsLo,
                           uint32_t ifid) {
    std::vector<uint8_t> f;
    uint32_t total = 32 + static_cast<uint32_t>(packet.size()) +
                     static_cast<uint32_t>((4 - (packet.size() % 4)) % 4);
    putU32le(f, 6);
    putU32le(f, total);
    putU32le(f, ifid);
    putU32le(f, tsHi);
    putU32le(f, tsLo);
    putU32le(f, static_cast<uint32_t>(packet.size()));
    putU32le(f, static_cast<uint32_t>(packet.size()));
    f.insert(f.end(), packet.begin(), packet.end());
    size_t pad = (4 - (packet.size() % 4)) % 4;
    for (size_t i = 0; i < pad; ++i) f.push_back(0);
    putU32le(f, total);
    return f;
}

}  // namespace

TA_TEST(pcapng_parses_shb_idb_epb_microseconds) {
    std::vector<uint8_t> pkt = {'h', 'e', 'l', 'l', 'o'};
    auto f = shbLe();
    auto idb = idbLe(6);  // us
    // tick count = 1700000000 s + 1.5 s in microseconds, split hi/lo
    uint64_t us = 1700000000ULL * 1000000ULL + 1500000ULL;
    auto epb = epbLe(pkt, static_cast<uint32_t>(us >> 32), static_cast<uint32_t>(us & 0xFFFFFFFFu), 0);
    f.insert(f.end(), idb.begin(), idb.end());
    f.insert(f.end(), epb.begin(), epb.end());
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(recs[0].interfaceId, 0u);
    TA_CHECK_EQ(recs[0].timestampNs, us * 1000ULL);
    TA_CHECK_EQ(recs[0].data.size(), pkt.size());
    TA_CHECK(recs[0].data == pkt);
}

TA_TEST(pcapng_nanosecond_resolution) {
    std::vector<uint8_t> pkt = {1, 2, 3, 4};
    auto f = shbLe();
    auto idb = idbLe(9);  // ns
    auto epb = epbLe(pkt, 0u, 123456789u, 0);
    f.insert(f.end(), idb.begin(), idb.end());
    f.insert(f.end(), epb.begin(), epb.end());
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(recs[0].timestampNs, 123456789u);
}

TA_TEST(pcapng_skips_unknown_blocks) {
    std::vector<uint8_t> pkt = {'a', 'b', 'c', 'd'};
    auto f = shbLe();
    // unknown block type 0x0BAD between SHB and IDB
    std::vector<uint8_t> unknown;
    putU32le(unknown, 0x0BAD);
    putU32le(unknown, 20);
    unknown.insert(unknown.end(), {1, 2, 3, 4, 5, 6, 7, 8});
    putU32le(unknown, 20);
    auto idb = idbLe(6);
    auto epb = epbLe(pkt, 1, 2, 0);
    f.insert(f.end(), unknown.begin(), unknown.end());
    f.insert(f.end(), idb.begin(), idb.end());
    f.insert(f.end(), epb.begin(), epb.end());
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(recs[0].data.size(), pkt.size());
}

TA_TEST(pcapng_simple_packet_block) {
    auto f = shbLe();
    std::vector<uint8_t> pkt = {'p', 'a', 'y'};
    std::vector<uint8_t> spb;
    putU32le(spb, 3);  // SPB type
    putU32le(spb, 20);
    putU32le(spb, 3);  // original length
    spb.insert(spb.end(), pkt.begin(), pkt.end());
    spb.push_back(0);  // pad
    putU32le(spb, 20);
    f.insert(f.end(), spb.begin(), spb.end());
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(recs[0].data.size(), static_cast<size_t>(3));
    TA_CHECK_EQ(recs[0].timestampNs, 0u);
}

TA_TEST(pcapng_rejects_bad_magic) {
    std::vector<uint8_t> f;
    putU32le(f, 0xDEADBEEF);
    putU32le(f, 28);
    putU32le(f, 0x1A2B3C4D);
    while (f.size() < 28) f.push_back(0);
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::BadByteOrderMagic);
    std::vector<uint8_t> empty;
    TA_CHECK_EQ(parsePcapng(empty.data(), empty.size(), &recs), PcapngStatus::TooShort);
}

TA_TEST(pcapng_rejects_inconsistent_block_length) {
    std::vector<uint8_t> pkt = {1, 2, 3, 4};
    auto f = shbLe();
    auto epb = epbLe(pkt, 0, 0, 0);
    f.insert(f.end(), epb.begin(), epb.end());
    // corrupt the EPB trailing length (last 4 bytes of the file)
    size_t last = f.size() - 4;
    f[last] = 0xFF;
    f[last + 1] = 0xFF;
    f[last + 2] = 0xFF;
    f[last + 3] = 0xFF;
    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::BadBlockLength);
}

TA_TEST(pcapng_big_endian_section) {
    std::vector<uint8_t> f;
    putU32be(f, 0x0A0D0D0A);
    putU32be(f, 28);
    putU32be(f, 0x1A2B3C4D);  // BE byte-order magic: bytes are 1A 2B 3C 4D
    f.push_back(0);
    f.push_back(1);  // major
    f.push_back(0);
    f.push_back(0);  // minor
    for (int i = 0; i < 8; ++i) f.push_back(0xFF);  // section length
    putU32be(f, 28);
    // IDB big-endian, no options: total 20
    putU32be(f, 1);
    putU32be(f, 20);
    f.push_back(0);
    f.push_back(1);  // link type ethernet
    f.push_back(0);
    f.push_back(0);  // reserved
    putU32be(f, 0);  // snaplen
    putU32be(f, 20);
    // EPB big-endian with a 4-byte packet: total 32+4 = 36
    std::vector<uint8_t> pkt = {9, 9, 9, 9};
    putU32be(f, 6);
    putU32be(f, 36);
    putU32be(f, 0);  // iface
    putU32be(f, 2);  // ts high
    putU32be(f, 5000000u);  // ts low (us)
    putU32be(f, 4);  // captured len
    putU32be(f, 4);  // original len
    f.insert(f.end(), pkt.begin(), pkt.end());
    putU32be(f, 36);

    std::vector<PcapngRecord> recs;
    TA_CHECK_EQ(parsePcapng(f.data(), f.size(), &recs), PcapngStatus::Ok);
    TA_CHECK_EQ(recs.size(), static_cast<size_t>(1));
    // BE u32 reads: tsHi=2, tsLo=5,000,000 us -> ns
    TA_CHECK_EQ(recs[0].timestampNs, (2ull * 4294967296ull + 5000000ull) * 1000ull);
    TA_CHECK(recs[0].data == pkt);
}
