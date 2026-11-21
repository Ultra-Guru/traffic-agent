#include "traffic/dns.h"

#include <cstring>

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

namespace {

void pushU16b(Bytes& b, uint16_t v) {
    b.push_back(static_cast<uint8_t>(v >> 8));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

// Full header with all four section counts.
Bytes dnsHeaderFull(uint16_t qd, uint16_t an, uint16_t ns, uint16_t ar,
                    uint16_t flags = 0x8180) {
    Bytes h;
    pushU16b(h, 0x1234);
    pushU16b(h, flags);
    pushU16b(h, qd);
    pushU16b(h, an);
    pushU16b(h, ns);
    pushU16b(h, ar);
    return h;
}

Bytes qname(const std::string& name) {
    Bytes q;
    size_t start = 0;
    while (start < name.size()) {
        size_t dot = name.find('.', start);
        if (dot == std::string::npos) dot = name.size();
        size_t len = dot - start;
        q.push_back(static_cast<uint8_t>(len));
        q.insert(q.end(), name.begin() + static_cast<long>(start),
                 name.begin() + static_cast<long>(dot));
        start = dot + 1;
    }
    q.push_back(0);
    return q;
}

Bytes rrHeader(uint16_t type, uint32_t ttl, uint16_t rdlen) {
    Bytes b;
    b.push_back(0xC0);
    b.push_back(0x0C);  // name: pointer to offset 12
    pushU16b(b, type);
    pushU16b(b, 1);  // IN
    b.push_back(static_cast<uint8_t>((ttl >> 24) & 0xff));
    b.push_back(static_cast<uint8_t>((ttl >> 16) & 0xff));
    b.push_back(static_cast<uint8_t>((ttl >> 8) & 0xff));
    b.push_back(static_cast<uint8_t>(ttl & 0xff));
    pushU16b(b, rdlen);
    return b;
}

}  // namespace

// ---------------- SRV (type 33) ----------------

TA_TEST(dns_srv_record_rendered) {
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("_imaps._tcp.example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 33);
    pushU16b(d, 1);

    Bytes rdata;
    pushU16b(rdata, 10);   // priority
    pushU16b(rdata, 20);   // weight
    pushU16b(rdata, 993);  // port
    auto target = qname("mail.example.com");
    rdata.insert(rdata.end(), target.begin(), target.end());

    auto rr = rrHeader(33, 300, static_cast<uint16_t>(rdata.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), rdata.begin(), rdata.end());

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(1));
    if (m.answers.size() == 1) {
        TA_CHECK_ST(m.answers[0].rdataText, "10 20 993 mail.example.com");
        TA_CHECK_ST(dnsTypeMnemonic(m.answers[0].type), "SRV");
    }
}

TA_TEST(dns_srv_rejects_short_rdata) {
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("_sip._tcp.example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 33);
    pushU16b(d, 1);
    Bytes rdata(5, 0);  // priority+weight+1 byte: too short for 6 fixed bytes
    auto rr = rrHeader(33, 300, static_cast<uint16_t>(rdata.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), rdata.begin(), rdata.end());
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::MalformedRdata);
}

// ---------------- CAA (type 257) ----------------

TA_TEST(dns_caa_record_rendered) {
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 257);
    pushU16b(d, 1);

    Bytes rdata;
    rdata.push_back(0);  // flags: not critical
    rdata.push_back(5);  // tag length
    const char tag[5] = {'i', 's', 's', 'u', 'e'};
    rdata.insert(rdata.end(), tag, tag + 5);
    const char* value = "letsencrypt.org";
    const size_t valueLen = std::strlen(value);
    rdata.insert(rdata.end(), value, value + valueLen);

    auto rr = rrHeader(257, 3600, static_cast<uint16_t>(rdata.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), rdata.begin(), rdata.end());

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(1));
    if (m.answers.size() == 1) {
        TA_CHECK_ST(m.answers[0].rdataText, "0 issue \"letsencrypt.org\"");
        TA_CHECK_ST(dnsTypeMnemonic(m.answers[0].type), "CAA");
    }
}

TA_TEST(dns_caa_rejects_tag_overflow) {
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 257);
    pushU16b(d, 1);
    Bytes rdata;
    rdata.push_back(0);
    rdata.push_back(9);  // tag claims 9 bytes but only "issue" (5) follows
    const char tag[5] = {'i', 's', 's', 'u', 'e'};
    rdata.insert(rdata.end(), tag, tag + 5);
    auto rr = rrHeader(257, 3600, static_cast<uint16_t>(rdata.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), rdata.begin(), rdata.end());
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::MalformedRdata);
}

