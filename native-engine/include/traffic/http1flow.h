#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

#include "http1.h"

namespace traffic {

// One complete HTTP/1 message: head fields plus (decoded) body.
struct Http1Message {
    bool isRequest = false;
    Http1Request request;
    Http1Response response;
    std::vector<uint8_t> body;  // de-chunked body, capped at kMaxBodyBytes
    bool truncated = false;    // body exceeded the retention cap
    uint64_t timestampMs = 0;
};

// Incremental single-direction HTTP/1 parser. Bytes from reassembled TCP are
// fed in as they arrive; completed messages accumulate until drained with
// takeMessages(). Handles Content-Length and chunked bodies, keep-alive
// pipelining, 1xx skipping and the 101-upgrade stop.
class Http1FlowParser {
public:
    enum class Mode { Requests, Responses };

    static constexpr size_t kMaxBodyBytes = 1u << 20;    // 1 MiB body retention
    static constexpr size_t kMaxHeaderBytes = 64u << 10;  // 64 KiB head cap

    explicit Http1FlowParser(Mode mode) : mode_(mode) {}

    void feed(const uint8_t* data, size_t len, uint64_t timestampMs);
    void stop() { stopped_ = true; }
    bool stopped() const { return stopped_; }
    bool upgradeDetected() const { return upgrade_; }

    // Response mode hint: the next response carries no body (used when the
    // engine pairs a HEAD request). 204/304/1xx are handled internally.
    void setNextResponseBodiless() { ++bodilessPending_; }

    std::vector<Http1Message> takeMessages();

private:
    enum class State {
        Headers,          // accumulating the head, waiting for CRLFCRLF
        BodyLength,       // draining a Content-Length body
        ChunkHeader,      // reading "<hex>[;ext] CRLF"
        ChunkData,        // draining chunk payload
        ChunkDataEnd,     // expecting the CRLF after chunk payload
        Trailers          // reading trailer lines until an empty line
    };

    void parseBuffer();
    bool tryStartMessage();       // parses the head of a new message
    void finishMessage(bool emit);
    void appendBody(const uint8_t* data, size_t len);
    void resetMessage();

    Mode mode_;
    State state_ = State::Headers;
    std::vector<uint8_t> buf_;
    size_t consumed_ = 0;
    Http1Message current_;
    size_t bodyBytesTotal_ = 0;  // wire bytes seen for this body (for truncation)
    size_t bodyExpected_ = 0;    // Content-Length target
    bool bodiless_ = false;
    size_t bodilessPending_ = 0;
    uint32_t chunkRemaining_ = 0;
    std::vector<Http1Message> messages_;
    bool stopped_ = false;
    bool upgrade_ = false;
    uint64_t lastTs_ = 0;
};

}  // namespace traffic
