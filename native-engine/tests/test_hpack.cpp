#include "traffic/hpack.h"

#include <string>
#include <vector>

#include "test_framework.hpp"

using namespace traffic;

namespace {

std::vector<uint8_t> hexBytes(const char* hex) {
    std::vector<uint8_t> out;
    size_t i = 0;
    while (hex[i] != '\0' && hex[i + 1] != '\0') {
        auto nib = [](char c) -> uint8_t {
            if (c >= '0' && c <= '9') return static_cast<uint8_t>(c - '0');
            return static_cast<uint8_t>(c - 'a' + 10);
        };
        out.push_back(static_cast<uint8_t>((nib(hex[i]) << 4) | nib(hex[i + 1])));
        i += 2;
    }
    return out;
}

std::vector<HpackHeader> decode(const std::vector<uint8_t>& block) {
    std::vector<HpackHeader> out;
    size_t consumed = 0;
    TA_CHECK_EQ(decodeHpack(block.data(), block.size(), &out, &consumed), HpackStatus::Ok);
    TA_CHECK_EQ(consumed, block.size());
    return out;
}

}  // namespace

TA_TEST(hpack_static_table_shape) {
    TA_CHECK_EQ(hpackStaticTableSize(), static_cast<size_t>(61));
    TA_CHECK_ST(hpackStaticName(1), ":authority");
    TA_CHECK_ST(hpackStaticValue(1), "");
    TA_CHECK_ST(hpackStaticName(2), ":method");
    TA_CHECK_ST(hpackStaticValue(2), "GET");
    TA_CHECK_ST(hpackStaticName(3), ":method");
    TA_CHECK_ST(hpackStaticValue(3), "POST");
    TA_CHECK_ST(hpackStaticName(4), ":path");
    TA_CHECK_ST(hpackStaticValue(4), "/");
    TA_CHECK_ST(hpackStaticName(6), ":scheme");
    TA_CHECK_ST(hpackStaticValue(6), "http");
    TA_CHECK_ST(hpackStaticName(7), ":scheme");
    TA_CHECK_ST(hpackStaticValue(7), "https");
    TA_CHECK_ST(hpackStaticName(8), ":status");
    TA_CHECK_ST(hpackStaticValue(8), "200");
    TA_CHECK_ST(hpackStaticValue(14), "500");
    TA_CHECK_ST(hpackStaticName(16), "accept-encoding");
    TA_CHECK_ST(hpackStaticName(28), "content-length");
    TA_CHECK_ST(hpackStaticName(61), "www-authenticate");
    TA_CHECK_ST(hpackStaticValue(61), "");  // RFC gives no example value
    TA_CHECK(hpackStaticName(0) == nullptr);
    TA_CHECK(hpackStaticName(62) == nullptr);
}

// RFC 7541 Appendix C.2.1 — literal with indexing, no Huffman.
TA_TEST(hpack_rfc_c21_vector) {
    // 82 86 84 01 0f ...: :method GET, :scheme http, :path /,
    // :authority www.example.com (last one literal, no huffman)
    std::vector<uint8_t> block = hexBytes("828684410f7777772e6578616d706c652e636f6d");
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(4));
    TA_CHECK_ST(h[0].name, ":method");
    TA_CHECK_ST(h[0].value, "GET");
    TA_CHECK_ST(h[1].name, ":scheme");
    TA_CHECK_ST(h[1].value, "http");
    TA_CHECK_ST(h[2].name, ":path");
    TA_CHECK_ST(h[2].value, "/");
    TA_CHECK_ST(h[3].name, ":authority");
    TA_CHECK_ST(h[3].value, "www.example.com");
}

// Huffman-coded literal "www.example.com" (the well-known code f1e3c2e5…).
TA_TEST(hpack_huffman_literal_vector) {
    std::vector<uint8_t> block = hexBytes("828684418cf1e3c2e5f23a6ba0ab90f4ff");
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(4));
    TA_CHECK_ST(h[3].name, ":authority");
    TA_CHECK_ST(h[3].value, "www.example.com");
}

