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
    // inflate the first label length byte to 100 (> 63, not a pointer pattern)
    d[12] = 100;
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

// ---------------- response parsing (RFC 1035 with compression) ----------------

namespace {

void pushU16b(Bytes& b, uint16_t v) {
    b.push_back(static_cast<uint8_t>(v >> 8));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

// Header: qr=1, rd=1, ra=1, rcode=0; one question "example.com" A IN.
Bytes dnsHeader(uint16_t ancount, uint16_t flags = 0x8180, uint16_t qdcount = 1) {
    Bytes h;
    pushU16b(h, 0x1234);  // id
    pushU16b(h, flags);
    pushU16b(h, qdcount);
    pushU16b(h, ancount);
    pushU16b(h, 0);  // nscount
    pushU16b(h, 0);  // arcount
    return h;
}

Bytes qnameExampleCom() {
    Bytes q;
    q.push_back(7);
    q.insert(q.end(), {'e', 'x', 'a', 'm', 'p', 'l', 'e'});
    q.push_back(3);
    q.insert(q.end(), {'c', 'o', 'm'});
    q.push_back(0);
    return q;
}

}  // namespace

TA_TEST(dns_response_a_record_with_pointer) {
    auto d = dnsHeader(1);
    auto qn = qnameExampleCom();
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);  // A
    pushU16b(d, 1);  // IN
    // answer: name = pointer to offset 12
    d.push_back(0xC0);
    d.push_back(0x0C);
    pushU16b(d, 1);    // type A
    pushU16b(d, 1);    // class IN
    d.push_back(0); d.push_back(0); d.push_back(1); d.push_back(0x2C);  // ttl 300
    pushU16b(d, 4);    // rdlength
    d.push_back(93); d.push_back(184); d.push_back(216); d.push_back(34);  // 93.184.216.34

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.rcode, 0u);
    TA_CHECK_EQ(m.questions.size(), static_cast<size_t>(1));
    TA_CHECK_ST(m.questions[0].name, "example.com");
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(1));
    if (m.answers.size() == 1) {
        TA_CHECK_ST(m.answers[0].name, "example.com");
        TA_CHECK_EQ(m.answers[0].type, 1u);
        TA_CHECK_EQ(m.answers[0].ttl, 300u);
        TA_CHECK_ST(m.answers[0].rdataText, "93.184.216.34");
    }
}

TA_TEST(dns_response_aaaa_cname_mx_txt) {
    auto d = dnsHeader(3);
    auto qn = qnameExampleCom();
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 255);  // ANY
    pushU16b(d, 1);
    // CNAME: pointer name, target = literal "www.example.com."
    d.push_back(0xC0); d.push_back(0x0C);
    pushU16b(d, 5);    // CNAME
    pushU16b(d, 1);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(0x3C);  // ttl 60
    Bytes cname = {3, 'w', 'w', 'w'};
    auto tail = qnameExampleCom();  // "example.com."
    cname.insert(cname.end(), tail.begin(), tail.end());
    pushU16b(d, static_cast<uint16_t>(cname.size()));
    d.insert(d.end(), cname.begin(), cname.end());
    // AAAA
    d.push_back(0xC0); d.push_back(0x0C);
    pushU16b(d, 28);   // AAAA
    pushU16b(d, 1);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(1);
    pushU16b(d, 16);
    const uint8_t v6[16] = {0x26, 0x06, 0x28, 0x00, 0x02, 0x20, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0x68};
    d.insert(d.end(), v6, v6 + 16);
    // MX: pref 10, exchange pointer to 12
    d.push_back(0xC0); d.push_back(0x0C);
    pushU16b(d, 15);   // MX
    pushU16b(d, 1);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(0x3C);
    pushU16b(d, 4);    // rdlen: 2 pref + 2-byte compression pointer
    pushU16b(d, 10);
    d.push_back(0xC0); d.push_back(0x0C);

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(3));
    if (m.answers.size() == 3) {
        TA_CHECK_EQ(m.answers[0].type, 5u);
        TA_CHECK_ST(m.answers[0].rdataText, "www.example.com");
        TA_CHECK_EQ(m.answers[1].type, 28u);
        TA_CHECK_ST(m.answers[1].rdataText, "2606:2800:220:1::68");
        TA_CHECK_EQ(m.answers[2].type, 15u);
        TA_CHECK_ST(m.answers[2].rdataText, "10 example.com");
    }
}

TA_TEST(dns_response_txt_record) {
    auto d = dnsHeader(1);
    auto qn = qnameExampleCom();
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 16);  // TXT
    pushU16b(d, 1);
    d.push_back(0xC0); d.push_back(0x0C);
    pushU16b(d, 16);  // TXT
    pushU16b(d, 1);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(0x3C);
    pushU16b(d, 14);  // one character-string: 1 length byte + 13 data bytes
    d.push_back(13);
    const char* txt = "v=spf1 -all";
    d.insert(d.end(), txt, txt + 11);
    d.push_back(' ');
    d.push_back('x');

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(1));
    if (m.answers.size() == 1) {
        TA_CHECK_EQ(m.answers[0].type, 16u);
        TA_CHECK(m.answers[0].rdataText.find("v=spf1 -all") == 0);
    }
}

TA_TEST(dns_response_rcode_and_nxdomain) {
    auto d = dnsHeader(0, 0x8183);  // rcode 3 = NXDOMAIN
    auto qn = qnameExampleCom();
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.rcode, 3u);
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(0));
}

TA_TEST(dns_response_rejects_pointer_loop) {
    // answer name points at itself -> loop guard must trip
    auto d = dnsHeader(1);
    auto qn = qnameExampleCom();
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);
    size_t answerNameAt = d.size();
    d.push_back(0xC0);
    d.push_back(static_cast<uint8_t>(answerNameAt & 0xFF));
    pushU16b(d, 1);
    pushU16b(d, 1);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(1);
    pushU16b(d, 4);
    d.push_back(1); d.push_back(1); d.push_back(1); d.push_back(1);
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::BadPointer);
}

TA_TEST(dns_response_truncated_rdata) {
    auto d = dnsHeader(1);
    auto qn = qnameExampleCom();
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);
    d.push_back(0xC0); d.push_back(0x0C);
    pushU16b(d, 1);
    pushU16b(d, 1);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(1);
    pushU16b(d, 4);
    d.push_back(1); d.push_back(2);  // claims 4 bytes, has 2
    DnsMessage m{};
    TA_CHECK(parseDnsResponse(d.data(), d.size(), &m) != DnsStatus::Ok);
}
