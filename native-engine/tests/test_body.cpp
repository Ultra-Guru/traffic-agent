#include "traffic/body.h"

#include <cstring>
#include <string>
#include <vector>

#include "test_framework.hpp"

extern "C" {
#include <zlib.h>
}

using namespace traffic;

namespace {

std::vector<uint8_t> strB(const std::string& s) { return std::vector<uint8_t>(s.begin(), s.end()); }

std::string toStr(const std::vector<uint8_t>& b) { return std::string(b.begin(), b.end()); }

std::vector<uint8_t> gzipBytes(const std::string& s) {
    z_stream zs{};
    deflateInit2(&zs, Z_DEFAULT_COMPRESSION, Z_DEFLATED, 15 + 16, 8, Z_DEFAULT_STRATEGY);
    zs.next_in = reinterpret_cast<Bytef*>(const_cast<char*>(s.data()));
    zs.avail_in = static_cast<uInt>(s.size());
    std::vector<uint8_t> out;
    uint8_t buf[4096];
    do {
        zs.next_out = buf;
        zs.avail_out = sizeof(buf);
        deflate(&zs, Z_FINISH);
        out.insert(out.end(), buf, buf + (sizeof(buf) - zs.avail_out));
    } while (zs.avail_out == 0);
    deflateEnd(&zs);
    return out;
}

std::vector<uint8_t> zlibBytes(const std::string& s) {
    z_stream zs{};
    deflateInit(&zs, Z_DEFAULT_COMPRESSION);
    zs.next_in = reinterpret_cast<Bytef*>(const_cast<char*>(s.data()));
    zs.avail_in = static_cast<uInt>(s.size());
    std::vector<uint8_t> out;
    uint8_t buf[4096];
    do {
        zs.next_out = buf;
        zs.avail_out = sizeof(buf);
        deflate(&zs, Z_FINISH);
        out.insert(out.end(), buf, buf + (sizeof(buf) - zs.avail_out));
    } while (zs.avail_out == 0);
    deflateEnd(&zs);
    return out;
}

std::vector<uint8_t> rawDeflateBytes(const std::string& s) {
    z_stream zs{};
    deflateInit2(&zs, Z_DEFAULT_COMPRESSION, Z_DEFLATED, -15, 8, Z_DEFAULT_STRATEGY);
    zs.next_in = reinterpret_cast<Bytef*>(const_cast<char*>(s.data()));
    zs.avail_in = static_cast<uInt>(s.size());
    std::vector<uint8_t> out;
    uint8_t buf[4096];
    do {
        zs.next_out = buf;
        zs.avail_out = sizeof(buf);
        deflate(&zs, Z_FINISH);
        out.insert(out.end(), buf, buf + (sizeof(buf) - zs.avail_out));
    } while (zs.avail_out == 0);
    deflateEnd(&zs);
    return out;
}

}  // namespace

TA_TEST(chunked_decodes_simple_body) {
    auto in = strB("5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n");
    std::vector<uint8_t> out;
    size_t consumed = 0;
    std::vector<std::pair<std::string, std::string>> trailers;
    TA_CHECK_EQ(decodeChunked(in.data(), in.size(), &out, &consumed, &trailers),
                ChunkedStatus::Complete);
    TA_CHECK_ST(toStr(out), "hello world");
    TA_CHECK_EQ(consumed, in.size());
    TA_CHECK(trailers.empty());
}

TA_TEST(chunked_skips_extensions_and_keeps_trailers) {
    auto in = strB("5;ext=1;foo=bar\r\nhello\r\n0\r\nX-Trail: yes\r\nX-B: b\r\n\r\n");
    std::vector<uint8_t> out;
    size_t consumed = 0;
    std::vector<std::pair<std::string, std::string>> trailers;
    TA_CHECK_EQ(decodeChunked(in.data(), in.size(), &out, &consumed, &trailers),
                ChunkedStatus::Complete);
    TA_CHECK_ST(toStr(out), "hello");
    bool found = false;
    for (auto& kv : trailers) {
        if (kv.first == "X-Trail" && kv.second == "yes") found = true;
    }
    TA_CHECK(found);
}

TA_TEST(chunked_partial_buffer_requests_more) {
    auto in = strB("5\r\nhel");
    std::vector<uint8_t> out;
    size_t consumed = 0;
    std::vector<std::pair<std::string, std::string>> trailers;
    TA_CHECK_EQ(decodeChunked(in.data(), in.size(), &out, &consumed, &trailers),
                ChunkedStatus::NeedMore);
    auto in2 = strB("5\r\nhello\r");
    TA_CHECK_EQ(decodeChunked(in2.data(), in2.size(), &out, &consumed, &trailers),
                ChunkedStatus::NeedMore);
}

TA_TEST(chunked_rejects_bad_hex_size) {
    auto in = strB("zz\r\nhello\r\n0\r\n\r\n");
    std::vector<uint8_t> out;
    size_t consumed = 0;
    std::vector<std::pair<std::string, std::string>> trailers;
    TA_CHECK_EQ(decodeChunked(in.data(), in.size(), &out, &consumed, &trailers),
                ChunkedStatus::Malformed);
}

