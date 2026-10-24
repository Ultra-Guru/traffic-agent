#include "traffic/http1.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(http1_parses_get_request) {
    std::string raw =
        "GET /path?x=1 HTTP/1.1\r\n"
        "Host: api.example.com\r\n"
        "User-Agent: ta-test\r\n"
        "\r\n";
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b.data(), b.size(), &r), Http1Status::Ok);
    TA_CHECK_ST(r.method, "GET");
    TA_CHECK_ST(r.target, "/path?x=1");
    TA_CHECK_ST(r.version, "HTTP/1.1");
    TA_CHECK_ST(r.headers.get("host"), "api.example.com");  // case-insensitive
    TA_CHECK_ST(r.headers.get("HOST"), "api.example.com");
    TA_CHECK(r.keepAlive);
    TA_CHECK_EQ(r.headers.size(), static_cast<size_t>(2));
    TA_CHECK_EQ(r.headerEnd, raw.size());
}

TA_TEST(http1_parses_post_with_content_length) {
    std::string raw =
        "POST /submit HTTP/1.1\r\n"
        "Host: h\r\n"
        "Content-Length: 5\r\n"
        "\r\nhello";
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b.data(), b.size(), &r), Http1Status::Ok);
    TA_CHECK_ST(r.method, "POST");
    TA_CHECK_EQ(r.contentLength, static_cast<size_t>(5));
    TA_CHECK(!r.chunked);
}

TA_TEST(http1_detects_chunked_and_close) {
    std::string raw =
        "POST /c HTTP/1.1\r\n"
        "Host: h\r\n"
        "Transfer-Encoding: chunked\r\n"
        "Connection: close\r\n"
        "\r\n";
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b.data(), b.size(), &r), Http1Status::Ok);
    TA_CHECK(r.chunked);
    TA_CHECK(!r.keepAlive);
}

TA_TEST(http1_default_keepalive_per_version) {
    std::string v10 = "GET / HTTP/1.0\r\nHost: h\r\n\r\n";
    auto b10 = tb::str(v10);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b10.data(), b10.size(), &r), Http1Status::Ok);
    TA_CHECK(!r.keepAlive);  // HTTP/1.0 defaults to close
}

TA_TEST(http1_allows_empty_header_block) {
    std::string raw = "GET / HTTP/1.1\r\n\r\n";
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b.data(), b.size(), &r), Http1Status::Ok);
    TA_CHECK_EQ(r.headers.size(), static_cast<size_t>(0));
    TA_CHECK_EQ(r.headerEnd, raw.size());
}

TA_TEST(http1_rejects_bad_content_length) {
    std::string raw = "POST / HTTP/1.1\r\nHost: h\r\nContent-Length: abc\r\n\r\n";
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b.data(), b.size(), &r), Http1Status::BadContentLength);
}

TA_TEST(http1_rejects_incomplete_headers) {
    std::string raw = "GET / HTTP/1.1\r\nHost: h\r\n";  // no CRLFCRLF
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK_EQ(parseHttpRequest(b.data(), b.size(), &r), Http1Status::TooShort);
}

TA_TEST(http1_rejects_malformed_request_line) {
    std::string raw = "GARBAGE\r\n\r\n";
    auto b = tb::str(raw);
    Http1Request r{};
    TA_CHECK(parseHttpRequest(b.data(), b.size(), &r) != Http1Status::Ok);
}

TA_TEST(http1_parses_response) {
    std::string raw =
        "HTTP/1.1 404 Not Found\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 18\r\n"
        "\r\n{\"error\":\"missing\"}";
    auto b = tb::str(raw);
    Http1Response r{};
    TA_CHECK_EQ(parseHttpResponse(b.data(), b.size(), &r), Http1Status::Ok);
    TA_CHECK_ST(r.version, "HTTP/1.1");
    TA_CHECK_EQ(r.status, 404);
    TA_CHECK_ST(r.reason, "Not Found");
    TA_CHECK_ST(r.headers.get("content-type"), "application/json");
    TA_CHECK_EQ(r.contentLength, static_cast<size_t>(18));
    TA_CHECK(r.keepAlive);
}

TA_TEST(http1_response_rejects_non_numeric_status) {
    std::string raw = "HTTP/1.1 OK Not Found\r\n\r\n";
    auto b = tb::str(raw);
    Http1Response r{};
    TA_CHECK(parseHttpResponse(b.data(), b.size(), &r) != Http1Status::Ok);
}