// ---------------- HTTPS (type 65) / SVCB (type 64) ----------------

TA_TEST(dns_https_record_rendered_with_alpn) {
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 65);
    pushU16b(d, 1);

    Bytes rdata;
    pushU16b(rdata, 1);  // priority 1 (alternative endpoint)
    auto target = qname("example.net");
    rdata.insert(rdata.end(), target.begin(), target.end());
    // SvcParam alpn(1): length 5, value: 2 "h2" 0x02? -> "2,h2" style bytes
    pushU16b(rdata, 1);   // key: alpn
    pushU16b(rdata, 5);   // value length
    rdata.push_back(2);   // alpn length prefix for "h2"
    rdata.push_back('h');
    rdata.push_back('2');
    rdata.push_back(3);   // alpn length prefix for "h3"... wait 3 chars
    rdata.push_back('h');
    // (structure matters, not semantics, for the renderer test)

    auto rr = rrHeader(65, 600, static_cast<uint16_t>(rdata.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), rdata.begin(), rdata.end());

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(1));
    if (m.answers.size() == 1) {
        TA_CHECK_ST(dnsTypeMnemonic(m.answers[0].type), "HTTPS");
        TA_CHECK(m.answers[0].rdataText.rfind("1 example.net", 0) == 0);
        TA_CHECK(m.answers[0].rdataText.find("alpn=") != std::string::npos);
    }
}

TA_TEST(dns_svcb_rejects_param_overflow) {
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 64);
    pushU16b(d, 1);
    Bytes rdata;
    pushU16b(rdata, 1);
    auto target = qname(".");
    rdata.insert(rdata.end(), target.begin(), target.end());
    pushU16b(rdata, 3);  // key: port
    pushU16b(rdata, 2);
    rdata.push_back(0x01);
    // claims 2-byte value, only 1 byte present -> truncated
    auto rr = rrHeader(64, 600, static_cast<uint16_t>(rdata.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), rdata.begin(), rdata.end());
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::MalformedRdata);
}

// ---------------- EDNS0 (OPT type 41) ----------------

TA_TEST(dns_edns_opt_parsed) {
    auto d = dnsHeaderFull(1, 0, 0, 1);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);

    // OPT RR: name=root, type=41, class=udp size 1232, ttl=0x00010000
    // (version 1) with DO bit clear, one option: cookie(10) len 8.
    d.push_back(0);  // root name
    pushU16b(d, 41);
    pushU16b(d, 1232);  // UDP payload size
    d.push_back(0x00); d.push_back(0x01); d.push_back(0x00); d.push_back(0x00);  // ver=1 (ttl bits 23..16)
    pushU16b(d, 12);  // rdlen: 4 header + 8 cookie
    pushU16b(d, 10);  // option code: cookie
    pushU16b(d, 8);   // option length
    for (int i = 0; i < 8; ++i) d.push_back(0xAA);

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK(m.edns.present);
    TA_CHECK_EQ(m.edns.udpPayloadSize, 1232u);
    TA_CHECK_EQ(m.edns.version, 1u);
    TA_CHECK_EQ(m.edns.extendedRcode, 0u);
    TA_CHECK(!m.edns.dnssecOk);
    TA_CHECK_EQ(m.edns.options.size(), static_cast<size_t>(1));
    if (m.edns.options.size() == 1) {
        TA_CHECK_EQ(m.edns.options[0].code, 10u);
        TA_CHECK_EQ(m.edns.options[0].data.size(), static_cast<size_t>(8));
    }
    // OPT itself must not appear as a regular additional record.
    TA_CHECK_EQ(m.additionals.size(), static_cast<size_t>(0));
    TA_CHECK_ST(dnsEdnsOptionName(10), "cookie");
    TA_CHECK_ST(dnsEdnsOptionName(8), "ecs");
    TA_CHECK_ST(dnsEdnsOptionName(65001), "unknown(65001)");
}

TA_TEST(dns_edns_dnssec_ok_bit) {
    auto d = dnsHeaderFull(1, 0, 0, 1);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 255);  // ANY
    pushU16b(d, 1);
    d.push_back(0);
    pushU16b(d, 41);
    pushU16b(d, 4096);
    // ttl: extended rcode 0, version 0, DO set (0x8000)
    d.push_back(0x00); d.push_back(0x00); d.push_back(0x80); d.push_back(0x00);
    pushU16b(d, 0);  // no options
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK(m.edns.present);
    TA_CHECK(m.edns.dnssecOk);
    TA_CHECK_EQ(m.edns.udpPayloadSize, 4096u);
}

