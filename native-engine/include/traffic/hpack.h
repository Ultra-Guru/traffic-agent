#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace traffic {

struct HpackHeader {
    std::string name;
    std::string value;
};

enum class HpackStatus {
    Ok,
    TooShort,
    MalformedInteger,   // integer prefix ran off the buffer
    MalformedString,    // bad length or bad Huffman padding
    BadIndex            // table index out of range
};

// Decodes a complete HPACK block (RFC 7541). Emits name/value pairs in order,
// resolves indexed fields, inserts literal-with-incremental-indexing entries
// into the dynamic table and honours dynamic table size updates. `consumed`
// receives the number of input bytes used.
HpackStatus decodeHpack(const uint8_t* data, size_t len, std::vector<HpackHeader>* out,
                        size_t* consumed);

// Stateful decoding context: one instance per connection direction. Real
// encoders reference dynamic-table entries inserted by *earlier* blocks on
// the same direction, so blocks cannot be decoded in isolation. The dynamic
// table persists across decode() calls.
class HpackDecoder {
public:
    HpackDecoder();
    ~HpackDecoder();
    HpackDecoder(HpackDecoder&&) noexcept;
    HpackDecoder(const HpackDecoder&) = delete;
    HpackDecoder& operator=(const HpackDecoder&) = delete;

    HpackStatus decode(const uint8_t* data, size_t len, std::vector<HpackHeader>* out);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

// Encodes headers as literal-without-indexing, plain (non-Huffman) strings:
// simple and always decodable, used for replay/mock construction.
std::vector<uint8_t> encodeHpack(const std::vector<HpackHeader>& headers);

// RFC 7541 Appendix B Huffman encoding (canonical code from nghttp2's table).
std::vector<uint8_t> huffmanEncode(const std::string& s);

// Exposed for tests.
size_t hpackStaticTableSize();
const char* hpackStaticName(size_t index);    // 1..61, nullptr otherwise
const char* hpackStaticValue(size_t index);   // 1..61, nullptr otherwise

}  // namespace traffic
