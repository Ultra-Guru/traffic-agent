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

TA_TEST(dns_header_only_with_questions_is_malformed) {
    // exactly 12 bytes: header says qdcount=1 but the question body is absent
    Bytes b(12, 0);
    b[4] = 0; b[5] = 1;
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(b.data(), b.size(), &q), DnsStatus::MalformedName);
}

TA_TEST(dns_accepts_max_label_length) {
    std::string label63(63, 'a');
    auto d = tb::dnsQuery(label63 + ".com");
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(d.data(), d.size(), &q), DnsStatus::Ok);
    TA_CHECK_EQ(q.name.size(), static_cast<size_t>(63 + 4));  // "a"*63 + ".com"
}

TA_TEST(dns_accepts_name_of_total_255) {
    // 4 labels of 63 + one label of 3 -> total label bytes = 255 (the limit)
    std::string l63(63, 'x');
    std::string name = l63 + "." + l63 + "." + l63 + "." + l63 + ".abc";
    auto d = tb::dnsQuery(name);
    DnsQuestion q{};
    TA_CHECK_EQ(parseDnsQuestion(d.data(), d.size(), &q), DnsStatus::Ok);
}
