#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace traffic {

struct DnsQuestion {
    std::string name;
    uint16_t qtype = 0;
    uint16_t qclass = 0;
};

enum class DnsStatus { Ok, TooShort, MalformedName, LabelTooLong };

// Parses the first question of a DNS message (header 12 bytes + QNAME/QTYPE/QCLASS).
DnsStatus parseDnsQuestion(const uint8_t* data, size_t len, DnsQuestion* out);

}  // namespace traffic
