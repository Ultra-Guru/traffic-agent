#include "traffic/sni.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(sni_extracts_host_name) {
    auto hello = tb::clientHello("api.example.com");
    TlsSniResult r{};
    TA_CHECK_EQ(parseTlsClientHelloSni(hello.data(), hello.size(), &r),
                SniStatus::Ok);
    TA_CHECK_ST(r.sni, "api.example.com");
    TA_CHECK_EQ(r.recordVersion, 0x0301);
}

TA_TEST(sni_rejects_non_handshake) {
    auto hello = tb::clientHello("x.com");
    hello[0] = 0x17;  // application data
    TlsSniResult r{};
    TA_CHECK_EQ(parseTlsClientHelloSni(hello.data(), hello.size(), &r),
                SniStatus::NotHandshake);
}

TA_TEST(sni_rejects_non_client_hello) {
    auto hello = tb::clientHello("x.com");
    hello[5] = 0x02;  // server hello
    TlsSniResult r{};
    TA_CHECK_EQ(parseTlsClientHelloSni(hello.data(), hello.size(), &r),
                SniStatus::NotClientHello);
}

TA_TEST(sni_handles_truncated_input) {
    auto hello = tb::clientHello("example.org");
    TlsSniResult r{};
    TA_CHECK_EQ(parseTlsClientHelloSni(hello.data(), 4, &r), SniStatus::TooShort);
    TA_CHECK_EQ(parseTlsClientHelloSni(hello.data(), 5, &r), SniStatus::TooShort);
}

TA_TEST(sni_six_bytes_reports_malformed) {
    // 5-byte record header + handshake type byte: passes the length and type
    // checks, but the ClientHello body is missing -> Malformed.
    auto hello = tb::clientHello("example.org");
    TlsSniResult r{};
    TA_CHECK_EQ(parseTlsClientHelloSni(hello.data(), 6, &r), SniStatus::Malformed);
}
