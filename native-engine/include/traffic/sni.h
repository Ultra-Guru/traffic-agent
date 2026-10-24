#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace traffic {

struct TlsSniResult {
    std::string sni;
    uint16_t recordVersion = 0;  // e.g. 0x0301 for TLS 1.0 record layer
    uint16_t handshakeSize = 0;
};

enum class SniStatus { Ok, TooShort, NotHandshake, NotClientHello, SniNotFound, Malformed };

// Walks TLS record -> ClientHello -> extensions and extracts the SNI host_name.
SniStatus parseTlsClientHelloSni(const uint8_t* data, size_t len, TlsSniResult* out);

}  // namespace traffic
