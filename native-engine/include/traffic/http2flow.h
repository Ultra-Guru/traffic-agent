#pragma once

#include <cstddef>
#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "hpack.h"

namespace traffic {

// ---------------------------------------------------------------------------
// HTTP/2 stream-level capture (RFC 7540) + gRPC framing (RFC 8441 style
// length-prefixed messages over HTTP/2 DATA frames).
//
// H2StreamTracker consumes complete frames (9-byte header already parsed by
// the engine) per direction and reassembles them into per-stream
// request/response records that mirror HttpExchangeRecord semantics:
//   - HEADERS (+CONTINUATION) blocks are HPACK-decoded with a per-direction
//     stateful context, so blocks referencing earlier dynamic-table entries
//     decode correctly (real browsers/servers do this constantly).
//   - DATA payloads are accumulated per direction (padding stripped).
//   - A second server-side HEADERS block on the same stream is treated as
//     trailers (gRPC trailer-only responses included).
//   - RST_STREAM flushes the stream; GOAWAY flushes everything still open.
// ---------------------------------------------------------------------------

// One direction of a stream: decoded header list + accumulated DATA.
struct H2StreamMessage {
    std::vector<HpackHeader> headers;  // in wire order, pseudo-headers first
    std::vector<uint8_t> data;         // DATA payload, padding stripped
    bool headersComplete = false;
    bool endStream = false;
    bool truncated = false;            // data hit the size cap
};

// One gRPC message split out of a DATA payload: 1 byte compressed flag +
// 4 bytes big-endian length + `length` bytes of (proto)payload.
struct GrpcMessage {
    bool compressed = false;
    uint32_t length = 0;              // declared length from the prefix
    std::vector<uint8_t> preview;     // capped payload preview
    bool truncated = false;
};

// A completed HTTP/2 stream, ready to be rendered as an exchange.
struct H2StreamRecord {
    uint32_t streamId = 0;
    H2StreamMessage request;          // client direction
    H2StreamMessage response;         // server direction
    std::vector<HpackHeader> trailers;
    bool isGrpc = false;
    std::vector<GrpcMessage> grpcMessages;  // response-direction messages
    std::string grpcStatus;                // "grpc-status" trailer value
    bool responseDone = false;
};

class H2StreamTracker {
public:
    static constexpr size_t kMaxDataBytes = 1u << 20;     // 1 MiB per direction
    static constexpr size_t kMaxStreams = 256;
    static constexpr size_t kMaxGrpcMessages = 64;
    static constexpr size_t kMaxGrpcPreview = 512;

    // A header block completed by END_HEADERS; drained for event emission.
    struct HeaderBlock {
        uint32_t streamId = 0;
        bool fromClient = false;
        std::vector<HpackHeader> headers;
    };

    // Feed one complete frame (payload excludes the 9-byte frame header).
    void onFrame(bool fromClient, uint8_t type, uint8_t flags, uint32_t streamId,
                 const uint8_t* payload, size_t len);

    // Streams that saw their response END_STREAM (or were flushed by
    // RST_STREAM / GOAWAY), oldest first.
    std::vector<H2StreamRecord> takeCompleted();

    // Header blocks decoded since the last drain, in arrival order.
    std::vector<HeaderBlock> takeDecodedHeaders();

    size_t openStreams() const { return streams_.size(); }

private:
    struct DirState {
        HpackDecoder hpack;   // stateful, per-direction dynamic table
        bool inHeaders = false;
        uint32_t streamId = 0;
        std::vector<uint8_t> block;  // HEADERS fragment under construction
    };

    struct Stream {
        H2StreamRecord rec;
    };

    DirState& dir(bool fromClient) { return fromClient ? client_ : server_; }

    Stream& streamFor(uint32_t streamId);
    void completeHeaderBlock(bool fromClient, bool endStream);
    void appendData(Stream& st, bool fromClient, const uint8_t* data, size_t len);
    void finishStream(Stream& st, bool fromClient);
    void flushStream(uint32_t streamId);
    void finalizeGrpc(H2StreamRecord& rec);
    static const std::string* headerValue(const std::vector<HpackHeader>& headers,
                                          const char* name);

    std::map<uint32_t, Stream> streams_;
    DirState client_;
    DirState server_;
    std::vector<H2StreamRecord> completed_;
    std::vector<HeaderBlock> decodedHeaders_;
};

// Splits an accumulated DATA payload into gRPC messages. Stops at the first
// structurally incomplete message (marks it truncated) or at the message cap.
void splitGrpcMessages(const std::vector<uint8_t>& data, std::vector<GrpcMessage>* out);

// Builds one gRPC DATA payload: 5-byte prefix + body (test/helper utility).
std::vector<uint8_t> buildGrpcMessage(const std::vector<uint8_t>& body, bool compressed = false);

}  // namespace traffic
