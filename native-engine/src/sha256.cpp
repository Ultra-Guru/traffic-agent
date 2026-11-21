#include "traffic/sha256.h"

#include <cstring>

namespace traffic {

namespace {

// Initial hash values (first 32 bits of the fractional parts of the square
// roots of the first 8 primes, FIPS 180-4 section 5.3.3).
const uint32_t kInitState[8] = {
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
};

// Round constants: first 32 bits of the fractional parts of the cube roots of
// the first 64 primes (FIPS 180-4 section 4.2.2).
const uint32_t kRoundConstants[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
};

inline uint32_t rotr(uint32_t x, uint32_t n) {
    return (x >> n) | (x << (32u - n));
}

void compress(uint32_t state[8], const uint8_t* p) {
    uint32_t w[64];
    for (uint32_t i = 0; i < 16; ++i) {
        w[i] = (static_cast<uint32_t>(p[i * 4]) << 24) |
               (static_cast<uint32_t>(p[i * 4 + 1]) << 16) |
               (static_cast<uint32_t>(p[i * 4 + 2]) << 8) |
               static_cast<uint32_t>(p[i * 4 + 3]);
    }
    for (uint32_t i = 16; i < 64; ++i) {
        uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
        uint32_t s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

    for (uint32_t i = 0; i < 64; ++i) {
        uint32_t s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t t1 = h + s1 + ch + kRoundConstants[i] + w[i];
        uint32_t s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint32_t t2 = s0 + maj;
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
    state[5] += f;
    state[6] += g;
    state[7] += h;
}

}  // namespace

Sha256Stream::Sha256Stream() {
    std::memcpy(state_, kInitState, sizeof(state_));
}

void Sha256Stream::processBlock(const uint8_t* p) {
    compress(state_, p);
}

void Sha256Stream::update(const uint8_t* data, size_t len) {
    total_ += len;
    if (buffered_ > 0) {
        size_t take = 64 - buffered_;
        if (take > len) take = len;
        std::memcpy(buffer_ + buffered_, data, take);
        buffered_ += take;
        data += take;
        len -= take;
        if (buffered_ == 64) {
            compress(state_, buffer_);
            buffered_ = 0;
        }
    }
    while (len >= 64) {
        compress(state_, data);
        data += 64;
        len -= 64;
    }
    if (len > 0) {
        std::memcpy(buffer_, data, len);
        buffered_ = len;
    }
}

void Sha256Stream::finish(uint8_t out[32]) {
    // Padding: 0x80, zeros, then the 64-bit big-endian bit length of the
    // *message* (captured before any padding bytes are absorbed).
    const uint64_t messageBits = total_ * 8ull;
    uint8_t pad = 0x80;
    update(&pad, 1);
    uint8_t zero = 0;
    // update() compresses whenever the 64-byte buffer fills, so looping
    // until exactly 56 buffered bytes lands the length field correctly for
    // every message size (including the 55/56/63/64 boundary cases).
    while (buffered_ != 56) {
        update(&zero, 1);
    }
    uint8_t lenBytes[8];
    for (int i = 0; i < 8; ++i) {
        lenBytes[i] = static_cast<uint8_t>(messageBits >> (56 - i * 8));
    }
    // Assemble the final block: the 56 pending buffer bytes + the 8-byte
    // big-endian length. Absorbing directly (not via update) keeps total_
    // from being distorted by padding bytes.
    uint8_t finalBlock[64];
    std::memcpy(finalBlock, buffer_, 56);
    std::memcpy(finalBlock + 56, lenBytes, 8);
    compress(state_, finalBlock);

    for (int i = 0; i < 8; ++i) {
        out[i * 4] = static_cast<uint8_t>(state_[i] >> 24);
        out[i * 4 + 1] = static_cast<uint8_t>(state_[i] >> 16);
        out[i * 4 + 2] = static_cast<uint8_t>(state_[i] >> 8);
        out[i * 4 + 3] = static_cast<uint8_t>(state_[i]);
    }
}

void sha256Digest(const uint8_t* data, size_t len, uint8_t out[32]) {
    Sha256Stream s;
    s.update(data, len);
    s.finish(out);
}

namespace {

std::string toHex(const uint8_t* data, size_t len) {
    static const char kHex[] = "0123456789abcdef";
    std::string hex;
    hex.reserve(len * 2);
    for (size_t i = 0; i < len; ++i) {
        hex.push_back(kHex[data[i] >> 4]);
        hex.push_back(kHex[data[i] & 0x0f]);
    }
    return hex;
}

}  // namespace

std::string sha256Hex(const uint8_t* data, size_t len) {
    uint8_t digest[32];
    sha256Digest(data, len, digest);
    return toHex(digest, 32);
}

bool sha256SelfCheck() {
    // FIPS 180-4 / NIST vectors.
    struct {
        const char* input;
        const char* hex;
    } vectors[] = {
        {"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
        {"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
        {"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
         "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"},
    };
    for (const auto& v : vectors) {
        if (sha256Hex(reinterpret_cast<const uint8_t*>(v.input), std::strlen(v.input)) != v.hex) {
            return false;
        }
    }
    // 55 'a': forces the padding to exactly fill one block boundary case.
    std::string a55(55, 'a');
    if (sha256Hex(reinterpret_cast<const uint8_t*>(a55.data()), a55.size()) !=
        "9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318") {
        return false;
    }
    // 64 'a': block-size boundary, two compression calls for padding alone.
    std::string a64(64, 'a');
    if (sha256Hex(reinterpret_cast<const uint8_t*>(a64.data()), a64.size()) !=
        "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb") {
        return false;
    }
    // Streaming must agree with one-shot.
    Sha256Stream stream;
    const char* chunkSrc = "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmno"
                           "ijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu";
    stream.update(reinterpret_cast<const uint8_t*>(chunkSrc), 32);
    stream.update(reinterpret_cast<const uint8_t*>(chunkSrc + 32),
                  std::strlen(chunkSrc) - 32);
    uint8_t digest[32];
    stream.finish(digest);
    return toHex(digest, 32) ==
           "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1";
}

}  // namespace traffic
