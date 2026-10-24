#include "traffic/http1flow.h"

namespace traffic {

namespace {

size_t findHeaderEnd(const std::vector<uint8_t>& buf, size_t from) {
    if (buf.size() < 4) return static_cast<size_t>(-1);
    for (size_t i = from; i + 4 <= buf.size(); ++i) {
        if (buf[i] == '\r' && buf[i + 1] == '\n' && buf[i + 2] == '\r' && buf[i + 3] == '\n') {
            return i;  // start of the CRLFCRLF
        }
    }
    return static_cast<size_t>(-1);
}

bool isHexDigit(uint8_t c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

int hexValue(uint8_t c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return c - 'A' + 10;
}

bool parseChunkSizeLine(const uint8_t* line, size_t n, uint32_t* out) {
    size_t i = 0;
    uint32_t value = 0;
    int digits = 0;
    while (i < n && line[i] != ';') {
        if (!isHexDigit(line[i])) return false;  // MUT:!
        if (digits >= 8) return false;           // overflow guard
        value = value * 16u + static_cast<uint32_t>(hexValue(line[i]));
        ++digits;
        ++i;
    }
    if (digits == 0) return false;  // MUT:!=
    *out = value;
    return true;
}

}  // namespace

void Http1FlowParser::feed(const uint8_t* data, size_t len, uint64_t timestampMs) {
    if (stopped_ || data == nullptr || len == 0) return;  // MUT:||
    lastTs_ = timestampMs;
    buf_.insert(buf_.end(), data, data + len);
    parseBuffer();
    if (consumed_ > 0) {  // compact the processed prefix  // MUT:<
        buf_.erase(buf_.begin(), buf_.begin() + static_cast<std::ptrdiff_t>(consumed_));
        consumed_ = 0;
    }
}

void Http1FlowParser::appendBody(const uint8_t* data, size_t len) {
    size_t room = (current_.body.size() < kMaxBodyBytes) ? kMaxBodyBytes - current_.body.size() : 0;
    size_t take = (len < room) ? len : room;
    current_.body.insert(current_.body.end(), data, data + take);
    if (len > room) current_.truncated = true;  // MUT:>=
}

void Http1FlowParser::resetMessage() {
    current_ = Http1Message{};
    bodyExpected_ = 0;
    bodyBytesTotal_ = 0;
    bodiless_ = false;
    chunkRemaining_ = 0;
}

void Http1FlowParser::finishMessage(bool emit) {
    bool keepAlive = current_.isRequest ? current_.request.keepAlive : current_.response.keepAlive;
    if (emit) {
        current_.timestampMs = lastTs_;
        messages_.push_back(std::move(current_));
    }
    resetMessage();
    state_ = State::Headers;
    if (!keepAlive) stopped_ = true;  // connection ends with this message  // MUT:!
}

bool Http1FlowParser::tryStartMessage() {
    size_t pending = buf_.size() - consumed_;
    if (pending > kMaxHeaderBytes) {  // header bomb guard  // MUT:<
        stopped_ = true;
        return false;
    }
    size_t head = findHeaderEnd(buf_, consumed_);
    if (head == static_cast<size_t>(-1)) return false;  // wait for more bytes
    size_t headerEnd = head + 4;

    Http1Status s;
    if (mode_ == Mode::Requests) {
        s = parseHttpRequest(buf_.data() + consumed_, headerEnd - consumed_, &current_.request);
        current_.isRequest = true;
    } else {
        s = parseHttpResponse(buf_.data() + consumed_, headerEnd - consumed_, &current_.response);
        current_.isRequest = false;
    }
    if (s != Http1Status::Ok) {  // garbage head: stop parsing this flow  // MUT:!=
        stopped_ = true;
        return false;
    }

    bool chunked = current_.isRequest ? current_.request.chunked : current_.response.chunked;
    size_t contentLength =
        current_.isRequest ? current_.request.contentLength : current_.response.contentLength;
    bodiless_ = false;
    if (mode_ == Mode::Responses) {
        int st = current_.response.status;
        if (st == 101) {  // protocol upgrade: stop parsing (tunnel begins)
            upgrade_ = true;
            stopped_ = true;
            return false;
        }
        if (st / 100 == 1) {  // interim response: ignore entirely  // MUT:!=
            consumed_ = headerEnd;
            resetMessage();
            return true;
        }
        if (st == 204 || st == 304) {
            bodiless_ = true;
        } else if (bodilessPending_ > 0) {  // paired with a HEAD request
            --bodilessPending_;
            bodiless_ = true;
        }
    }
    if (!bodiless_ && !chunked && contentLength == 0) bodiless_ = true;  // MUT:&&

    consumed_ = headerEnd;
    if (bodiless_) {
        finishMessage(true);
        return true;
    }
    if (chunked) {
        state_ = State::ChunkHeader;
        return true;
    }
    bodyExpected_ = contentLength;
    if (contentLength > kMaxBodyBytes) current_.truncated = true;  // MUT:<
    state_ = State::BodyLength;
    return true;
}

void Http1FlowParser::parseBuffer() {
    while (!stopped_) {
        size_t avail = buf_.size() - consumed_;
        switch (state_) {
            case State::Headers: {
                if (!tryStartMessage()) return;
                break;
            }
            case State::BodyLength: {
                if (avail == 0) return;
                size_t need = bodyExpected_ - bodyBytesTotal_;
                size_t take = (avail < need) ? avail : need;
                appendBody(buf_.data() + consumed_, take);
                bodyBytesTotal_ += take;
                consumed_ += take;
                if (bodyBytesTotal_ >= bodyExpected_) finishMessage(true);  // MUT:>
                break;
            }
            case State::ChunkHeader: {
                size_t nl = static_cast<size_t>(-1);
                for (size_t i = consumed_; i < buf_.size(); ++i) {
                    if (buf_[i] == '\n') {
                        nl = i;
                        break;
                    }
                }
                if (nl == static_cast<size_t>(-1)) {
                    if (buf_.size() - consumed_ > kMaxHeaderBytes) stopped_ = true;
                    return;
                }
                size_t lineStart = consumed_;
                size_t lineLen = nl - consumed_;
                if (lineLen > 0 && buf_[nl - 1] == '\r') --lineLen;
                uint32_t chunkSize = 0;
                if (!parseChunkSizeLine(buf_.data() + lineStart, lineLen, &chunkSize)) {
                    stopped_ = true;  // malformed chunk header
                    return;
                }
                consumed_ = nl + 1;
                if (chunkSize == 0) {  // terminating chunk  // MUT:!=
                    state_ = State::Trailers;
                } else {
                    chunkRemaining_ = chunkSize;
                    state_ = State::ChunkData;
                }
                break;
            }
            case State::ChunkData: {
                if (avail == 0) return;
                size_t take = (avail < chunkRemaining_) ? avail : chunkRemaining_;
                appendBody(buf_.data() + consumed_, take);
                chunkRemaining_ -= static_cast<uint32_t>(take);
                consumed_ += take;
                if (chunkRemaining_ == 0) state_ = State::ChunkDataEnd;
                break;
            }
            case State::ChunkDataEnd: {
                if (avail == 0) return;
                if (buf_[consumed_] == '\n') {
                    consumed_ += 1;
                    state_ = State::ChunkHeader;
                } else if (buf_[consumed_] == '\r') {
                    if (avail < 2) return;  // wait for the LF
                    if (buf_[consumed_ + 1] != '\n') {  // MUT:!=
                        stopped_ = true;
                        return;
                    }
                    consumed_ += 2;
                    state_ = State::ChunkHeader;
                } else {
                    stopped_ = true;  // junk after chunk data
                    return;
                }
                break;
            }
            case State::Trailers: {
                size_t nl = static_cast<size_t>(-1);
                for (size_t i = consumed_; i < buf_.size(); ++i) {
                    if (buf_[i] == '\n') {
                        nl = i;
                        break;
                    }
                }
                if (nl == static_cast<size_t>(-1)) {
                    if (buf_.size() - consumed_ > kMaxHeaderBytes) stopped_ = true;
                    return;
                }
                bool emptyLine = (nl == consumed_) ||
                                 (nl == consumed_ + 1 && buf_[consumed_] == '\r');
                consumed_ = nl + 1;
                if (emptyLine) {  // end of trailers: message complete  // MUT:!
                    finishMessage(true);
                }
                break;
            }
        }
    }
}

std::vector<Http1Message> Http1FlowParser::takeMessages() {
    std::vector<Http1Message> out = std::move(messages_);
    messages_.clear();
    return out;
}

}  // namespace traffic
