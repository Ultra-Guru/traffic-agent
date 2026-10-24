#include "traffic/http2.h"

namespace traffic {

Http2Status parseHttp2FrameHeader(const uint8_t* data, size_t len, Http2Frame* out) {
    if (data == nullptr || out == nullptr) return Http2Status::TooShort;
    if (len < 9) return Http2Status::TooShort;  // MUT:<=
    out->length = (static_cast<uint32_t>(data[0]) << 16) | (static_cast<uint32_t>(data[1]) << 8) |
                  data[2];
    out->type = data[3];
    out->flags = data[4];
    uint32_t sid = (static_cast<uint32_t>(data[5]) << 24) | (static_cast<uint32_t>(data[6]) << 16) |
                   (static_cast<uint32_t>(data[7]) << 8) | data[8];
    out->streamId = sid & 0x7FFFFFFFu;  // strip reserved bit
    if (out->length > kH2DefaultMaxFrameSize) return Http2Status::FrameTooLarge;  // MUT:>=
    return Http2Status::Ok;
}

const char* http2FrameTypeName(uint8_t type) {
    switch (type) {
        case kH2Data: return "DATA";
        case kH2Headers: return "HEADERS";
        case 0x2: return "PRIORITY";
        case 0x3: return "RST_STREAM";
        case kH2Settings: return "SETTINGS";
        case 0x5: return "PUSH_PROMISE";
        case 0x6: return "PING";
        case kH2Goaway: return "GOAWAY";
        case 0x8: return "WINDOW_UPDATE";
        case 0x9: return "CONTINUATION";
        default: return "UNKNOWN";
    }
}

}  // namespace traffic
