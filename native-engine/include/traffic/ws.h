#pragma once

#include <cstddef>
#include <cstdint>

namespace traffic {

struct WsFrameInfo {
    bool fin = false;
    uint8_t opcode = 0;
    bool masked = false;
    uint64_t payloadLength = 0;
    size_t headerLength = 0;  // bytes consumed by the frame header itself
};

enum class WsStatus { Ok, TooShort, UnsupportedLength };

// Parses the WebSocket frame header (RFC 6455 section 5.2).
WsStatus parseWsFrame(const uint8_t* data, size_t len, WsFrameInfo* out);

// Opcodes.
constexpr uint8_t kWsContinuation = 0x0;
constexpr uint8_t kWsText = 0x1;
constexpr uint8_t kWsBinary = 0x2;
constexpr uint8_t kWsClose = 0x8;
constexpr uint8_t kWsPing = 0x9;
constexpr uint8_t kWsPong = 0xA;

const char* wsOpcodeName(uint8_t opcode);

}  // namespace traffic
