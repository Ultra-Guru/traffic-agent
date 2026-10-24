#pragma once

// Byte-level builders used to synthesize test packets deterministically.

#include <cstdint>
#include <string>
#include <vector>

namespace tb {

using Bytes = std::vector<uint8_t>;

inline void putU16(Bytes& b, size_t pos, uint16_t v) {
    b[pos] = static_cast<uint8_t>(v >> 8);
    b[pos + 1] = static_cast<uint8_t>(v & 0xFF);
}

inline void pushU16(Bytes& b, uint16_t v) {
    b.push_back(static_cast<uint8_t>(v >> 8));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

inline void pushU32(Bytes& b, uint32_t v) {
    b.push_back(static_cast<uint8_t>(v >> 24));
    b.push_back(static_cast<uint8_t>((v >> 16) & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

inline Bytes str(const std::string& s) { return Bytes(s.begin(), s.end()); }

// Minimal 20-byte TCP header (data offset 5) + payload.
inline Bytes tcpSegment(uint32_t seq, uint8_t flags, const Bytes& payload = {}) {
    Bytes h(20, 0);
    putU16(h, 0, 12345);   // src port
    putU16(h, 2, 80);      // dst port
    h[4] = static_cast<uint8_t>(seq >> 24);
    h[5] = static_cast<uint8_t>((seq >> 16) & 0xFF);
    h[6] = static_cast<uint8_t>((seq >> 8) & 0xFF);
    h[7] = static_cast<uint8_t>(seq & 0xFF);
    h[12] = 0x50;  // data offset 5 << 4
    h[13] = flags;
    Bytes out = h;
    out.insert(out.end(), payload.begin(), payload.end());
    return out;
}

// IPv4 header (20 bytes, protocol selectable) + payload.
inline Bytes ipv4(const Bytes& payload, uint8_t protocol = 6, uint16_t totalLen = 0) {
    Bytes h(20, 0);
    h[0] = 0x45;  // version 4, IHL 5
    uint16_t tl = totalLen != 0 ? totalLen : static_cast<uint16_t>(20 + payload.size());
    putU16(h, 2, tl);
    h[8] = 64;  // TTL
    h[9] = protocol;
    h[12] = 192; h[13] = 168; h[14] = 1; h[15] = 10;  // src 192.168.1.10
    h[16] = 142; h[17] = 250; h[18] = 10; h[19] = 20;  // dst 142.250.10.20
    Bytes out = h;
    out.insert(out.end(), payload.begin(), payload.end());
    return out;
}

inline Bytes udpDatagram(uint16_t srcPort, uint16_t dstPort, const Bytes& payload) {
    Bytes h(8, 0);
    putU16(h, 0, srcPort);
    putU16(h, 2, dstPort);
    putU16(h, 4, static_cast<uint16_t>(8 + payload.size()));
    Bytes out = h;
    out.insert(out.end(), payload.begin(), payload.end());
    return out;
}

// DNS query message with a single question.
inline Bytes dnsQuery(const std::string& name, uint16_t qtype = 1) {
    Bytes d;
    pushU16(d, 0x1234);  // id
    pushU16(d, 0x0100);  // flags: recursion desired
    pushU16(d, 1);       // qdcount
    pushU16(d, 0);       // ancount
    pushU16(d, 0);       // nscount
    pushU16(d, 0);       // arcount
    size_t start = 0;
    while (true) {
        size_t dot = name.find('.', start);
        std::string label = (dot == std::string::npos) ? name.substr(start) : name.substr(start, dot - start);
        d.push_back(static_cast<uint8_t>(label.size()));
        d.insert(d.end(), label.begin(), label.end());
        if (dot == std::string::npos) break;
        start = dot + 1;
    }
    d.push_back(0);  // root label
    pushU16(d, qtype);
    pushU16(d, 1);  // IN
    return d;
}

// TLS ClientHello carrying an SNI extension with the given host name.
inline Bytes clientHello(const std::string& sni) {
    // server_name extension payload:
    //   list_len(2) | name_type(1)=0 | name_len(2) | name
    Bytes ext;
    pushU16(ext, static_cast<uint16_t>(1 + 2 + sni.size()));
    ext.push_back(0);
    pushU16(ext, static_cast<uint16_t>(sni.size()));
    ext.insert(ext.end(), sni.begin(), sni.end());

    // ClientHello body
    Bytes body;
    pushU16(body, 0x0303);                  // client_version TLS 1.2
    body.insert(body.end(), 32, 0xAB);      // random
    body.push_back(0);                      // session id length
    pushU16(body, 2);                       // cipher suites length
    pushU16(body, 0x1301);                  // TLS_AES_128_GCM_SHA256
    body.push_back(1);                      // compression methods length
    body.push_back(0);                      // null compression
    pushU16(body, static_cast<uint16_t>(4 + ext.size()));  // extensions total length
    pushU16(body, 0x0000);                  // extension type: server_name
    pushU16(body, static_cast<uint16_t>(ext.size()));      // extension length
    body.insert(body.end(), ext.begin(), ext.end());

    // Handshake: ClientHello
    Bytes ch;
    ch.push_back(0x01);
    ch.push_back(static_cast<uint8_t>((body.size() >> 16) & 0xFF));
    ch.push_back(static_cast<uint8_t>((body.size() >> 8) & 0xFF));
    ch.push_back(static_cast<uint8_t>(body.size() & 0xFF));
    ch.insert(ch.end(), body.begin(), body.end());

    // TLS record
    Bytes rec;
    rec.push_back(0x16);
    rec.push_back(0x03);
    rec.push_back(0x01);
    pushU16(rec, static_cast<uint16_t>(ch.size()));
    rec.insert(rec.end(), ch.begin(), ch.end());
    return rec;
}

// Rich ClientHello with a fixed, deterministic fingerprint shape:
// ciphers 1301,1302,c02b,c02f,00ff; extensions SNI(0), ec_point_formats(11),
// supported_groups(10), signature_algorithms(13), ALPN(16), supported_versions(43).
inline Bytes clientHelloFull(const std::string& sni) {
    Bytes body;
    pushU16(body, 0x0303);                       // client_version TLS 1.2
    for (int i = 0; i < 32; ++i) body.push_back(0xCD);  // random
    body.push_back(4);                            // session id length
    const uint8_t sid[4] = {0x9A, 0xBC, 0xDE, 0xF0};
    body.insert(body.end(), sid, sid + 4);
    const uint16_t ciphers[] = {0x1301, 0x1302, 0xC02B, 0xC02F, 0x00FF};
    pushU16(body, static_cast<uint16_t>(sizeof(ciphers)));
    for (uint16_t c : ciphers) pushU16(body, c);
    body.push_back(1);                            // compression methods length
    body.push_back(0);                            // null

    Bytes exts;
    // server_name
    Bytes sniExt;
    pushU16(sniExt, static_cast<uint16_t>(3 + sni.size()));
    sniExt.push_back(0);
    pushU16(sniExt, static_cast<uint16_t>(sni.size()));
    sniExt.insert(sniExt.end(), sni.begin(), sni.end());
    pushU16(exts, 0x0000);
    pushU16(exts, static_cast<uint16_t>(sniExt.size()));
    exts.insert(exts.end(), sniExt.begin(), sniExt.end());
    // ec_point_formats: [uncompressed]
    pushU16(exts, 0x000B);
    pushU16(exts, 2);
    exts.push_back(1);
    exts.push_back(0);
    // supported_groups: x25519(29), secp256r1(23)
    pushU16(exts, 0x000A);
    pushU16(exts, 6);
    pushU16(exts, 4);
    pushU16(exts, 29);
    pushU16(exts, 23);
    // signature_algorithms: ecdsa_secp256r1_sha256(0x0403), rsa_pss_rsae_sha256(0x0804)
    pushU16(exts, 0x000D);
    pushU16(exts, 6);
    pushU16(exts, 4);
    pushU16(exts, 0x0403);
    pushU16(exts, 0x0804);
    // ALPN: h2, http/1.1
    Bytes alpn;
    pushU16(alpn, static_cast<uint16_t>(3 + 9));  // list: (1+2) + (1+8)
    alpn.push_back(2);
    const uint8_t h2[2] = {'h', '2'};
    alpn.insert(alpn.end(), h2, h2 + 2);
    alpn.push_back(8);
    const uint8_t http11[8] = {'h', 't', 't', 'p', '/', '1', '.', '1'};
    alpn.insert(alpn.end(), http11, http11 + 8);
    pushU16(exts, 0x0010);
    pushU16(exts, static_cast<uint16_t>(alpn.size()));
    exts.insert(exts.end(), alpn.begin(), alpn.end());
    // supported_versions: TLS 1.3, TLS 1.2
    pushU16(exts, 0x002B);
    pushU16(exts, 5);
    exts.push_back(4);
    pushU16(exts, 0x0304);
    pushU16(exts, 0x0303);

    pushU16(body, static_cast<uint16_t>(exts.size()));
    body.insert(body.end(), exts.begin(), exts.end());

    Bytes ch;
    ch.push_back(0x01);
    ch.push_back(static_cast<uint8_t>((body.size() >> 16) & 0xFF));
    ch.push_back(static_cast<uint8_t>((body.size() >> 8) & 0xFF));
    ch.push_back(static_cast<uint8_t>(body.size() & 0xFF));
    ch.insert(ch.end(), body.begin(), body.end());

    Bytes rec;
    rec.push_back(0x16);
    rec.push_back(0x03);
    rec.push_back(0x01);
    pushU16(rec, static_cast<uint16_t>(ch.size()));
    rec.insert(rec.end(), ch.begin(), ch.end());
    return rec;
}

// TLS ServerHello (record + handshake) with cipher and optional ALPN.
inline Bytes serverHello(uint16_t cipher, const std::string& alpn) {
    Bytes body;
    pushU16(body, 0x0303);              // server_version
    for (int i = 0; i < 32; ++i) body.push_back(0x77);
    body.push_back(0);                  // session id
    pushU16(body, cipher);
    body.push_back(0);                  // compression
    if (!alpn.empty()) {
        Bytes a;
        pushU16(a, static_cast<uint16_t>(1 + alpn.size()));
        a.push_back(static_cast<uint8_t>(alpn.size()));
        a.insert(a.end(), alpn.begin(), alpn.end());
        pushU16(body, static_cast<uint16_t>(4 + a.size()));  // extensions length
        pushU16(body, 0x0010);
        pushU16(body, static_cast<uint16_t>(a.size()));
        body.insert(body.end(), a.begin(), a.end());
    } else {
        pushU16(body, 0);
    }
    Bytes hs;
    hs.push_back(0x02);
    hs.push_back(static_cast<uint8_t>((body.size() >> 16) & 0xFF));
    hs.push_back(static_cast<uint8_t>((body.size() >> 8) & 0xFF));
    hs.push_back(static_cast<uint8_t>(body.size() & 0xFF));
    hs.insert(hs.end(), body.begin(), body.end());
    Bytes rec;
    rec.push_back(0x16);
    rec.push_back(0x03);
    rec.push_back(0x03);
    pushU16(rec, static_cast<uint16_t>(hs.size()));
    rec.insert(rec.end(), hs.begin(), hs.end());
    return rec;
}

// HTTP/2 frame: 9-byte header + payload.
inline Bytes h2Frame(uint8_t type, uint8_t flags, uint32_t streamId, const Bytes& payload) {
    Bytes f;
    f.push_back(static_cast<uint8_t>((payload.size() >> 16) & 0xFF));
    f.push_back(static_cast<uint8_t>((payload.size() >> 8) & 0xFF));
    f.push_back(static_cast<uint8_t>(payload.size() & 0xFF));
    f.push_back(type);
    f.push_back(flags);
    f.push_back(static_cast<uint8_t>((streamId >> 24) & 0x7F));
    f.push_back(static_cast<uint8_t>((streamId >> 16) & 0xFF));
    f.push_back(static_cast<uint8_t>((streamId >> 8) & 0xFF));
    f.push_back(static_cast<uint8_t>(streamId & 0xFF));
    f.insert(f.end(), payload.begin(), payload.end());
    return f;
}

}  // namespace tb
