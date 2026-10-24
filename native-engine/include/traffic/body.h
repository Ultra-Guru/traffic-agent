#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace traffic {

enum class ChunkedStatus { NeedMore, Complete, Malformed };

// Decodes an entire chunked transfer body (RFC 7266 section 4.1 / RFC 9112
// 7.1). Handles chunk extensions, trailers and the terminating 0-chunk.
// `consumed` gets the number of input bytes used (including trailers).
// NeedMore means the buffer ends mid-chunk and more wire bytes are expected.
ChunkedStatus decodeChunked(const uint8_t* data, size_t len, std::vector<uint8_t>* out,
                            size_t* consumed,
                            std::vector<std::pair<std::string, std::string>>* trailers);

// Decompresses a response body by Content-Encoding. Supported: gzip/x-gzip,
// deflate (zlib-wrapped with raw-deflate fallback) and identity/"".
// Output is capped at 16 MiB as a decompression-bomb guard; exceeding the cap
// returns false.
bool decompressBody(const uint8_t* data, size_t len, const std::string& contentEncoding,
                    std::vector<uint8_t>* out);

// Sniffs a MIME type from magic bytes; text-ish declared types win over the
// generic text/plain heuristic. Returns "application/octet-stream" when the
// body gives nothing away.
std::string sniffMime(const uint8_t* data, size_t len, const std::string& declaredContentType);

}  // namespace traffic
