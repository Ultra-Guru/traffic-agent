#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace traffic {

struct TlsExtension {
    uint16_t type = 0;
    uint16_t length = 0;
};

// Full ClientHello view used for JA3 fingerprinting and the detail panel.
struct ClientHelloInfo {
    uint16_t recordVersion = 0;               // record layer version
    uint16_t clientVersion = 0;               // legacy_version field
    std::string randomHex;                    // 64 hex chars
    std::string sessionIdHex;
    std::vector<uint16_t> cipherSuites;
    std::vector<uint8_t> compression;
    std::vector<TlsExtension> extensions;     // raw type/length walk
    std::string sni;                          // extension 0
    std::vector<std::string> alpn;            // extension 16
    std::vector<uint16_t> supportedVersions;  // extension 43
    std::vector<uint16_t> supportedGroups;    // extension 10
    std::vector<uint16_t> signatureAlgorithms;  // extension 13
    std::vector<uint8_t> ecPointFormats;      // extension 11
    std::string ja3;                          // raw JA3 string
    std::string ja3Md5;                       // md5(ja3) hex
};

struct ServerHelloInfo {
    uint16_t recordVersion = 0;
    uint16_t serverVersion = 0;
    uint16_t cipher = 0;
    std::string alpn;  // first negotiated protocol, "" when absent
};

enum class TlsStatus { Ok, TooShort, NotHandshake, NotClientHello, NotServerHello, Malformed };

// Walks record -> handshake -> ClientHello, enumerating every extension and
// computing the JA3 fingerprint "version,ciphers,extensions,groups,formats".
TlsStatus parseTlsClientHello(const uint8_t* data, size_t len, ClientHelloInfo* out);

// Walks record -> handshake -> ServerHello: version, cipher, ALPN.
TlsStatus parseTlsServerHello(const uint8_t* data, size_t len, ServerHelloInfo* out);

// IANA-style OpenSSL name for a cipher suite; unknown suites render as
// "0x%04x". Returns by value (thread-safe).
std::string tlsCipherName(uint16_t cipher);

// "SSL 3.0".."TLS 1.3"; unknown versions render as "0x%04x".
std::string tlsVersionName(uint16_t version);

}  // namespace traffic
