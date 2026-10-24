#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace traffic {

struct WsFrameInfo {
    bool fin = false;
    uint8_t opcode = 0;
    bool masked = false;
    uint64_t payloadLength = 0;
    size_t headerLength = 0;  // bytes consumed by the frame header itself
};

enum class WsStatus { Ok, TooShort, UnsupportedLength, BadMask };

// Parses the WebSocket frame header (RFC 6455 section 5.2).
WsStatus parseWsFrame(const uint8_t* data, size_t len, WsFrameInfo* out);

// Parses a complete frame (header + payload) and unmask it. On success
// `out` holds the header fields, `unmaskedPayload` the (unmasked) payload
// and the return value is Ok. TooShort when the frame is incomplete.
WsStatus decodeWsFrame(const uint8_t* data, size_t len, WsFrameInfo* out,
                       std::vector<uint8_t>* unmaskedPayload);

// One fully assembled message (fragments already joined).
struct WsMessage {
    uint8_t opcode = 0;
    std::vector<uint8_t> payload;
    bool fin = true;
};

// Incremental frame-by-frame assembler: feed() TCP payload bytes as they are
// reassembled; complete messages (including interleaved control frames) can
// be drained with takeMessages().
class WsMessageAssembler {
public:
    void feed(const uint8_t* data, size_t len);
    std::vector<WsMessage> takeMessages();

private:
    void tryParse();

    std::vector<uint8_t> buf_;
    std::vector<WsMessage> messages_;
    std::vector<uint8_t> pendingPayload_;  // fragmented data message
    uint8_t pendingOpcode_ = 0;
    bool fragmenting_ = false;
};

// Opcodes.
constexpr uint8_t kWsContinuation = 0x0;
constexpr uint8_t kWsText = 0x1;
constexpr uint8_t kWsBinary = 0x2;
constexpr uint8_t kWsClose = 0x8;
constexpr uint8_t kWsPing = 0x9;
constexpr uint8_t kWsPong = 0xA;

const char* wsOpcodeName(uint8_t opcode);

}  // namespace traffic
