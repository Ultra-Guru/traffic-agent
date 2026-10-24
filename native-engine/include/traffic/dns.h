#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace traffic {

struct DnsQuestion {
    std::string name;
    uint16_t qtype = 0;
    uint16_t qclass = 0;
};

struct DnsAnswer {
    std::string name;
    uint16_t type = 0;
    uint16_t cls = 0;
    uint32_t ttl = 0;
    std::string rdataText;  // A/AAAA/... rendered for the UI
};

struct DnsMessage {
    uint16_t flags = 0;
    uint16_t rcode = 0;
    std::vector<DnsQuestion> questions;
    std::vector<DnsAnswer> answers;
};

enum class DnsStatus {
    Ok,
    TooShort,
    MalformedName,
    LabelTooLong,
    Malformed,        // structural violation outside the name fields
    BadPointer,       // compression pointer loop / out of bounds
    MalformedRdata    // truncated or unknown rdata encoding
};

// Parses the first question of a DNS message (header 12 bytes + QNAME/QTYPE/QCLASS).
DnsStatus parseDnsQuestion(const uint8_t* data, size_t len, DnsQuestion* out);

// Full response parse: all questions and answers with name compression
// (RFC 1035 section 4.1.4) and A/AAAA/CNAME/MX/TXT/NS/SOA/PTR rdata
// rendering. Questions-only messages parse fine too (qdcount, ancount = 0).
DnsStatus parseDnsResponse(const uint8_t* data, size_t len, DnsMessage* out);

// "1.2.3.4", "fe80::1", "example.com.", "10 mail.example.com.",
// "\"v=spf1 ...\"", "ns.example.com. host.example.com. 1 2 3 4 5" etc.
std::string dnsTypeMnemonic(uint16_t type);

}  // namespace traffic
