#pragma once

#include <cstddef>
#include <cstdint>

namespace traffic {

// HTTP/2 frame header is fixed 9 bytes.
struct Http2Frame {
    uint32_t length = 0;
    uint8_t type = 0;
    uint8_t flags = 0;
    uint32_t streamId = 0;  // R bit already stripped
};

enum class Http2Status { Ok, TooShort, FrameTooLarge };

Http2Status parseHttp2FrameHeader(const uint8_t* data, size_t len, Http2Frame* out);

// Frame types (RFC 7540 section 6).
constexpr uint8_t kH2Data = 0x0;
constexpr uint8_t kH2Headers = 0x1;
constexpr uint8_t kH2Settings = 0x4;
constexpr uint8_t kH2Goaway = 0x7;

// Frame flag bits.
constexpr uint8_t kH2FlagEndStream = 0x01;
constexpr uint8_t kH2FlagEndHeaders = 0x04;
constexpr uint8_t kH2FlagPadded = 0x08;
constexpr uint8_t kH2FlagPriority = 0x20;

constexpr size_t kH2DefaultMaxFrameSize = 16384;

const char* http2FrameTypeName(uint8_t type);

}  // namespace traffic
