#include "traffic/ip.h"

#include "test_framework.hpp"
#include "builders.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(ip_parses_minimal_header) {
    Bytes b(20, 0);
    b[0] = 0x45;  // v4, IHL 5
    b[2] = 0; b[3] = 40;  // total length 40
    b[8] = 64;
    b[9] = 6;  // TCP
    b[12] = 1; b[13] = 2; b[14] = 3; b[15] = 4;
    Ipv4Header h{};
    TA_CHECK_EQ(parseIpv4(b.data(), b.size(), &h), Ipv4Status::Ok);
    TA_CHECK_EQ(h.version, 4);
    TA_CHECK_EQ(h.ihl, 5);
    TA_CHECK_EQ(h.totalLength, 40);
    TA_CHECK_EQ(h.protocol, 6);
    TA_CHECK_EQ(h.srcAddr, 0x01020304u);
    TA_CHECK_EQ(h.headerLengthBytes(), 20);
}

TA_TEST(ip_rejects_short_buffer) {
    Bytes b(19, 0);
    b[0] = 0x45;
    Ipv4Header h{};
    TA_CHECK_EQ(parseIpv4(b.data(), b.size(), &h), Ipv4Status::TooShort);
    TA_CHECK_EQ(parseIpv4(nullptr, 40, &h), Ipv4Status::TooShort);
}

TA_TEST(ip_rejects_bad_version) {
    Bytes b(20, 0);
    b[0] = 0x65;  // version 6
    Ipv4Header h{};
    TA_CHECK_EQ(parseIpv4(b.data(), b.size(), &h), Ipv4Status::BadVersion);
}

TA_TEST(ip_rejects_bad_ihl) {
    Bytes b(20, 0);
    b[0] = 0x44;  // IHL 4 (< 5)
    Ipv4Header h{};
    TA_CHECK_EQ(parseIpv4(b.data(), b.size(), &h), Ipv4Status::BadIhl);
}

TA_TEST(ip_rejects_truncated_total_length) {
    Bytes b(24, 0);
    b[0] = 0x46;  // IHL 6 -> header 24 bytes
    b[2] = 0; b[3] = 20;  // total length 20 < 24
    Ipv4Header h{};
    TA_CHECK_EQ(parseIpv4(b.data(), b.size(), &h), Ipv4Status::Truncated);
}

TA_TEST(ip_payload_offset_respects_options) {
    Bytes b(25, 0);
    b[0] = 0x46;  // IHL 6, 24-byte header with options
    b[2] = 0; b[3] = 32;
    b[24] = 0xAA;
    const uint8_t* p = ipv4Payload(b.data(), b.size());
    TA_CHECK(p != nullptr);
    TA_CHECK_EQ(*p, 0xAA);
}

TA_TEST(ip_payload_null_for_invalid) {
    Bytes b(10, 0);
    TA_CHECK(ipv4Payload(b.data(), b.size()) == nullptr);
    TA_CHECK(ipv4Payload(nullptr, 40) == nullptr);
}

TA_TEST(ip_payload_null_when_header_consumes_everything) {
    // exactly 20 bytes: the IPv4 header fills the whole packet
    Bytes b(20, 0);
    b[0] = 0x45;
    b[2] = 0; b[3] = 20;  // total length 20
    TA_CHECK(ipv4Payload(b.data(), b.size()) == nullptr);
}
