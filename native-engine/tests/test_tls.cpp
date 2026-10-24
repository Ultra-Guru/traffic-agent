#include "traffic/md5.h"
#include "traffic/tls.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

// JA3 known vector for the fixed clientHelloFull() shape. The md5 was
// cross-validated against python3 hashlib.md5:
//   python3 -c "import hashlib;print(hashlib.md5(b'771,4865-4866-49195-49199-255,0-11-10-13-16-43,29-23,0').hexdigest())"
const char* kExpectedJa3 = "771,4865-4866-49195-49199-255,0-11-10-13-16-43,29-23,0";
const char* kExpectedJa3Md5 = "21d2e3024b63e0bac86dd07f7fb8c2bf";

std::string strOf(const std::vector<uint8_t>& b) {
    return std::string(b.begin(), b.end());
}

}  // namespace

TA_TEST(tls_full_client_hello_fields) {
    auto hello = clientHelloFull("api.example.com");
    ClientHelloInfo chi{};
    TlsStatus s = parseTlsClientHello(hello.data(), hello.size(), &chi);
    TA_CHECK_EQ(s, TlsStatus::Ok);
    TA_CHECK_EQ(chi.recordVersion, 0x0301);
    TA_CHECK_EQ(chi.clientVersion, 0x0303);
    TA_CHECK_EQ(chi.randomHex.size(), static_cast<size_t>(64));
    TA_CHECK_ST(chi.randomHex.substr(0, 4), "cdcd");
    TA_CHECK_EQ(chi.sessionIdHex.size(), static_cast<size_t>(8));
    TA_CHECK_ST(chi.sessionIdHex, "9abcdef0");
    TA_CHECK_EQ(chi.cipherSuites.size(), static_cast<size_t>(5));
    TA_CHECK_EQ(chi.cipherSuites[0], 0x1301);
    TA_CHECK_EQ(chi.cipherSuites[4], 0x00FF);
    TA_CHECK_EQ(chi.compression.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(chi.compression[0], 0);
    TA_CHECK_ST(chi.sni, "api.example.com");
    TA_CHECK_EQ(chi.alpn.size(), static_cast<size_t>(2));
    TA_CHECK_ST(chi.alpn[0], "h2");
    TA_CHECK_ST(chi.alpn[1], "http/1.1");
    TA_CHECK_EQ(chi.supportedVersions.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(chi.supportedVersions[0], 0x0304);
    TA_CHECK_EQ(chi.supportedVersions[1], 0x0303);
    TA_CHECK_EQ(chi.supportedGroups.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(chi.supportedGroups[0], 29);   // x25519
    TA_CHECK_EQ(chi.supportedGroups[1], 23);   // secp256r1
    TA_CHECK_EQ(chi.signatureAlgorithms.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(chi.signatureAlgorithms[0], 0x0403);
    TA_CHECK_EQ(chi.signatureAlgorithms[1], 0x0804);
    TA_CHECK_EQ(chi.ecPointFormats.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(chi.ecPointFormats[0], 0);
    TA_CHECK_EQ(chi.extensions.size(), static_cast<size_t>(6));
    TA_CHECK_EQ(chi.extensions[0].type, 0);
    TA_CHECK_EQ(chi.extensions[1].type, 11);
    TA_CHECK_EQ(chi.extensions[2].type, 10);
    TA_CHECK_EQ(chi.extensions[3].type, 13);
    TA_CHECK_EQ(chi.extensions[4].type, 16);
    TA_CHECK_EQ(chi.extensions[5].type, 43);
}

TA_TEST(tls_ja3_known_vector) {
    auto hello = clientHelloFull("ja3.example.org");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);
    TA_CHECK_ST(chi.ja3, kExpectedJa3);
    TA_CHECK_ST(chi.ja3Md5, kExpectedJa3Md5);
    // ja3Md5 must equal md5Hex(ja3) for any successfully parsed hello.
    std::string self = md5Hex(reinterpret_cast<const uint8_t*>(chi.ja3.data()), chi.ja3.size());
    TA_CHECK_ST(chi.ja3Md5, self);
    // The SNI does not take part in the fingerprint.
    auto hello2 = clientHelloFull("other.example.net");
    ClientHelloInfo chi2{};
    TA_CHECK_EQ(parseTlsClientHello(hello2.data(), hello2.size(), &chi2), TlsStatus::Ok);
    TA_CHECK_ST(chi2.ja3Md5, chi.ja3Md5);
}

TA_TEST(tls_ja3_empty_segments_stay_empty) {
    // ClientHello without extensions/groups: ",,," must stay empty, not "0".
    Bytes body;
    pushU16(body, 0x0303);
    body.insert(body.end(), 32, 0);
    body.push_back(0);              // session id
    pushU16(body, 2);              // cipher suites length
    pushU16(body, 0x1301);
    body.push_back(1);             // compression length
    body.push_back(0);
    pushU16(body, 0);              // extensions length
    Bytes ch;
    ch.push_back(0x01);
    ch.push_back(0);
    ch.push_back(static_cast<uint8_t>((body.size() >> 8) & 0xFF));
    ch.push_back(static_cast<uint8_t>(body.size() & 0xFF));
    ch.insert(ch.end(), body.begin(), body.end());
    Bytes rec;
    rec.push_back(0x16);
    rec.push_back(0x03);
    rec.push_back(0x01);
    pushU16(rec, static_cast<uint16_t>(ch.size()));
    rec.insert(rec.end(), ch.begin(), ch.end());

    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(rec.data(), rec.size(), &chi), TlsStatus::Ok);
    TA_CHECK_ST(chi.ja3, "771,4865,,,");
    TA_CHECK_ST(chi.sni, "");
}

TA_TEST(tls_minimal_sni_hello_parses) {
    auto hello = clientHello("plain.example.io");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);
    TA_CHECK_ST(chi.sni, "plain.example.io");
    TA_CHECK_EQ(chi.cipherSuites.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(chi.extensions.size(), static_cast<size_t>(1));
    TA_CHECK_ST(chi.ja3, "771,4865,0,,");
}

TA_TEST(tls_rejects_garbage) {
    ClientHelloInfo chi{};
    Bytes bad = {0x16, 0x03};
    TA_CHECK_EQ(parseTlsClientHello(bad.data(), bad.size(), &chi), TlsStatus::TooShort);
    Bytes notTls = str("GET / HTTP/1.1\r\n\r\n");
    TA_CHECK_EQ(parseTlsClientHello(notTls.data(), notTls.size(), &chi),
                TlsStatus::NotHandshake);
    // ServerHello is not a ClientHello
    auto sh = serverHello(0x1301, "");
    TA_CHECK(parseTlsClientHello(sh.data(), sh.size(), &chi) != TlsStatus::Ok);
}

TA_TEST(tls_truncated_extension_is_rejected) {
    auto hello = clientHelloFull("cut.example.com");
    // Cut the record length so the record claims more than it has.
    hello[3] = 0xFF;
    ClientHelloInfo chi{};
    TA_CHECK(parseTlsClientHello(hello.data(), hello.size(), &chi) != TlsStatus::Ok);
    // Truncate the tail: half an extension list is malformed too.
    auto cut = Bytes(hello.begin(), hello.end() - 10);
    TA_CHECK(parseTlsClientHello(cut.data(), cut.size(), &chi) != TlsStatus::Ok);
}

TA_TEST(tls_server_hello_parse) {
    auto sh = serverHello(0x1302, "h2");
    ServerHelloInfo info{};
    TA_CHECK_EQ(parseTlsServerHello(sh.data(), sh.size(), &info), TlsStatus::Ok);
    TA_CHECK_EQ(info.recordVersion, 0x0303);
    TA_CHECK_EQ(info.serverVersion, 0x0303);
    TA_CHECK_EQ(info.cipher, 0x1302);
    TA_CHECK_ST(info.alpn, "h2");

    auto plain = serverHello(0x002F, "");
    ServerHelloInfo info2{};
    TA_CHECK_EQ(parseTlsServerHello(plain.data(), plain.size(), &info2), TlsStatus::Ok);
    TA_CHECK_EQ(info2.cipher, 0x002F);
    TA_CHECK_ST(info2.alpn, "");

    // A ClientHello is not a ServerHello.
    auto ch = clientHello("x.example.com");
    TA_CHECK(parseTlsServerHello(ch.data(), ch.size(), &info2) != TlsStatus::Ok);
}

TA_TEST(tls_cipher_names) {
    TA_CHECK_ST(tlsCipherName(0x1301), "TLS_AES_128_GCM_SHA256");
    TA_CHECK_ST(tlsCipherName(0x1302), "TLS_AES_256_GCM_SHA384");
    TA_CHECK_ST(tlsCipherName(0x1303), "TLS_CHACHA20_POLY1305_SHA256");
    TA_CHECK_ST(tlsCipherName(0xC030), "ECDHE-RSA-AES256-GCM-SHA384");
    TA_CHECK_ST(tlsCipherName(0xC02B), "ECDHE-ECDSA-AES128-GCM-SHA256");
    TA_CHECK_ST(tlsCipherName(0xCCA8), "ECDHE-RSA-CHACHA20-POLY1305");
    TA_CHECK_ST(tlsCipherName(0x009C), "AES256-GCM-SHA384");
    TA_CHECK_ST(tlsCipherName(0x009B), "AES128-GCM-SHA256");
    TA_CHECK_ST(tlsCipherName(0x002F), "AES128-SHA");
    TA_CHECK_ST(tlsCipherName(0x0035), "AES256-SHA");
    TA_CHECK_ST(tlsCipherName(0x000A), "DES-CBC3-SHA");
    TA_CHECK_ST(tlsCipherName(0xC013), "ECDHE-RSA-AES128-SHA");
    TA_CHECK_ST(tlsCipherName(0xC014), "ECDHE-RSA-AES256-SHA");
    TA_CHECK_ST(tlsCipherName(0x00FF), "TLS_EMPTY_RENEGOTIATION_INFO_SCSV");
    // unknown suite formats as 0x%04x
    TA_CHECK_ST(tlsCipherName(0x1234), "0x1234");
    // count coverage: at least 30 distinct known names
    int known = 0;
    for (uint32_t c = 0; c <= 0xFFFF; ++c) {
        std::string n = tlsCipherName(static_cast<uint16_t>(c));
        if (n.size() > 1 && n[0] != '0') ++known;
    }
    TA_CHECK(known >= 30);
}

TA_TEST(tls_version_names) {
    TA_CHECK_ST(tlsVersionName(0x0300), "SSLv3");
    TA_CHECK_ST(tlsVersionName(0x0301), "TLSv1.0");
    TA_CHECK_ST(tlsVersionName(0x0302), "TLSv1.1");
    TA_CHECK_ST(tlsVersionName(0x0303), "TLSv1.2");
    TA_CHECK_ST(tlsVersionName(0x0304), "TLSv1.3");
    TA_CHECK_ST(tlsVersionName(0x0002), "0x0002");
}
