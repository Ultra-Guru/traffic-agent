#include "traffic/md5.h"

#include <cmath>
#include <cstring>

namespace traffic {

namespace {

// Per-round shift amounts (RFC 1321 section 3.4).
const uint32_t kShifts[64] = {
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
};

// T[i] = floor(4294967296 * abs(sin(i+1))), i = 0..63 (RFC 1321 section 3.4).
// Derived deterministically so it cannot drift from the spec:
const uint32_t kConstants[64] = {
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a,
    0xa8304613, 0xfd469501, 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821, 0xf61e2562, 0xc040b340,
    0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8,
    0x676f02d9, 0x8d2a4c8a, 0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, 0x289b7ec6, 0xeaa127fa,
    0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92,
    0xffeff47d, 0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
};

// Runtime guard: kConstants must match floor(2^32*|sin(i)|). Kept cheap
// (only exercised when assertions are enabled in tests via md5SelfCheck()).
inline uint32_t sinConstant(uint32_t i) {
    double s = std::fabs(std::sin(static_cast<double>(i) + 1.0));
    return static_cast<uint32_t>(4294967296.0 * s);
}

inline uint32_t rotl(uint32_t x, uint32_t n) {
    return (x << n) | (x >> (32u - n));
}

struct Md5State {
    uint32_t a, b, c, d;
    uint64_t total = 0;  // bytes absorbed so far (message only)
    uint8_t buffer[64] = {};
    size_t buffered = 0;

    Md5State() : a(0x67452301u), b(0xefcdab89u), c(0x98badcfeu), d(0x10325476u) {}

    void processBlock(const uint8_t* p) {
        // Little-endian message schedule.
        uint32_t m[16];
        for (uint32_t i = 0; i < 16; ++i) {
            m[i] = static_cast<uint32_t>(p[i * 4]) |
                   (static_cast<uint32_t>(p[i * 4 + 1]) << 8) |
                   (static_cast<uint32_t>(p[i * 4 + 2]) << 16) |
                   (static_cast<uint32_t>(p[i * 4 + 3]) << 24);
        }
        uint32_t aa = a, bb = b, cc = c, dd = d;
        for (uint32_t i = 0; i < 64; ++i) {
            uint32_t f = 0;
            uint32_t g = 0;
            if (i < 16) {
                f = (bb & cc) | (~bb & dd);
                g = i;
            } else if (i < 32) {
                f = (dd & bb) | (~dd & cc);
                g = (5 * i + 1) % 16;
            } else if (i < 48) {
                f = bb ^ cc ^ dd;
                g = (3 * i + 5) % 16;
            } else {
                f = cc ^ (bb | ~dd);
                g = (7 * i) % 16;
            }
            uint32_t tmp = dd;
            dd = cc;
            cc = bb;
            bb = bb + rotl(aa + f + kConstants[i] + m[g], kShifts[i]);
            aa = tmp;
        }
        a += aa;
        b += bb;
        c += cc;
        d += dd;
    }

    void update(const uint8_t* data, size_t len) {
        total += len;
        while (len > 0) {
            size_t take = 64 - buffered;
            if (take > len) take = len;
            std::memcpy(buffer + buffered, data, take);
            buffered += take;
            data += take;
            len -= take;
            if (buffered == 64) {
                processBlock(buffer);
                buffered = 0;
            }
        }
    }

    void finish(uint8_t out[16]) {
        uint64_t bits = total * 8;
        buffer[buffered++] = 0x80;
        if (buffered > 56) {
            while (buffered < 64) buffer[buffered++] = 0;
            processBlock(buffer);
            buffered = 0;
        }
        while (buffered < 56) buffer[buffered++] = 0;  // MUT:<=
        for (int i = 0; i < 8; ++i) {
            buffer[buffered++] = static_cast<uint8_t>((bits >> (8 * i)) & 0xFFu);
        }
        processBlock(buffer);
        buffered = 0;
        const uint32_t words[4] = {a, b, c, d};
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                out[i * 4 + j] = static_cast<uint8_t>((words[i] >> (8 * j)) & 0xFFu);
            }
        }
    }
};

const char kHexDigits[] = "0123456789abcdef";

}  // namespace

void md5Digest(const uint8_t* data, size_t len, uint8_t out[16]) {
    if (out == nullptr) return;
    if (data == nullptr) len = 0;
    Md5State st;
    st.update(data, len);
    st.finish(out);
}

std::string md5Hex(const uint8_t* data, size_t len) {
    if (data == nullptr) len = 0;
    uint8_t digest[16];
    md5Digest(data, len, digest);
    std::string hex;
    hex.reserve(32);
    for (int i = 0; i < 16; ++i) {
        hex.push_back(kHexDigits[digest[i] >> 4]);
        hex.push_back(kHexDigits[digest[i] & 0x0Fu]);
    }
    return hex;
}

// Exposed for tests: verifies the round constants against their analytic
// definition (floor(2^32 * |sin(i+1)|)) and checks the RFC 1321 test vectors.
bool md5SelfCheck() {
    for (uint32_t i = 0; i < 64; ++i) {
        if (kConstants[i] != sinConstant(i)) return false;
    }
    struct Vec {
        const char* input;
        const char* hex;
    };
    static const Vec kVectors[] = {
        {"", "d41d8cd98f00b204e9800998ecf8427e"},
        {"a", "0cc175b9c0f1b6a831c399e269772661"},
        {"abc", "900150983cd24fb0d6963f7d28e17f72"},
        {"message digest", "f96b697d7cb7938d525a2f31aaf161d0"},
        {"abcdefghijklmnopqrstuvwxyz", "c3fcd3d76192e4007dfb496cca67e13b"},
    };
    for (const Vec& v : kVectors) {
        std::string in(v.input);
        if (md5Hex(reinterpret_cast<const uint8_t*>(in.data()), in.size()) != v.hex) {
            return false;
        }
    }
    return true;
}

}  // namespace traffic