// RFC 7541 Appendix C.5.1 — first response, everything Huffman-coded.
TA_TEST(hpack_rfc_c51_response_vector) {
    std::vector<uint8_t> block = hexBytes(
        "488264025885aec3771a4b6196d07abe941054d444a8200595040b8166e082a62d1bff"
        "6e919d29ad171863c78f0b97c8e9ae82ae43d3");
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(4));
    TA_CHECK_ST(h[0].name, ":status");
    TA_CHECK_ST(h[0].value, "302");
    TA_CHECK_ST(h[1].name, "cache-control");
    TA_CHECK_ST(h[1].value, "private");
    TA_CHECK_ST(h[2].name, "date");
    TA_CHECK_ST(h[2].value, "Mon, 21 Oct 2013 20:13:21 GMT");
    TA_CHECK_ST(h[3].name, "location");
    TA_CHECK_ST(h[3].value, "https://www.example.com");
}

// RFC 7541 Appendix C.4.1 + C.4.2 in one block: the second request's 0xBE
// references the dynamic entry inserted by the first one.
TA_TEST(hpack_rfc_c42_second_request) {
    std::vector<uint8_t> block =
        hexBytes("828684410f7777772e6578616d706c652e636f6d" "828684be5886a8eb10649cbf");
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(9));
    TA_CHECK_ST(h[0].name, ":method");
    TA_CHECK_ST(h[0].value, "GET");
    TA_CHECK_ST(h[3].name, ":authority");
    TA_CHECK_ST(h[3].value, "www.example.com");
    // second request: :authority comes from dynamic entry 62
    TA_CHECK_ST(h[7].name, ":authority");
    TA_CHECK_ST(h[7].value, "www.example.com");
    TA_CHECK_ST(h[8].name, "cache-control");
    TA_CHECK_ST(h[8].value, "no-cache");
}

TA_TEST(hpack_huffman_encode_known_vector) {
    auto enc = huffmanEncode("www.example.com");
    std::vector<uint8_t> want = hexBytes("f1e3c2e5f23a6ba0ab90f4ff");
    TA_CHECK_EQ(enc.size(), want.size());
    TA_CHECK(enc == want);
    TA_CHECK_EQ(huffmanEncode("").size(), static_cast<size_t>(0));
    // "a" codes to 5 bits '00011'; EOS padding fills the rest with ones -> 0x1F.
    auto one = huffmanEncode("a");
    TA_CHECK_EQ(one.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(one[0], 0x1F);
}

TA_TEST(hpack_huffman_roundtrip_random) {
    // Deterministic LCG string generator; every string must survive
    // encode -> literal-with-huffman -> decode.
    uint32_t seed = 12345;
    auto next = [&seed]() {
        seed = seed * 1103515245u + 12345u;
        return (seed >> 16) & 0xFF;
    };
    for (int iter = 0; iter < 64; ++iter) {
        size_t n = next() % 97;
        std::string s;
        for (size_t i = 0; i < n; ++i) {
            char c = static_cast<char>(32 + (next() % 95));  // printable, no EOS
            s.push_back(c);
        }
        auto enc = huffmanEncode(s);
        // literal header without indexing, new name, huffman on:
        // 0x00 <len|huffman bit> <bytes>
        std::vector<uint8_t> block;
        block.push_back(0x00);
        size_t len = enc.size();
        if (len < 127) {
            block.push_back(static_cast<uint8_t>(0x80u | len));
        } else {
            // 7-bit prefix integer continuation (RFC 7541 section 5.1)
            block.push_back(0xFF);
            size_t rem = len - 127;
            while (rem >= 128) {
                block.push_back(static_cast<uint8_t>(0x80u | (rem & 0x7Fu)));
                rem >>= 7;
            }
            block.push_back(static_cast<uint8_t>(rem));
        }
        block.insert(block.end(), enc.begin(), enc.end());
        // value: plain non-huffman literal (same string for simplicity)
        if (s.size() < 127) {
            block.push_back(static_cast<uint8_t>(s.size()));
        } else {
            block.push_back(127);
            size_t rem = s.size() - 127;
            while (rem >= 128) {
                block.push_back(static_cast<uint8_t>(0x80u | (rem & 0x7Fu)));
                rem >>= 7;
            }
            block.push_back(static_cast<uint8_t>(rem));
        }
        block.insert(block.end(), s.begin(), s.end());
        std::vector<HpackHeader> out;
        size_t consumed = 0;
        TA_CHECK_EQ(decodeHpack(block.data(), block.size(), &out, &consumed), HpackStatus::Ok);
        TA_CHECK_EQ(consumed, block.size());
        TA_CHECK_EQ(out.size(), static_cast<size_t>(1));
        if (out.size() == 1) TA_CHECK_ST(out[0].value, s);
    }
}

TA_TEST(hpack_dynamic_table_insert_and_reference) {
    // One block: literal-with-incremental-indexing (0x40) inserting
    // custom-header, then an indexed reference to it (62 = first dynamic).
    std::vector<uint8_t> block;
    block.push_back(0x40);
    block.push_back(13);
    const char* n = "custom-header";
    block.insert(block.end(), n, n + 13);
    block.push_back(12);
    const char* v = "custom-value";
    block.insert(block.end(), v, v + 12);
    block.push_back(0xBE);  // dynamic index 62
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(2));
    TA_CHECK_ST(h[0].name, "custom-header");
    TA_CHECK_ST(h[0].value, "custom-value");
    TA_CHECK_ST(h[1].name, "custom-header");
    TA_CHECK_ST(h[1].value, "custom-value");
}

