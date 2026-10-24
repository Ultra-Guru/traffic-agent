#include "traffic/md5.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(md5_known_vectors) {
    TA_CHECK(md5SelfCheck());
    TA_CHECK_ST(md5Hex(nullptr, 0), "d41d8cd98f00b204e9800998ecf8427e");
    Bytes empty;
    TA_CHECK_ST(md5Hex(empty.data(), empty.size()), "d41d8cd98f00b204e9800998ecf8427e");
    std::string abc = "abc";
    TA_CHECK_ST(md5Hex(reinterpret_cast<const uint8_t*>(abc.data()), abc.size()),
                "900150983cd24fb0d6963f7d28e17f72");
}

TA_TEST(md5_multi_block_boundaries) {
    // Lengths around the 64-byte block boundary and the 56-byte padding
    // offset; every digest must be 32 lowercase hex chars and stable.
    for (size_t n : {1u, 55u, 56u, 63u, 64u, 65u, 119u, 120u, 128u, 1000u}) {
        Bytes data(n);
        uint32_t x = 12345;
        for (size_t i = 0; i < n; ++i) {
            x = x * 1103515245u + 12345u;
            data[i] = static_cast<uint8_t>(x >> 16);
        }
        std::string h = md5Hex(data.data(), data.size());
        TA_CHECK_EQ(h.size(), static_cast<size_t>(32));
        for (char c : h) {
            TA_CHECK((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'));
        }
        TA_CHECK_ST(md5Hex(data.data(), data.size()), h);  // deterministic
    }
}

TA_TEST(md5_hex_is_lowercase) {
    std::string s = "The quick brown fox jumps over the lazy dog";
    TA_CHECK_ST(md5Hex(reinterpret_cast<const uint8_t*>(s.data()), s.size()),
                "9e107d9d372bb6826bd81d3542a419d6");
}

TA_TEST(md5_digest_bytes) {
    uint8_t digest[16];
    md5Digest(nullptr, 0, digest);
    TA_CHECK_EQ(digest[0], 0xd4);
    TA_CHECK_EQ(digest[15], 0x7e);
}
