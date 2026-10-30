#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace traffic {

// FIPS 180-4 SHA-256, self-contained (no OpenSSL dependency). Used for JA4
// fingerprints (12-hex truncated digests) and content hashing in the store.

// Writes the 32-byte digest of data[0..len) into out[32].
void sha256Digest(const uint8_t* data, size_t len, uint8_t out[32]);

// Lowercase hex SHA-256 of data[0..len).
std::string sha256Hex(const uint8_t* data, size_t len);

// Streaming variant for hashing large buffers in chunks (cap the body hash
// without holding the whole body in memory).
class Sha256Stream {
public:
    Sha256Stream();
    void update(const uint8_t* data, size_t len);
    // Finalizes and writes the digest; the stream must not be reused after.
    void finish(uint8_t out[32]);

private:
    void processBlock(const uint8_t* p);
    uint32_t state_[8];
    uint64_t total_ = 0;       // bytes absorbed so far
    uint8_t buffer_[64] = {};  // partial block buffer
    size_t buffered_ = 0;
};

// Verifies the FIPS 180-4 test vectors (empty, "abc", 55-'a' and 64-'a'
// boundary cases). Used by the unit tests.
bool sha256SelfCheck();

}  // namespace traffic
