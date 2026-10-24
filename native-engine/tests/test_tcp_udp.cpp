#include "traffic/tcp.h"
#include "traffic/udp.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(tcp_parses_basic_header) {
    auto seg = tb::tcpSegment(1000, TcpHeader::kPsh | TcpHeader::kAck, {1, 2, 3});
    TcpHeader t{};
    TA_CHECK_EQ(parseTcp(seg.data(), seg.size(), &t), TcpStatus::Ok);
    TA_CHECK_EQ(t.srcPort, 12345);
    TA_CHECK_EQ(t.dstPort, 80);
    TA_CHECK_EQ(t.seq, 1000u);
    TA_CHECK(t.has(TcpHeader::kAck));
    TA_CHECK(t.has(TcpHeader::kPsh));
    TA_CHECK(!t.has(TcpHeader::kSyn));
    TA_CHECK_EQ(t.headerLengthBytes(), 20);
    TA_CHECK_EQ(tcpPayloadOffset(t), static_cast<size_t>(20));
}

TA_TEST(tcp_rejects_short_segment) {
    Bytes b(19, 0);
    TcpHeader t{};
    TA_CHECK_EQ(parseTcp(b.data(), b.size(), &t), TcpStatus::TooShort);
}

TA_TEST(tcp_rejects_bad_data_offset) {
    auto seg = tb::tcpSegment(0, 0);
    seg[12] = 0x40;  // data offset 4
    TcpHeader t{};
    TA_CHECK_EQ(parseTcp(seg.data(), seg.size(), &t), TcpStatus::BadOffset);
}

TA_TEST(udp_parses_basic_datagram) {
    auto d = tb::udpDatagram(5353, 443, {0xC0, 0x00});
    UdpHeader u{};
    TA_CHECK_EQ(parseUdp(d.data(), d.size(), &u), UdpStatus::Ok);
    TA_CHECK_EQ(u.srcPort, 5353);
    TA_CHECK_EQ(u.dstPort, 443);
    TA_CHECK_EQ(u.length, 10);
}

TA_TEST(udp_rejects_short_and_bad_length) {
    Bytes b(7, 0);
    UdpHeader u{};
    TA_CHECK_EQ(parseUdp(b.data(), b.size(), &u), UdpStatus::TooShort);
    Bytes c(8, 0);
    c[4] = 0; c[5] = 7;  // length field 7 < 8
    TA_CHECK_EQ(parseUdp(c.data(), c.size(), &u), UdpStatus::BadLength);
}

TA_TEST(udp_accepts_header_only_length_field) {
    Bytes b(8, 0);
    b[4] = 0; b[5] = 8;  // length field exactly 8
    UdpHeader u{};
    TA_CHECK_EQ(parseUdp(b.data(), b.size(), &u), UdpStatus::Ok);
    TA_CHECK_EQ(u.length, 8);
}
