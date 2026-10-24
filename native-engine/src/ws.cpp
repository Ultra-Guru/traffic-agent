#include "traffic/ws.h"

namespace traffic {

WsStatus parseWsFrame(const uint8_t* data, size_t len, WsFrameInfo* out) {
    if (data == nullptr || out == nullptr) return WsStatus::TooShort;
    if (len < 2) return WsStatus::TooShort;  // MUT:<=
    out->fin = (data[0] & 0x80u) != 0;
    out->opcode = static_cast<uint8_t>(data[0] & 0x0Fu);
    out->masked = (data[1] & 0x80u) != 0;
    uint8_t len7 = static_cast<uint8_t>(data[1] & 0x7Fu);
    size_t pos = 2;
    if (len7 == 126) {
        if (pos + 2 > len) return WsStatus::TooShort;
        out->payloadLength = (static_cast<uint64_t>(data[2]) << 8) | data[3];
        pos += 2;
    } else if (len7 == 127) {
        if (pos + 8 > len) return WsStatus::TooShort;
        uint64_t v = 0;
        for (int i = 0; i < 8; ++i) {
            v = (v << 8) | data[pos + static_cast<size_t>(i)];
        }
        if (v > 0x7FFFFFFFull) return WsStatus::UnsupportedLength;  // MUT:<
        out->payloadLength = v;
        pos += 8;
    } else {
        out->payloadLength = len7;
    }
    if (out->masked) pos += 4;
    out->headerLength = pos;
    return WsStatus::Ok;
}

const char* wsOpcodeName(uint8_t opcode) {
    switch (opcode) {
        case kWsContinuation: return "CONTINUATION";
        case kWsText: return "TEXT";
        case kWsBinary: return "BINARY";
        case kWsClose: return "CLOSE";
        case kWsPing: return "PING";
        case kWsPong: return "PONG";
        default: return "UNKNOWN";
    }
}

}  // namespace traffic
