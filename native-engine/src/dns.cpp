#include "traffic/dns.h"

#include <cstdio>
#include <string>

namespace traffic {

namespace {

std::string labelString(const uint8_t* data, size_t len) {
    std::string s;
    static const char* kHex = "0123456789abcdef";
    for (size_t i = 0; i < len && s.size() < 256; ++i) {
        uint8_t c = data[i];
        if (c >= 0x20 && c < 0x7Fu) {
            s.push_back(static_cast<char>(c));
        } else {
            s.push_back('\\');
            s.push_back('x');
            s.push_back(kHex[c >> 4]);
            s.push_back(kHex[c & 0x0Fu]);
        }
    }
    return s;
}

uint16_t rdU16(const uint8_t* p) {
    return static_cast<uint16_t>((p[0] << 8) | p[1]);
}

uint32_t rdU32(const uint8_t* p) {
    return (static_cast<uint32_t>(p[0]) << 24) | (static_cast<uint32_t>(p[1]) << 16) |
           (static_cast<uint32_t>(p[2]) << 8) | p[3];
}

// Reads a possibly-compressed domain name (RFC 1035 section 4.1.4) starting
// at *pos. On success *pos is advanced past the name bytes at the ORIGINAL
// location (pointer suffixes do not advance it further).
DnsStatus readName(const uint8_t* data, size_t len, size_t* pos, std::string* out) {
    std::string name;
    size_t p = *pos;
    size_t end = *pos;
    bool followed = false;
    size_t jumps = 0;
    size_t total = 0;
    while (true) {
        if (p >= len) return DnsStatus::MalformedName;
        uint8_t l = data[p];
        if (l == 0) {
            ++p;
            if (!followed) end = p;
            break;  // root label terminates the name
        }
        if ((l & 0xC0u) == 0xC0u) {  // compression pointer  // MUT:!=
            if (p + 1 >= len) return DnsStatus::MalformedName;
            size_t target = (static_cast<size_t>(l & 0x3Fu) << 8) | data[p + 1];
            if (!followed) end = p + 2;
            followed = true;
            ++jumps;
            if (jumps > 16) return DnsStatus::BadPointer;  // loop / chain guard  // MUT:<
            p = target;
            continue;
        }
        if (l > 63) return DnsStatus::LabelTooLong;  // MUT:>=
        if (p + 1 + l > len) return DnsStatus::MalformedName;
        total += l;
        if (total > 255) return DnsStatus::LabelTooLong;  // MUT:>=
        if (!name.empty()) name.push_back('.');
        name.append(reinterpret_cast<const char*>(data + p + 1), l);
        p += 1 + l;
        if (!followed) end = p;
    }
    *pos = end;
    *out = name;
    return DnsStatus::Ok;
}

std::string ipv4Text(const uint8_t* p) {
    std::string s;
    for (int i = 0; i < 4; ++i) {
        if (i > 0) s.push_back('.');
        s += std::to_string(p[i]);
    }
    return s;
}

std::string ipv6Text(const uint8_t* p) {
    // RFC 5952 style: 8 groups of lowercase hex with the longest zero run
    // elided as "::" (ties go to the first run, at least two groups).
    uint16_t groups[8];
    for (int i = 0; i < 8; ++i) {
        groups[i] = static_cast<uint16_t>((p[i * 2] << 8) | p[i * 2 + 1]);
    }
    int bestStart = -1, bestLen = 0;
    for (int i = 0; i < 8;) {
        if (groups[i] != 0) {
            ++i;
            continue;
        }
        int j = i;
        while (j < 8 && groups[j] == 0) ++j;
        if (j - i > bestLen) {
            bestLen = j - i;
            bestStart = i;
        }
        i = j;
    }
    if (bestLen < 2) bestStart = -1;  // don't elide a single group
    char buf[8];
    std::string left, right;
    for (int i = 0; i < (bestStart >= 0 ? bestStart : 8); ++i) {
        if (!left.empty()) left.push_back(':');
        std::snprintf(buf, sizeof(buf), "%x", groups[i]);
        left += buf;
    }
    if (bestStart >= 0) {
        for (int i = bestStart + bestLen; i < 8; ++i) {
            if (!right.empty()) right.push_back(':');
            std::snprintf(buf, sizeof(buf), "%x", groups[i]);
            right += buf;
        }
        return left + "::" + right;
    }
    return left;
}

// Renders one answer's rdata into human-readable text.
std::string svcbParamKey(uint16_t key) {
    switch (key) {
        case 0: return "mandatory";
        case 1: return "alpn";
        case 2: return "no-default-alpn";
        case 3: return "port";
        case 4: return "ipv4hint";
        case 5: return "ech";
        case 6: return "ipv6hint";
        case 7: return "dohpath";
        case 8: return "ohttp";
        default: return "key" + std::to_string(key);
    }
}

DnsStatus renderRdata(const uint8_t* data, size_t len, size_t pos, uint16_t type, uint16_t rdlen,
                      std::string* out) {
    if (pos + rdlen > len) return DnsStatus::MalformedRdata;  // MUT:>=
    const uint8_t* r = data + pos;
    switch (type) {
        case 1:  // A
            if (rdlen != 4) return DnsStatus::MalformedRdata;
            *out = ipv4Text(r);
            return DnsStatus::Ok;
        case 28: {  // AAAA
            if (rdlen != 16) return DnsStatus::MalformedRdata;
            *out = ipv6Text(r);
            return DnsStatus::Ok;
        }
        case 2:   // NS
        case 5:   // CNAME
        case 12: {  // PTR
            size_t p = pos;
            return readName(data, len, &p, out);
        }
        case 15: {  // MX: preference + exchange
            if (rdlen < 3) return DnsStatus::MalformedRdata;
            size_t p = pos + 2;
            std::string host;
            DnsStatus s = readName(data, len, &p, &host);
            if (s != DnsStatus::Ok) return s;
            *out = std::to_string(rdU16(r)) + " " + host;
            return DnsStatus::Ok;
        }
        case 16: {  // TXT: sequence of character-strings
            std::string s;
            size_t p = pos;
            size_t endPos = pos + rdlen;
            while (p < endPos) {
                uint8_t clen = data[p];
                if (p + 1 + clen > endPos) return DnsStatus::MalformedRdata;
                s.append(reinterpret_cast<const char*>(data + p + 1), clen);
                p += 1 + clen;
            }
            *out = s;
            return DnsStatus::Ok;
        }
        case 6: {  // SOA: mname rname serial refresh retry expire minimum
            size_t p = pos;
            std::string mname, rname;
            DnsStatus s = readName(data, len, &p, &mname);
            if (s != DnsStatus::Ok) return s;
            s = readName(data, len, &p, &rname);
            if (s != DnsStatus::Ok) return s;
            if (p + 20 > len) return DnsStatus::MalformedRdata;
            const uint8_t* q = data + p;
            *out = mname + " " + rname + " " + std::to_string(rdU32(q)) + " " +
                   std::to_string(rdU32(q + 4)) + " " + std::to_string(rdU32(q + 8)) + " " +
                   std::to_string(rdU32(q + 12)) + " " + std::to_string(rdU32(q + 16));
            return DnsStatus::Ok;
        }
        case 33: {  // SRV: priority weight port target
            if (rdlen < 7) return DnsStatus::MalformedRdata;  // MUT:<=
            size_t p = pos + 6;
            std::string target;
            DnsStatus s = readName(data, len, &p, &target);
            if (s != DnsStatus::Ok) return s;
            *out = std::to_string(rdU16(r)) + " " + std::to_string(rdU16(r + 2)) + " " +
                   std::to_string(rdU16(r + 4)) + " " + target;
            return DnsStatus::Ok;
        }
        case 257: {  // CAA: flags tag value
            if (rdlen < 2) return DnsStatus::MalformedRdata;
            const uint8_t caaFlags = r[0];
            const size_t tagLen = r[1];
            if (2 + tagLen > rdlen) return DnsStatus::MalformedRdata;  // MUT:>=
            std::string tag(reinterpret_cast<const char*>(r + 2), tagLen);
            std::string value(reinterpret_cast<const char*>(r + 2 + tagLen), rdlen - 2 - tagLen);
            *out = std::to_string(caaFlags) + " " + tag + " \"" + value + "\"";
            return DnsStatus::Ok;
        }
        case 64:    // SVCB
        case 65: {  // HTTPS: priority target param-list (alpn,h2,...)
            if (rdlen < 3) return DnsStatus::MalformedRdata;
            size_t p = pos + 2;  // skip the 2-byte priority
            std::string target;
            DnsStatus s = readName(data, len, &p, &target);
            if (s != DnsStatus::Ok) return s;
            std::string result = std::to_string(rdU16(r)) + " " + target;
            // SvcParams: key(2) len(2) value, rendered as key=value pairs.
            size_t q = p;
            const size_t endPos = pos + rdlen;
            while (q + 4 <= endPos) {
                uint16_t key = rdU16(data + q);
                uint16_t vlen = rdU16(data + q + 2);
                q += 4;
                if (q + vlen > endPos) return DnsStatus::MalformedRdata;
                result += " " + svcbParamKey(key) + "=" +
                          labelString(data + q, vlen);
                q += vlen;
            }
            *out = result;
            return DnsStatus::Ok;
        }
        default: {
            *out = labelString(r, rdlen);
            return DnsStatus::Ok;
        }
    }
}

}  // namespace

DnsStatus parseDnsQuestion(const uint8_t* data, size_t len, DnsQuestion* out) {
    if (data == nullptr || out == nullptr) return DnsStatus::TooShort;
    if (len < 12) return DnsStatus::TooShort;  // MUT:<=
    uint16_t qdcount = static_cast<uint16_t>((data[4] << 8) | data[5]);
    if (qdcount == 0) return DnsStatus::MalformedName;  // MUT:!=
    size_t pos = 12;
    std::string name;
    DnsStatus s = readName(data, len, &pos, &name);
    if (s != DnsStatus::Ok) return s;
    if (name.empty()) return DnsStatus::MalformedName;
    if (pos + 4 > len) return DnsStatus::MalformedName;  // MUT:>=
    out->name = name;
    out->qtype = static_cast<uint16_t>((data[pos] << 8) | data[pos + 1]);
    out->qclass = static_cast<uint16_t>((data[pos + 2] << 8) | data[pos + 3]);
    return DnsStatus::Ok;
}

DnsStatus parseDnsResponse(const uint8_t* data, size_t len, DnsMessage* out) {
    if (data == nullptr || out == nullptr) return DnsStatus::TooShort;
    if (len < 12) return DnsStatus::TooShort;
    out->flags = static_cast<uint16_t>((data[2] << 8) | data[3]);
    out->rcode = static_cast<uint16_t>(out->flags & 0x0Fu);
    uint16_t qdcount = static_cast<uint16_t>((data[4] << 8) | data[5]);
    uint16_t ancount = static_cast<uint16_t>((data[6] << 8) | data[7]);
    uint16_t nscount = static_cast<uint16_t>((data[8] << 8) | data[9]);
    uint16_t arcount = static_cast<uint16_t>((data[10] << 8) | data[11]);
    size_t pos = 12;

    for (uint16_t i = 0; i < qdcount; ++i) {
        DnsQuestion q;
        DnsStatus s = readName(data, len, &pos, &q.name);
        if (s != DnsStatus::Ok) return s;
        if (pos + 4 > len) return DnsStatus::Malformed;  // MUT:>=
        q.qtype = static_cast<uint16_t>((data[pos] << 8) | data[pos + 1]);
        q.qclass = static_cast<uint16_t>((data[pos + 2] << 8) | data[pos + 3]);
        pos += 4;
        out->questions.push_back(std::move(q));
    }

    // Shared walker for answer / authority / additional sections.
    auto walkSection = [&](uint16_t count, std::vector<DnsAnswer>* section,
                           bool allowOpt) -> DnsStatus {
        for (uint16_t i = 0; i < count; ++i) {
            DnsAnswer a;
            DnsStatus s = readName(data, len, &pos, &a.name);
            if (s != DnsStatus::Ok) return s;
            if (pos + 10 > len) return DnsStatus::Malformed;
            a.type = static_cast<uint16_t>((data[pos] << 8) | data[pos + 1]);
            a.cls = static_cast<uint16_t>((data[pos + 2] << 8) | data[pos + 3]);
            a.ttl = rdU32(data + pos + 4);
            uint16_t rdlen = static_cast<uint16_t>((data[pos + 8] << 8) | data[pos + 9]);
            pos += 10;
            if (pos + rdlen > len) return DnsStatus::Malformed;

            // OPT pseudo-RR (RFC 6891): owner root, type 41. The class field
            // is the UDP payload size, the TTL packs ext-rcode/version/flags.
            if (a.type == 41 && allowOpt) {
                out->edns.present = true;  // MUT:!
                out->edns.udpPayloadSize = a.cls;
                out->edns.extendedRcode = static_cast<uint8_t>(a.ttl >> 24);
                out->edns.version = static_cast<uint8_t>((a.ttl >> 16) & 0xffu);
                out->edns.dnssecOk = (a.ttl & 0x8000u) != 0u;
                size_t q2 = pos;
                const size_t endPos = pos + rdlen;
                while (q2 + 4 <= endPos) {
                    DnsEdnsOption opt;
                    opt.code = rdU16(data + q2);
                    uint16_t olen = rdU16(data + q2 + 2);
                    q2 += 4;
                    if (q2 + olen > endPos) return DnsStatus::MalformedRdata;
                    opt.data.assign(data + q2, data + q2 + olen);
                    q2 += olen;
                    out->edns.options.push_back(std::move(opt));
                }
                pos += rdlen;
                continue;
            }
            s = renderRdata(data, len, pos, a.type, rdlen, &a.rdataText);
            if (s != DnsStatus::Ok) return s;
            pos += rdlen;
            section->push_back(std::move(a));
        }
        return DnsStatus::Ok;
    };

    DnsStatus s = walkSection(ancount, &out->answers, false);
    if (s != DnsStatus::Ok) return s;
    s = walkSection(nscount, &out->authorities, false);
    if (s != DnsStatus::Ok) return s;
    s = walkSection(arcount, &out->additionals, true);
    if (s != DnsStatus::Ok) return s;
    return DnsStatus::Ok;
}

std::string dnsEdnsOptionName(uint16_t code) {
    switch (code) {
        case 3: return "nsid";
        case 5: return "nosi";
        case 8: return "ecs";
        case 10: return "cookie";
        case 11: return "keepalive";
        case 12: return "padding";
        case 9: return "expire";
        case 13: return "chain";
        case 14: return "key-tag";
        case 15: return "extended-dns-error";
        case 26946: return "deviceid";
        default: return "unknown(" + std::to_string(code) + ")";
    }
}

std::string dnsTypeMnemonic(uint16_t type) {
    switch (type) {
        case 1: return "A";
        case 2: return "NS";
        case 5: return "CNAME";
        case 6: return "SOA";
        case 12: return "PTR";
        case 15: return "MX";
        case 16: return "TXT";
        case 28: return "AAAA";
        case 33: return "SRV";
        case 41: return "OPT";
        case 64: return "SVCB";
        case 65: return "HTTPS";
        case 255: return "ANY";
        case 257: return "CAA";
        default: break;
    }
    return "TYPE" + std::to_string(type);
}

}  // namespace traffic
