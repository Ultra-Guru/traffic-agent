#include "traffic/ja4.h"

#include <algorithm>
#include <cstdio>

#include "traffic/sha256.h"

namespace traffic {

bool isGrease(uint16_t value) {
    const uint8_t hi = static_cast<uint8_t>(value >> 8);
    const uint8_t lo = static_cast<uint8_t>(value & 0xff);
    // GREASE values repeat both nibbles: 0x0a0a, 0x1a1a, ..., 0xfafa.
    return hi == lo && (hi & 0x0fu) == 0x0au;  // MUT:!=
}

namespace {

// 2 lowercase hex digits, values 0..255 ("00".."ff").
std::string hex2(size_t value) {
    char buf[3];
    std::snprintf(buf, sizeof(buf), "%02zx", value);
    return std::string(buf);
}

// Sorted, de-duplicated, GREASE-free copy of the input.
std::vector<uint16_t> sanitized(std::vector<uint16_t> in) {
    std::vector<uint16_t> out;
    for (uint16_t v : in) {
        if (!isGrease(v)) out.push_back(v);
    }
    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());
    return out;
}

// sha256("v1,v2,v3") truncated to the first 12 lowercase hex chars.
std::string truncatedHash(const std::vector<uint16_t>& values) {
    std::string joined;
    for (size_t i = 0; i < values.size(); ++i) {
        if (i > 0) joined.push_back(',');
        joined += std::to_string(values[i]);
    }
    return sha256Hex(reinterpret_cast<const uint8_t*>(joined.data()), joined.size())
        .substr(0, 12);
}

// The TLS version used by JA4 part A: the highest supported_versions entry
// (extension 43) when present, otherwise the legacy client_version. Reported
// as 2 chars per the JA4 spec (SSL 3.0 -> "30", TLS 1.0..1.3 -> "10".."13").
std::string versionChars(const ClientHelloInfo& hello) {
    uint16_t version = hello.clientVersion;
    for (uint16_t v : hello.supportedVersions) {
        if (v > version) version = v;  // MUT:<
    }
    switch (version) {
        case 0x0300: return "30";
        case 0x0301: return "10";
        case 0x0302: return "11";
        case 0x0303: return "12";
        case 0x0304: return "13";
        default: return "00";
    }
}

}  // namespace

Ja4Fingerprint computeJa4(const ClientHelloInfo& hello, bool quic) {
    Ja4Fingerprint fp;

    // Part A: proto, version, sni-mode, cipher count, extension count, ALPN.
    std::string a;
    a.push_back(quic ? 'q' : 't');
    a += versionChars(hello);
    a.push_back(hello.sni.empty() ? 'i' : 'd');

    std::vector<uint16_t> ciphers = sanitized(hello.cipherSuites);
    std::vector<uint16_t> exts;
    for (const TlsExtension& e : hello.extensions) {
        // SNI (0) and ALPN (16) are excluded from the extension hash but
        // still counted in the extension count per the JA4 spec.
        if (isGrease(e.type)) continue;
        exts.push_back(e.type);
    }
    std::sort(exts.begin(), exts.end());
    exts.erase(std::unique(exts.begin(), exts.end()), exts.end());

    a += hex2(ciphers.size());
    a += hex2(exts.size());
    std::string alpn = "-";
    if (!hello.alpn.empty()) {
        alpn = hello.alpn.front();
        for (char& c : alpn) {
            if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
        }
    }
    a += alpn;
    fp.partA = a;

    fp.cipherHash = truncatedHash(ciphers);

    std::vector<uint16_t> hashExts;
    for (uint16_t t : exts) {
        if (t == 0 || t == 16) continue;  // SNI / ALPN excluded from the hash
        hashExts.push_back(t);
    }
    fp.extensionHash = truncatedHash(hashExts);

    fp.full = fp.partA + "_" + fp.cipherHash + "_" + fp.extensionHash;
    return fp;
}

}  // namespace traffic
