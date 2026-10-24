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

}  // namespace tb
