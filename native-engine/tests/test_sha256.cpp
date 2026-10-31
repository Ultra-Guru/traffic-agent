#include "traffic/sha256.h"

#include <cstring>
#include <string>

#include "test_framework.hpp"

using namespace traffic;

namespace {

// NIST FIPS 180-4 vectors cross-validated with python3 hashlib.
const struct {
    const char* input;
    const char* hex;
} kVectors[] = {
    {"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
    {"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
     "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"},
    {"abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmno"
     "ijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu",
     "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1"},
};

std::string repeat(char c, size_t n) {
    return std::string(n, c);
}

// Plain lowercase hex of a digest (NOT a further hash).
std::string hexOf(const uint8_t* data, size_t len) {
    static const char kHex[] = "0123456789abcdef";
    std::string out;
    out.reserve(len * 2);
    for (size_t i = 0; i < len; ++i) {
        out.push_back(kHex[data[i] >> 4]);
        out.push_back(kHex[data[i] & 0x0f]);
    }
    return out;
}

}  // namespace

TA_TEST(sha256_nist_vectors) {
    for (const auto& v : kVectors) {
        TA_CHECK_ST(sha256Hex(reinterpret_cast<const uint8_t*>(v.input), std::strlen(v.input)),
                    v.hex);
    }
}

TA_TEST(sha256_block_boundaries) {
    // 55 'a': the pad byte lands on the 56-byte boundary slot.
    TA_CHECK_ST(sha256Hex(reinterpret_cast<const uint8_t*>(repeat('a', 55).data()), 55),
                "9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318");
    // 56 'a': padding must spill into a second block.
    TA_CHECK_ST(sha256Hex(reinterpret_cast<const uint8_t*>(repeat('a', 56).data()), 56),
                "b35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a");
    // 63 'a': the pad byte forces the length field into a second block.
    TA_CHECK_ST(sha256Hex(reinterpret_cast<const uint8_t*>(repeat('a', 63).data()), 63),
                "7d3e74a05d7db15bce4ad9ec0658ea98e3f06eeecf16b4c6fff2da457ddc2f34");
    TA_CHECK_ST(sha256Hex(reinterpret_cast<const uint8_t*>(repeat('a', 64).data()), 64),
                "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb");
    // 1000 'a': multi-block message exercise.
    TA_CHECK_ST(sha256Hex(reinterpret_cast<const uint8_t*>(repeat('a', 1000).data()), 1000),
                "41edece42d63e8d9bf515a9ba6932e1c20cbc9f5a5d134645adb5db1b9737ea3");
}

TA_TEST(sha256_stream_matches_oneshot) {
    const std::string msg = "streamed-message-with-several-chunks-of-varying-size";
    const std::string expected = sha256Hex(reinterpret_cast<const uint8_t*>(msg.data()), msg.size());

    // Every chunk split must produce the identical digest.
    for (size_t cut = 1; cut < msg.size(); cut += 7) {
        Sha256Stream s;
        s.update(reinterpret_cast<const uint8_t*>(msg.data()), cut);
        s.update(reinterpret_cast<const uint8_t*>(msg.data() + cut), msg.size() - cut);
        uint8_t digest[32];
        s.finish(digest);
        TA_CHECK_ST(hexOf(digest, 32), expected);
    }
}

TA_TEST(sha256_stream_byte_by_byte) {
    const std::string msg = "one byte at a time, 64+ total to cross a block";
    const std::string expected = sha256Hex(reinterpret_cast<const uint8_t*>(msg.data()), msg.size());
    Sha256Stream s;
    for (char c : msg) {
        uint8_t b = static_cast<uint8_t>(c);
        s.update(&b, 1);
    }
    uint8_t digest[32];
    s.finish(digest);
    TA_CHECK_ST(hexOf(digest, 32), expected);
}

TA_TEST(sha256_self_check_helper) {
    TA_CHECK(sha256SelfCheck());
}
