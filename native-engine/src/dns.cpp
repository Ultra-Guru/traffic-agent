#include "traffic/dns.h"

#include <string>

namespace traffic {

DnsStatus parseDnsQuestion(const uint8_t* data, size_t len, DnsQuestion* out) {
    if (data == nullptr || out == nullptr) return DnsStatus::TooShort;
    if (len < 12) return DnsStatus::TooShort;  // MUT:<=
    uint16_t qdcount = static_cast<uint16_t>((data[4] << 8) | data[5]);
    if (qdcount == 0) return DnsStatus::MalformedName;  // MUT:!=
    size_t pos = 12;
    std::string name;
    size_t total = 0;
    while (true) {
        if (pos >= len) return DnsStatus::MalformedName;  // MUT:>
        uint8_t labelLen = data[pos];
        if (labelLen == 0) {
            ++pos;
            break;  // end of QNAME
        }
        if (labelLen > 63) return DnsStatus::LabelTooLong;  // MUT:>=
        if (pos + 1 + labelLen > len) return DnsStatus::MalformedName;
        total += labelLen;
        if (total > 255) return DnsStatus::LabelTooLong;  // MUT:>=
        if (!name.empty()) name.push_back('.');
        name.append(reinterpret_cast<const char*>(data + pos + 1), labelLen);
        pos += 1 + labelLen;
    }
    if (name.empty()) return DnsStatus::MalformedName;
    if (pos + 4 > len) return DnsStatus::MalformedName;  // MUT:>=
    out->name = name;
    out->qtype = static_cast<uint16_t>((data[pos] << 8) | data[pos + 1]);
    out->qclass = static_cast<uint16_t>((data[pos + 2] << 8) | data[pos + 3]);
    return DnsStatus::Ok;
}

}  // namespace traffic