TA_TEST(hpack_dynamic_table_eviction) {
    // Shrink the dynamic table to a tiny size, then insert entries: older
    // ones must be evicted (index 62 then points at the newest entry).
    std::vector<uint8_t> block;
    block.push_back(0x20);  // dynamic table size update -> 0
    block.push_back(0x40);
    block.push_back(4);
    const char* n = "dddd";
    block.insert(block.end(), n, n + 4);
    block.push_back(4);
    const char* v = "1111";
    block.insert(block.end(), v, v + 4);
    block.push_back(0x40);
    block.push_back(4);
    const char* n2 = "eeee";
    block.insert(block.end(), n2, n2 + 4);
    block.push_back(4);
    const char* v2 = "2222";
    block.insert(block.end(), v2, v2 + 4);
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(2));
    TA_CHECK_ST(h[1].name, "eeee");
    TA_CHECK_ST(h[1].value, "2222");
}

TA_TEST(hpack_rejects_bad_index) {
    // indexed field, integer 127 + 0 continuation -> index 127, beyond any table
    std::vector<uint8_t> block = {0xFF, 0x00};
    std::vector<HpackHeader> out;
    size_t consumed = 0;
    TA_CHECK_EQ(decodeHpack(block.data(), block.size(), &out, &consumed),
                HpackStatus::BadIndex);
    // a lone continuation byte is a truncated integer
    std::vector<uint8_t> cont = {0xFF};
    TA_CHECK_EQ(decodeHpack(cont.data(), cont.size(), &out, &consumed),
                HpackStatus::MalformedInteger);
    // an empty block is valid: zero headers, zero bytes consumed
    static const uint8_t kEmptyBlock[1] = {0};
    TA_CHECK_EQ(decodeHpack(kEmptyBlock, 0, &out, &consumed), HpackStatus::Ok);
    TA_CHECK_EQ(out.size(), static_cast<size_t>(0));
    TA_CHECK_EQ(consumed, static_cast<size_t>(0));
}

TA_TEST(hpack_rejects_truncated_string) {
    std::vector<uint8_t> block = {0x40, 5, 'a', 'b'};  // claims 5 bytes, has 2
    std::vector<HpackHeader> out;
    size_t consumed = 0;
    TA_CHECK_EQ(decodeHpack(block.data(), block.size(), &out, &consumed),
                HpackStatus::TooShort);
}

TA_TEST(hpack_encode_decode_roundtrip) {
    std::vector<HpackHeader> in;
    in.push_back({":method", "POST"});
    in.push_back({":path", "/submit"});
    in.push_back({"x-custom", "value with spaces"});
    in.push_back({"content-type", "application/json"});
    auto block = encodeHpack(in);
    auto out = decode(block);
    TA_CHECK_EQ(out.size(), in.size());
    for (size_t i = 0; i < in.size(); ++i) {
        TA_CHECK_ST(out[i].name, in[i].name);
        TA_CHECK_ST(out[i].value, in[i].value);
    }
}

TA_TEST(hpack_string_with_high_bytes_survives) {
    // Latin-1 payload bytes must round-trip through the non-Huffman path.
    std::vector<uint8_t> block;
    block.push_back(0x40);
    block.push_back(3);
    const char n[3] = {'x', 'y', 'z'};
    block.insert(block.end(), n, n + 3);
    block.push_back(4);
    const uint8_t v[4] = {0xC3, 0xA9, 0xE2, 0x82};  // utf-8-ish high bytes
    block.insert(block.end(), v, v + 4);
    auto h = decode(block);
    TA_CHECK_EQ(h.size(), static_cast<size_t>(1));
    TA_CHECK_EQ(h[0].value.size(), static_cast<size_t>(4));
    TA_CHECK_EQ(static_cast<unsigned char>(h[0].value[0]), 0xC3);
}
