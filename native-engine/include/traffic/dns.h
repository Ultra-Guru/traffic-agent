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

// EDNS0 OPT pseudo-RR (RFC 6891): the additional-section record whose owner
// name is root, type 41. Carries the extended rcode, UDP payload size, the
// DNSSEC OK bit and a list of TLV options.
struct DnsEdnsOption {
    uint16_t code = 0;
    std::vector<uint8_t> data;
};

struct DnsEdns {
    bool present = false;
    uint16_t udpPayloadSize = 0;
    uint8_t extendedRcode = 0;  // upper 8 bits of the 12-bit rcode
    uint8_t version = 0;
    bool dnssecOk = false;      // DO bit (flag bit 15 of the OPT TTL)
    std::vector<DnsEdnsOption> options;
};

struct DnsMessage {
    uint16_t flags = 0;
    uint16_t rcode = 0;
    std::vector<DnsQuestion> questions;
    std::vector<DnsAnswer> answers;
    std::vector<DnsAnswer> authorities;   // NS section
    std::vector<DnsAnswer> additionals;   // non-OPT additional records
    DnsEdns edns;

    // 4-bit opcode from the flags (0 = QUERY, 4 = NOTIFY, 5 = UPDATE).
    uint16_t opcode() const { return (flags >> 11) & 0x0Fu; }
    bool isResponse() const { return (flags & 0x8000u) != 0u; }
    bool authoritativeAnswer() const { return (flags & 0x0400u) != 0u; }
    bool truncation() const { return (flags & 0x0200u) != 0u; }
    bool recursionDesired() const { return (flags & 0x0100u) != 0u; }
    bool recursionAvailable() const { return (flags & 0x0080u) != 0u; }
    bool checkingDisabled() const { return (flags & 0x0010u) != 0u; }
    bool authenticatedData() const { return (flags & 0x0020u) != 0u; }
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
// (RFC 1035 section 4.1.4) and A/AAAA/CNAME/MX/TXT/NS/SOA/PTR/SRV/CAA/
// HTTPS/SVCB rdata rendering. The additional section is walked; OPT records
// populate out->edns, everything else lands in out->additionals.
// Questions-only messages parse fine too (qdcount, ancount = 0).
DnsStatus parseDnsResponse(const uint8_t* data, size_t len, DnsMessage* out);

// "1.2.3.4", "fe80::1", "example.com.", "10 mail.example.com.",
// "\"v=spf1 ...\"", "ns.example.com. host.example.com. 1 2 3 4 5" etc.
std::string dnsTypeMnemonic(uint16_t type);

// Human name for an EDNS0 option code (RFC 6891 + registry): "nsid",
// "ecs", "cookie", "keepalive", "padding", "expire", "unknown(65001)".
std::string dnsEdnsOptionName(uint16_t code);

}  // namespace traffic
