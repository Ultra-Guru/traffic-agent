#include "traffic/ja4.h"
#include "traffic/sha256.h"
#include "traffic/tls.h"

#include <cstring>

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

// Python cross-validation for the clientHelloFull() shape (sorted lists):
//   ciphers  = "255,4865,4866,49195,49199"               -> 6f1267d6a49b
//   exts     = "10,11,13,43" (SNI 0 / ALPN 16 dropped) -> 561b5c1e0392
//   hashlib.sha256(b"255,4865,4866,49195,49199").hexdigest()[:12]
const char* kFullJa4 = "t13d0506h2_6f1267d6a49b_561b5c1e0392";
const char* kFullJa4Quic = "q13d0506h2_6f1267d6a49b_561b5c1e0392";

}  // namespace

TA_TEST(ja4_full_client_hello) {
    auto hello = clientHelloFull("api.example.com");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);
    Ja4Fingerprint fp = computeJa4(chi, false);
    TA_CHECK_ST(fp.full, kFullJa4);
    TA_CHECK_ST(fp.partA, "t13d0506h2");
    TA_CHECK_ST(fp.cipherHash, "6f1267d6a49b");
    TA_CHECK_ST(fp.extensionHash, "561b5c1e0392");
}

TA_TEST(ja4_quic_transport_char) {
    auto hello = clientHelloFull("quic.example.com");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);
    Ja4Fingerprint fp = computeJa4(chi, true);
    TA_CHECK_ST(fp.full, kFullJa4Quic);
    // Only the leading transport char differs from the TCP variant.
    TA_CHECK(fp.partA[0] == 'q');
    TA_CHECK(fp.partA[1] == '1');  // version "13" follows
}

TA_TEST(ja4_grease_is_removed) {
    auto hello = clientHelloFull("greased.example.com");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);

    // Splice GREASE values into both lists post-parse: the fingerprint must
    // be identical (GREASE never contributes to counts, order or hashes).
    Ja4Fingerprint clean = computeJa4(chi, false);
    chi.cipherSuites.insert(chi.cipherSuites.begin(), 0x0a0a);
    chi.cipherSuites.push_back(0x1a1a);
    TlsExtension greaseExt{0x2a2a, 0};
    chi.extensions.push_back(greaseExt);
    Ja4Fingerprint greased = computeJa4(chi, false);
    TA_CHECK_ST(greased.full, clean.full);
}

TA_TEST(ja4_grease_detector) {
    TA_CHECK(isGrease(0x0a0a));
    TA_CHECK(isGrease(0xfafa));
    TA_CHECK(isGrease(0x1a1a));
    TA_CHECK(!isGrease(0x1301));
    TA_CHECK(!isGrease(0x0a0b));
    TA_CHECK(!isGrease(0x0b0a));
    TA_CHECK(!isGrease(0x00ff));
}

TA_TEST(ja4_no_sni_reports_ip_mode) {
    // Build a hello with no SNI at all by hand: ciphers 1301 only.
    Bytes body;
    pushU16(body, 0x0303);
    body.insert(body.end(), 32, 0xEE);
    body.push_back(0);  // session id
    pushU16(body, 2);
    pushU16(body, 0x1301);
    body.push_back(1);
    body.push_back(0);
    pushU16(body, 0);  // zero-length extensions

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
    Ja4Fingerprint fp = computeJa4(chi, false);
    // No SNI -> 'i', no ALPN -> '-', no extensions -> "00" count and the
    // empty-string hash (sha256("")[:12] = e3b0c44298fc).
    TA_CHECK_ST(fp.partA, "t12i0100-");
    TA_CHECK_ST(fp.cipherHash, sha256Hex(reinterpret_cast<const uint8_t*>("4865"), 4)
                                   .substr(0, 12));
    TA_CHECK_ST(fp.extensionHash, "e3b0c44298fc");
}

TA_TEST(ja4_version_uses_supported_versions_max) {
    auto hello = clientHelloFull("ver.example.com");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);
    // client_version is 0x0303 but supported_versions offers 0x0304: JA4
    // must report "13" (the max), not "12".
    TA_CHECK(chi.clientVersion == 0x0303);
    TA_CHECK(chi.supportedVersions.size() == 2);
    Ja4Fingerprint fp = computeJa4(chi, false);
    TA_CHECK(fp.partA.rfind("t13d", 0) == 0);
}

TA_TEST(ja4_counts_are_deduplicated) {
    auto hello = clientHelloFull("dup.example.com");
    ClientHelloInfo chi{};
    TA_CHECK_EQ(parseTlsClientHello(hello.data(), hello.size(), &chi), TlsStatus::Ok);
    // Duplicate a real (non-GREASE) extension and cipher: the count in partA
    // must not grow because JA4 sorts and de-duplicates.
    Ja4Fingerprint clean = computeJa4(chi, false);
    chi.extensions.push_back(TlsExtension{0x000B, 0});
    chi.cipherSuites.push_back(0x1301);
    Ja4Fingerprint dup = computeJa4(chi, false);
    TA_CHECK_ST(dup.partA, clean.partA);
    TA_CHECK_ST(dup.cipherHash, clean.cipherHash);
    TA_CHECK_ST(dup.extensionHash, clean.extensionHash);
}
