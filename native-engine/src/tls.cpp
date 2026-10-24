#include "traffic/tls.h"

#include "traffic/md5.h"

#include <cstdio>

namespace traffic {

namespace {

bool readU16(const uint8_t* data, size_t len, size_t pos, uint16_t* out) {
    if (pos + 2 > len) return false;  // MUT:>=
    *out = static_cast<uint16_t>((data[pos] << 8) | data[pos + 1]);
    return true;
}

bool readU24(const uint8_t* data, size_t len, size_t pos, uint32_t* out) {
    if (pos + 3 > len) return false;
    *out = (static_cast<uint32_t>(data[pos]) << 16) | (static_cast<uint32_t>(data[pos + 1]) << 8) |
           data[pos + 2];
    return true;
}

void appendHex(std::string* out, const uint8_t* data, size_t len) {
    static const char* kDigits = "0123456789abcdef";
    for (size_t i = 0; i < len; ++i) {
        out->push_back(kDigits[data[i] >> 4]);
        out->push_back(kDigits[data[i] & 0x0Fu]);
    }
}

// Collects handshake message bodies across (possibly multiple) TLS records.
// Returns true when one handshake message of the wanted type was assembled
// completely into body.
bool assembleHandshake(const uint8_t* data, size_t len, uint8_t wantType,
                       std::vector<uint8_t>* body, uint16_t* recordVersion) {
    std::vector<uint8_t> all;   // bytes of the wanted message collected so far
    uint32_t wanted = 0;        // 0 == not started, else message body length
    size_t pos = 0;
    while (pos + 5 <= len) {
        if (data[pos] != 0x16) return false;  // only handshake records  // MUT:!=
        uint16_t ver = static_cast<uint16_t>((data[pos + 1] << 8) | data[pos + 2]);
        uint16_t rlen = static_cast<uint16_t>((data[pos + 3] << 8) | data[pos + 4]);
        if (recordVersion != nullptr) *recordVersion = ver;
        size_t payloadStart = pos + 5;
        if (payloadStart + rlen > len) return false;  // truncated record  // MUT:<
        const uint8_t* hs = data + payloadStart;
        size_t hsEnd = payloadStart + rlen;
        if (wanted == 0) {
            if (hsEnd < payloadStart + 4 || hs[0] != wantType) {  // MUT:!=
                pos = hsEnd;  // some other handshake message, keep scanning
                continue;
            }
            uint32_t hlen = 0;
            readU24(hs, hsEnd, 1, &hlen);
            size_t avail = hsEnd - (payloadStart + 4);
            if (avail >= hlen) {
                body->assign(hs + 4, hs + 4 + hlen);
                return true;
            }
            // message continues in the next record
            wanted = hlen;
            all.assign(hs + 4, data + hsEnd);
        } else {
            // continuation record: payload belongs to the wanted message
            size_t take = static_cast<size_t>(wanted) - all.size();
            if (take > rlen) take = rlen;
            all.insert(all.end(), hs, hs + take);
            if (all.size() >= wanted) {
                all.resize(wanted);
                *body = std::move(all);
                return true;
            }
        }
        pos = hsEnd;
    }
    return false;
}

// Splits an extension blob into (type, length) pairs and decodes the ones we
// care about. Returns false on structural violation.
bool decodeExtensions(const uint8_t* data, size_t len, ClientHelloInfo* out) {
    size_t p = 0;
    while (p + 4 <= len) {  // MUT:>
        uint16_t type = static_cast<uint16_t>((data[p] << 8) | data[p + 1]);
        uint16_t elen = static_cast<uint16_t>((data[p + 2] << 8) | data[p + 3]);
        size_t v = p + 4;
        if (v + elen > len) return false;  // MUT:>=
        TlsExtension ext;
        ext.type = type;
        ext.length = elen;
        out->extensions.push_back(ext);
        const uint8_t* d = data + v;
        size_t dlen = elen;
        if (type == 0x0000) {  // server_name
            uint16_t listLen = 0;
            if (!readU16(d, dlen, 0, &listLen)) return false;
            size_t q = 2;
            if (q >= dlen) return false;
            uint8_t nameType = d[q];
            if (nameType == 0) {  // host_name  // MUT:!=
                uint16_t nameLen = 0;
                if (!readU16(d, dlen, q + 1, &nameLen)) return false;
                if (q + 3 + nameLen > dlen) return false;  // MUT:>=
                out->sni.assign(reinterpret_cast<const char*>(d) + q + 3, nameLen);
            }
        } else if (type == 0x0010) {  // ALPN
            uint16_t listLen = 0;
            if (!readU16(d, dlen, 0, &listLen)) return false;
            size_t q = 2;
            while (q < dlen) {  // MUT:>=
                uint8_t plen = d[q];
                ++q;
                if (q + plen > dlen) return false;  // MUT:>=
                out->alpn.emplace_back(reinterpret_cast<const char*>(d) + q, plen);
                q += plen;
            }
        } else if (type == 0x002B) {  // supported_versions
            if (dlen < 1) return false;
            uint8_t listLen = d[0];
            size_t q = 1;
            if (q + listLen > dlen) return false;  // MUT:>
            for (uint8_t i = 0; i + 1 < listLen; i += 2) {
                out->supportedVersions.push_back(
                    static_cast<uint16_t>((d[q + i] << 8) | d[q + i + 1]));
            }
        } else if (type == 0x000A) {  // supported_groups
            uint16_t listLen = 0;
            if (!readU16(d, dlen, 0, &listLen)) return false;
            size_t q = 2;
            if (q + listLen > dlen) return false;  // MUT:>
            for (uint16_t i = 0; i + 1 < listLen; i += 2) {
                out->supportedGroups.push_back(
                    static_cast<uint16_t>((d[q + i] << 8) | d[q + i + 1]));
            }
        } else if (type == 0x000D) {  // signature_algorithms
            uint16_t listLen = 0;
            if (!readU16(d, dlen, 0, &listLen)) return false;
            size_t q = 2;
            if (q + listLen > dlen) return false;  // MUT:>
            for (uint16_t i = 0; i + 1 < listLen; i += 2) {
                out->signatureAlgorithms.push_back(
                    static_cast<uint16_t>((d[q + i] << 8) | d[q + i + 1]));
            }
        } else if (type == 0x000B) {  // ec_point_formats
            if (dlen < 1) return false;
            uint8_t listLen = d[0];
            size_t q = 1;
            if (q + listLen > dlen) return false;  // MUT:>
            for (uint8_t i = 0; i < listLen; ++i) {
                out->ecPointFormats.push_back(d[q + i]);
            }
        }
        p = v + elen;
    }
    return true;
}

void buildJa3(ClientHelloInfo* out) {
    std::string ja3;
    ja3 += std::to_string(out->clientVersion);
    ja3.push_back(',');
    for (size_t i = 0; i < out->cipherSuites.size(); ++i) {
        if (i > 0) ja3.push_back('-');
        ja3 += std::to_string(out->cipherSuites[i]);
    }
    ja3.push_back(',');
    for (size_t i = 0; i < out->extensions.size(); ++i) {
        if (i > 0) ja3.push_back('-');
        ja3 += std::to_string(out->extensions[i].type);
    }
    ja3.push_back(',');
    for (size_t i = 0; i < out->supportedGroups.size(); ++i) {
        if (i > 0) ja3.push_back('-');
        ja3 += std::to_string(out->supportedGroups[i]);
    }
    ja3.push_back(',');
    for (size_t i = 0; i < out->ecPointFormats.size(); ++i) {
        if (i > 0) ja3.push_back('-');
        ja3 += std::to_string(out->ecPointFormats[i]);
    }
    out->ja3 = ja3;
    out->ja3Md5 = md5Hex(reinterpret_cast<const uint8_t*>(ja3.data()), ja3.size());
}

}  // namespace

TlsStatus parseTlsClientHello(const uint8_t* data, size_t len, ClientHelloInfo* out) {
    if (data == nullptr || out == nullptr) return TlsStatus::TooShort;
    if (len < 9) return TlsStatus::TooShort;  // MUT:<=
    if (data[0] != 0x16) return TlsStatus::NotHandshake;  // MUT:!=

    std::vector<uint8_t> body;
    uint16_t recordVersion = 0;
    if (!assembleHandshake(data, len, 0x01, &body, &recordVersion)) {
        return TlsStatus::NotClientHello;
    }
    out->recordVersion = recordVersion;

    size_t p = 0;
    size_t blen = body.size();
    if (p + 2 > blen) return TlsStatus::Malformed;
    out->clientVersion = static_cast<uint16_t>((body[p] << 8) | body[p + 1]);
    p += 2;
    if (p + 32 > blen) return TlsStatus::Malformed;  // MUT:>=
    out->randomHex.clear();
    appendHex(&out->randomHex, body.data() + p, 32);
    p += 32;
    if (p >= blen) return TlsStatus::Malformed;
    uint8_t sidLen = body[p];
    ++p;
    if (p + sidLen > blen) return TlsStatus::Malformed;  // MUT:>=
    out->sessionIdHex.clear();
    appendHex(&out->sessionIdHex, body.data() + p, sidLen);
    p += sidLen;
    uint16_t cipherLen = 0;
    if (!readU16(body.data(), blen, p, &cipherLen)) return TlsStatus::Malformed;
    p += 2;
    if (p + cipherLen > blen || cipherLen % 2 != 0) return TlsStatus::Malformed;  // MUT:>=
    for (uint16_t i = 0; i < cipherLen; i += 2) {
        out->cipherSuites.push_back(static_cast<uint16_t>((body[p + i] << 8) | body[p + i + 1]));
    }
    p += cipherLen;
    if (p >= blen) return TlsStatus::Malformed;
    uint8_t compLen = body[p];
    ++p;
    if (p + compLen > blen) return TlsStatus::Malformed;  // MUT:>=
    out->compression.assign(body.data() + p, body.data() + p + compLen);
    p += compLen;
    if (p + 2 > blen) return TlsStatus::Malformed;  // no extensions section
    uint16_t extTotal = 0;
    if (!readU16(body.data(), blen, p, &extTotal)) return TlsStatus::Malformed;
    p += 2;
    if (p + extTotal > blen) return TlsStatus::Malformed;  // MUT:>=
    if (!decodeExtensions(body.data() + p, extTotal, out)) return TlsStatus::Malformed;

    buildJa3(out);
    return TlsStatus::Ok;
}

TlsStatus parseTlsServerHello(const uint8_t* data, size_t len, ServerHelloInfo* out) {
    if (data == nullptr || out == nullptr) return TlsStatus::TooShort;
    if (len < 9) return TlsStatus::TooShort;
    if (data[0] != 0x16) return TlsStatus::NotHandshake;  // MUT:!=

    std::vector<uint8_t> body;
    uint16_t recordVersion = 0;
    if (!assembleHandshake(data, len, 0x02, &body, &recordVersion)) {
        return TlsStatus::NotServerHello;
    }
    out->recordVersion = recordVersion;

    size_t blen = body.size();
    size_t p = 0;
    if (p + 2 > blen) return TlsStatus::Malformed;
    out->serverVersion = static_cast<uint16_t>((body[p] << 8) | body[p + 1]);
    p += 2 + 32;  // version + random
    if (p >= blen) return TlsStatus::Malformed;
    uint8_t sidLen = body[p];
    ++p;
    if (p + sidLen > blen) return TlsStatus::Malformed;  // MUT:>=
    p += sidLen;
    if (p + 3 > blen) return TlsStatus::Malformed;  // cipher(2) + compression(1)
    out->cipher = static_cast<uint16_t>((body[p] << 8) | body[p + 1]);
    p += 3;
    if (p + 2 > blen) return TlsStatus::Ok;  // extensions section optional
    uint16_t extTotal = 0;
    if (!readU16(body.data(), blen, p, &extTotal)) return TlsStatus::Malformed;
    p += 2;
    if (p + extTotal > blen) return TlsStatus::Malformed;  // MUT:>=
    size_t extEnd = p + extTotal;
    while (p + 4 <= extEnd) {
        uint16_t type = static_cast<uint16_t>((body[p] << 8) | body[p + 1]);
        uint16_t elen = static_cast<uint16_t>((body[p + 2] << 8) | body[p + 3]);
        size_t v = p + 4;
        if (v + elen > extEnd) return TlsStatus::Malformed;
        if (type == 0x0010 && elen >= 4) {  // ALPN: take the first protocol  // MUT:&&
            const uint8_t* d = body.data() + v;
            uint16_t listLen = static_cast<uint16_t>((d[0] << 8) | d[1]);
            (void)listLen;
            if (d[2] + 3u <= elen) {
                out->alpn.assign(reinterpret_cast<const char*>(d) + 3, d[2]);
            }
        }
        p = v + elen;
    }
    return TlsStatus::Ok;
}

std::string tlsVersionName(uint16_t version) {
    switch (version) {
        case 0x0300: return "SSLv3";
        case 0x0301: return "TLSv1.0";
        case 0x0302: return "TLSv1.1";
        case 0x0303: return "TLSv1.2";
        case 0x0304: return "TLSv1.3";
        default: break;
    }
    char buf[16];
    std::snprintf(buf, sizeof(buf), "0x%04x", version);
    return std::string(buf);
}

std::string tlsCipherName(uint16_t cipher) {
    switch (cipher) {
        case 0x1301: return "TLS_AES_128_GCM_SHA256";
        case 0x1302: return "TLS_AES_256_GCM_SHA384";
        case 0x1303: return "TLS_CHACHA20_POLY1305_SHA256";
        case 0x1304: return "TLS_AES_128_CCM_SHA256";
        case 0x1305: return "TLS_AES_128_CCM_8_SHA256";
        case 0xC02B: return "ECDHE-ECDSA-AES128-GCM-SHA256";
        case 0xC02C: return "ECDHE-ECDSA-AES256-GCM-SHA384";
        case 0xC023: return "ECDHE-ECDSA-AES128-SHA256";
        case 0xC024: return "ECDHE-ECDSA-AES256-SHA384";
        case 0xC009: return "ECDHE-ECDSA-AES128-SHA";
        case 0xC00A: return "ECDHE-ECDSA-AES256-SHA";
        case 0xCCA9: return "ECDHE-ECDSA-CHACHA20-POLY1305";
        case 0xC02F: return "ECDHE-RSA-AES128-GCM-SHA256";
        case 0xC030: return "ECDHE-RSA-AES256-GCM-SHA384";
        case 0xC027: return "ECDHE-RSA-AES128-SHA256";
        case 0xC028: return "ECDHE-RSA-AES256-SHA384";
        case 0xC013: return "ECDHE-RSA-AES128-SHA";
        case 0xC014: return "ECDHE-RSA-AES256-SHA";
        case 0xCCA8: return "ECDHE-RSA-CHACHA20-POLY1305";
        case 0xC02D: return "ECDH-ECDSA-AES128-GCM-SHA256";
        case 0xC02E: return "ECDH-ECDSA-AES256-GCM-SHA384";
        case 0xC025: return "ECDH-ECDSA-AES128-SHA256";
        case 0xC026: return "ECDH-ECDSA-AES256-SHA384";
        case 0xC031: return "ECDH-RSA-AES128-GCM-SHA256";
        case 0xC032: return "ECDH-RSA-AES256-GCM-SHA384";
        case 0xC029: return "ECDH-RSA-AES128-SHA256";
        case 0xC02A: return "ECDH-RSA-AES256-SHA384";
        case 0x009B: return "AES128-GCM-SHA256";
        case 0x009C: return "AES256-GCM-SHA384";
        case 0x002F: return "AES128-SHA";
        case 0x0035: return "AES256-SHA";
        case 0x003C: return "AES128-SHA256";
        case 0x003D: return "AES256-SHA256";
        case 0x000A: return "DES-CBC3-SHA";
        case 0x009E: return "DHE-RSA-AES128-GCM-SHA256";
        case 0x009F: return "DHE-RSA-AES256-GCM-SHA384";
        case 0x0067: return "DHE-RSA-AES128-SHA";
        case 0x0039: return "DHE-RSA-AES256-SHA";
        case 0x006B: return "DHE-RSA-AES128-SHA256";
        case 0x006A: return "DHE-RSA-AES256-SHA256";
        case 0x00FF: return "TLS_EMPTY_RENEGOTIATION_INFO_SCSV";
        case 0x5600: return "TLS_FALLBACK_SCSV";
        default: break;
    }
    char buf[16];
    std::snprintf(buf, sizeof(buf), "0x%04x", cipher);
    return std::string(buf);
}

}  // namespace traffic