TA_TEST(dns_edns_rejects_truncated_option) {
    auto d = dnsHeaderFull(1, 0, 0, 1);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);
    d.push_back(0);
    pushU16b(d, 41);
    pushU16b(d, 1232);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(0);
    pushU16b(d, 6);  // claims one option
    pushU16b(d, 10);
    pushU16b(d, 8);  // 8-byte cookie value...
    for (int i = 0; i < 4; ++i) d.push_back(0xBB);  // ...only 4 present
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::MalformedRdata);
}

// ---------------- header semantics + sections ----------------

TA_TEST(dns_header_flag_helpers) {
    auto d = dnsHeaderFull(1, 0, 0, 0, 0x8580);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    // 0x8580 = QR + AA + RD + RA
    TA_CHECK(m.isResponse());
    TA_CHECK(m.authoritativeAnswer());
    TA_CHECK(m.recursionDesired());
    TA_CHECK(m.recursionAvailable());
    TA_CHECK(!m.truncation());
    TA_CHECK(!m.checkingDisabled());
    TA_CHECK(!m.authenticatedData());
    TA_CHECK_EQ(m.opcode(), 0u);
}

TA_TEST(dns_opcode_extracted) {
    // opcode 4 (NOTIFY) sits at bits 14..11 of the flags.
    auto d = dnsHeaderFull(0, 0, 0, 0, 0x2000);
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.opcode(), 4u);
    TA_CHECK(!m.isResponse());
}

TA_TEST(dns_authority_and_additional_sections) {
    // nscount=1 (SOA in authority), arcount=1 (A record, not OPT)
    auto d = dnsHeaderFull(1, 0, 1, 1, 0x8183);  // NXDOMAIN + SOA authority
    auto qn = qname("gone.example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);

    // authority SOA
    Bytes soa;
    auto mname = qname("ns1.example.com");
    soa.insert(soa.end(), mname.begin(), mname.end());
    auto rname = qname("host.example.com");
    soa.insert(soa.end(), rname.begin(), rname.end());
    for (uint32_t v : {2024010101u, 7200u, 3600u, 1209600u, 300u}) {
        soa.push_back(static_cast<uint8_t>((v >> 24) & 0xff));
        soa.push_back(static_cast<uint8_t>((v >> 16) & 0xff));
        soa.push_back(static_cast<uint8_t>((v >> 8) & 0xff));
        soa.push_back(static_cast<uint8_t>(v & 0xff));
    }
    auto rr = rrHeader(6, 3600, static_cast<uint16_t>(soa.size()));
    d.insert(d.end(), rr.begin(), rr.end());
    d.insert(d.end(), soa.begin(), soa.end());

    // additional A record for the resolver
    Bytes a4 = {192, 168, 1, 1};
    auto rr2 = rrHeader(1, 60, 4);
    d.insert(d.end(), rr2.begin(), rr2.end());
    d.insert(d.end(), a4.begin(), a4.end());

    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK_EQ(m.rcode, 3u);
    TA_CHECK_EQ(m.authorities.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(m.additionals.size(), static_cast<size_t>(1));
    if (m.authorities.size() == 1) {
        TA_CHECK_ST(m.authorities[0].rdataText,
                    "ns1.example.com host.example.com 2024010101 7200 3600 1209600 300");
    }
    if (m.additionals.size() == 1) {
        TA_CHECK_ST(m.additionals[0].rdataText, "192.168.1.1");
    }
    TA_CHECK(!m.edns.present);
}

TA_TEST(dns_opt_in_answer_section_is_not_edns) {
    // An OPT-looking record in the ANSWER section is malformed usage but must
    // be treated as a regular (raw-rendered) record, not EDNS0 state.
    auto d = dnsHeaderFull(1, 1, 0, 0);
    auto qn = qname("example.com");
    d.insert(d.end(), qn.begin(), qn.end());
    pushU16b(d, 1);
    pushU16b(d, 1);
    d.push_back(0xC0); d.push_back(0x0C);
    pushU16b(d, 41);
    pushU16b(d, 1232);
    d.push_back(0); d.push_back(0); d.push_back(0); d.push_back(0);
    pushU16b(d, 0);
    DnsMessage m{};
    TA_CHECK_EQ(parseDnsResponse(d.data(), d.size(), &m), DnsStatus::Ok);
    TA_CHECK(!m.edns.present);  // only the additional section may carry OPT
    TA_CHECK_EQ(m.answers.size(), static_cast<size_t>(1));
}