TA_TEST(chunked_rejects_missing_terminator) {
    auto in = strB("5\r\nhello\r\n");  // no final 0-chunk
    std::vector<uint8_t> out;
    size_t consumed = 0;
    std::vector<std::pair<std::string, std::string>> trailers;
    TA_CHECK_EQ(decodeChunked(in.data(), in.size(), &out, &consumed, &trailers),
                ChunkedStatus::NeedMore);
}

TA_TEST(chunked_handles_crlf_inside_chunk_data) {
    auto in = strB("6\r\na\r\nb\r\n\r\n0\r\n\r\n");
    std::vector<uint8_t> out;
    size_t consumed = 0;
    std::vector<std::pair<std::string, std::string>> trailers;
    TA_CHECK_EQ(decodeChunked(in.data(), in.size(), &out, &consumed, &trailers),
                ChunkedStatus::Complete);
    TA_CHECK_ST(toStr(out), "a\r\nb\r\n");
}

TA_TEST(gzip_body_decompresses) {
    std::string payload = "{\"ok\":true,\"items\":[1,2,3]}";
    auto gz = gzipBytes(payload);
    std::vector<uint8_t> out;
    TA_CHECK(decompressBody(gz.data(), gz.size(), "gzip", &out));
    TA_CHECK_ST(toStr(out), payload);
    // x-gzip alias must work too.
    std::vector<uint8_t> out2;
    TA_CHECK(decompressBody(gz.data(), gz.size(), "x-gzip", &out2));
    TA_CHECK_ST(toStr(out2), payload);
}

TA_TEST(deflate_body_zlib_and_raw_fallback) {
    std::string payload = "deflate me, raw or wrapped";
    auto z = zlibBytes(payload);
    std::vector<uint8_t> out;
    TA_CHECK(decompressBody(z.data(), z.size(), "deflate", &out));
    TA_CHECK_ST(toStr(out), payload);
    auto raw = rawDeflateBytes(payload);
    std::vector<uint8_t> out2;
    TA_CHECK(decompressBody(raw.data(), raw.size(), "deflate", &out2));
    TA_CHECK_ST(toStr(out2), payload);
}

TA_TEST(identity_passthrough) {
    auto in = strB("plain text");
    std::vector<uint8_t> out;
    TA_CHECK(decompressBody(in.data(), in.size(), "", &out));
    TA_CHECK_ST(toStr(out), "plain text");
    TA_CHECK(decompressBody(in.data(), in.size(), "identity", &out));
    TA_CHECK_ST(toStr(out), "plain text");
}

TA_TEST(gzip_garbage_fails_cleanly) {
    std::vector<uint8_t> garbage = {0x1f, 0x8b, 0x08, 0x00, 'g', 'a', 'r', 'b'};
    std::vector<uint8_t> out;
    TA_CHECK(!decompressBody(garbage.data(), garbage.size(), "gzip", &out));
}

TA_TEST(mime_sniff_magic_bytes) {
    TA_CHECK_ST(sniffMime(nullptr, 0, "text/html"), "text/html");  // empty body keeps declared
    std::vector<uint8_t> png = {0x89, 'P', 'N', 'G', 0x0D, 0x0A, 0x1A, 0x0A};
    TA_CHECK_ST(sniffMime(png.data(), png.size(), "application/octet-stream"), "image/png");
    std::vector<uint8_t> jpg = {0xFF, 0xD8, 0xFF, 0xE0, 0, 0};
    TA_CHECK_ST(sniffMime(jpg.data(), jpg.size(), ""), "image/jpeg");
    std::vector<uint8_t> gif = {'G', 'I', 'F', '8', '9', 'a'};
    TA_CHECK_ST(sniffMime(gif.data(), gif.size(), ""), "image/gif");
    std::vector<uint8_t> webp = {'R', 'I', 'F', 'F', 0, 0, 0, 0, 'W', 'E', 'B', 'P'};
    TA_CHECK_ST(sniffMime(webp.data(), webp.size(), ""), "image/webp");
    std::vector<uint8_t> pdf = {'%', 'P', 'D', 'F', '-', '1', '.', '7'};
    TA_CHECK_ST(sniffMime(pdf.data(), pdf.size(), ""), "application/pdf");
    std::vector<uint8_t> zip = {'P', 'K', 0x03, 0x04, 0, 0, 0, 0};
    TA_CHECK_ST(sniffMime(zip.data(), zip.size(), ""), "application/zip");
    std::vector<uint8_t> woff2 = {'w', 'O', 'F', '2', 0, 0, 0, 0};
    TA_CHECK_ST(sniffMime(woff2.data(), woff2.size(), ""), "font/woff2");
}

TA_TEST(mime_sniff_text_heuristics) {
    std::string txt = "just some plain ascii text lines\n";
    TA_CHECK_ST(sniffMime(reinterpret_cast<const uint8_t*>(txt.data()), txt.size(), ""),
                "text/plain");
    // Binary (NUL early) without known magic -> octet-stream.
    std::vector<uint8_t> bin = {'a', 'b', 0x00, 'c'};
    TA_CHECK_ST(sniffMime(bin.data(), bin.size(), ""), "application/octet-stream");
    // Declared json is preserved even though the body is sniffable text.
    std::string js = "{\"a\":1}";
    TA_CHECK_ST(sniffMime(reinterpret_cast<const uint8_t*>(js.data()), js.size(),
                          "application/json"),
                "application/json");
}
