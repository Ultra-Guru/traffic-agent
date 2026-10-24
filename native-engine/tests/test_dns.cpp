#include "traffic/dns.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(dns_parses_query_name) {
    auto d = tb::dnsQuery("api.example.com");
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(d.data(), d.size(), &q), DnsStatus::Ok);
    TA_CHECK_ST(q.name, "api.example.com");
    TA_CHECK_EQ(q.qtype, 1);
    TA_CHECK_EQ(q.qclass, 1);
}

TA_TEST(dns_rejects_short_message) {
    Bytes b(11, 0);
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(b.data(), b.size(), &q), DnsStatus::TooShort);
}

TA_TEST(dns_rejects_zero_question_count) {
    auto d = tb::dnsQuery("a.b");
    d[4] = 0; d[5] = 0;  // qdcount = 0
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(d.data(), d.size(), &q), DnsStatus::MalformedName);
}

TA_TEST(dns_rejects_oversized_label) {
    auto d = tb::dnsQuery("a.b");
    // inflate the first label length byte to 200 (> 63)
    d[12] = 200;
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(d.data(), d.size(), &q), DnsStatus::LabelTooLong);
}

TA_TEST(dns_rejects_unterminated_name) {
    auto d = tb::dnsQuery("a.b");
    // remove trailing bytes after labels: truncate before the root label
    Bytes cut(d.begin(), d.begin() + 12 + 4);  // header + 2 labels, no terminator/qtype
    DnsQuestion q{};
    TA_CHECK(parseDnsQuestion(cut.data(), cut.size(), &q) != DnsStatus::Ok);
}
