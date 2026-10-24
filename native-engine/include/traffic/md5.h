#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace traffic {

// RFC 1321 MD5, self-contained (no OpenSSL dependency). Needed for JA3
// fingerprints; also handy for content hashing in the capture store.

// Writes the 16-byte digest of data[0..len) into out[16].
void md5Digest(const uint8_t* data, size_t len, uint8_t out[16]);

// Lowercase hex MD5 of data[0..len), e.g. "d41d8cd98f00b204e9800998ecf8427e".
std::string md5Hex(const uint8_t* data, size_t len);

// Verifies the round constants against floor(2^32*|sin(i)|) and the RFC 1321
// test vectors. Used by the unit tests.
bool md5SelfCheck();

}  // namespace traffic
