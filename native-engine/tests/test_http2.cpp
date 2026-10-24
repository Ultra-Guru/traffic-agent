#include "traffic/http2.h"

#include "builders.hpp"
#include "test_framework.hpp"

using namespace traffic;
using namespace tb;

TA_TEST(h2_parses_settings_frame) {
    // length=4, type=SETTINGS, flags=0, stream=0
    Bytes b = {0x00, 0x00, 0x04, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00};
    Http2Frame f{};
    TA_CHECK_EQ(parseHttp2FrameHeader(b.data(), b.size(), &f), Http2Status::Ok);
    TA_CHECK_EQ(f.length, 4u);
    TA_CHECK_EQ(f.type, kH2Settings);
    TA_CHECK_EQ(f.streamId, 0u);
    TA_CHECK_ST(http2FrameTypeName(f.type), "SETTINGS");
}

TA_TEST(h2_strips_reserved_bit_from_stream_id) {
    Bytes b = {0x00, 0x00, 0x00, 0x04, 0x00, 0x80, 0x00, 0x00, 0x01};
    Http2Frame f{};
    TA_CHECK_EQ(parseHttp2FrameHeader(b.data(), b.size(), &f), Http2Status::Ok);
    TA_CHECK_EQ(f.streamId, 1u);
}

TA_TEST(h2_rejects_short_buffer) {
    Bytes b(8, 0);
    Http2Frame f{};
    TA_CHECK_EQ(parseHttp2FrameHeader(b.data(), b.size(), &f), Http2Status::TooShort);
}

TA_TEST(h2_rejects_oversized_frame) {
    Bytes b = {0x00, 0x40, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};  // length 16385
    Http2Frame f{};
    TA_CHECK_EQ(parseHttp2FrameHeader(b.data(), b.size(), &f), Http2Status::FrameTooLarge);
}

TA_TEST(h2_accepts_frame_at_exact_default_max) {
    Bytes b = {0x00, 0x40, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00};  // length 16384
    Http2Frame f{};
    TA_CHECK_EQ(parseHttp2FrameHeader(b.data(), b.size(), &f), Http2Status::Ok);
    TA_CHECK_EQ(f.length, 16384u);
}

TA_TEST(h2_frame_type_names) {
    TA_CHECK_ST(http2FrameTypeName(kH2Data), "DATA");
    TA_CHECK_ST(http2FrameTypeName(kH2Headers), "HEADERS");
    TA_CHECK_ST(http2FrameTypeName(kH2Goaway), "GOAWAY");
    TA_CHECK_ST(http2FrameTypeName(0xFE), "UNKNOWN");
}
