#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "traffic/tls.h"

namespace traffic {

// JA4 fingerprint (FoxIO JA4 v1 spec) computed from a parsed ClientHello.
//
// Format:  <a>_<b>_<c>
//   a = "<proto><version><sni><cipher-count><ext-count>_<alpn>"
//        proto:   "t" (TCP/TLS), "q" (QUIC)
//        version: 2 hex chars of the max offered TLS version (e.g. "13")
//        sni:     "d" (DNS name present) or "i" (no SNI / IP literal)
//        counts:  2 hex chars each, after GREASE removal
//        alpn:    first offered ALPN lowercased, "-" when absent
//   b = first 12 hex chars of sha256(sorted comma-joined cipher list)
//   c = first 12 hex chars of sha256(sorted comma-joined extension list,
//       excluding SNI(0) and ALPN(16))
//
// Example: t13d1516h2_8daaf6152771_b0da82dd1658
struct Ja4Fingerprint {
    std::string partA;        // "t13d1516h2" (without underscores)
    std::string cipherHash;   // 12 hex chars
    std::string extensionHash;  // 12 hex chars
    std::string full;         // partA_cipherHash_extensionHash
};

// True when the 16-bit value is a TLS GREASE value (RFC 8701): the pattern
// 0x?a?a where every nibble is repeated (0x0a0a, 0x1a1a, ... 0xfafa).
bool isGrease(uint16_t value);

// Computes JA4 for a parsed ClientHello. `quic` selects the transport char
// ('q' instead of 't'), used for QUIC Initials carrying the same hello.
Ja4Fingerprint computeJa4(const ClientHelloInfo& hello, bool quic);

}  // namespace traffic
