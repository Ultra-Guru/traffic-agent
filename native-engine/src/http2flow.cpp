#include "traffic/http2flow.h"

#include <cstring>

#include "traffic/http2.h"

namespace traffic {

namespace {

// GrpcMessage prefix: 1 byte compressed flag + 4 bytes big-endian length.
constexpr size_t kGrpcPrefixBytes = 5;

uint32_t readBe32(const uint8_t* p) {
    return (static_cast<uint32_t>(p[0]) << 24) | (static_cast<uint32_t>(p[1]) << 16) |
           (static_cast<uint32_t>(p[2]) << 8) | static_cast<uint32_t>(p[3]);
}

}  // namespace

H2StreamTracker::Stream& H2StreamTracker::streamFor(uint32_t streamId) {
    auto it = streams_.find(streamId);
    if (it != streams_.end()) return it->second;
    if (streams_.size() >= kMaxStreams && streams_.empty() == false) {
        // Evict the oldest (lowest) stream id to bound memory on hostile peers.
        streams_.erase(streams_.begin());
    }
    Stream& st = streams_[streamId];
    st.rec.streamId = streamId;
    return st;
}

void H2StreamTracker::onFrame(bool fromClient, uint8_t type, uint8_t flags, uint32_t streamId,
                              const uint8_t* payload, size_t len) {
    switch (type) {
        case kH2Data: {
            if (streamId == 0) break;
            const uint8_t* data = payload;
            size_t dataLen = len;
            if ((flags & kH2FlagPadded) != 0) {
                if (len == 0) break;
                size_t pad = payload[0];
                if (pad + 1 > len) break;  // corrupt padding
                data = payload + 1;
                dataLen = len - pad - 1;
            }
            Stream& st = streamFor(streamId);
            appendData(st, fromClient, data, dataLen);
            if ((flags & kH2FlagEndStream) != 0) finishStream(st, fromClient);
            break;
        }
        case kH2Headers: {
            if (streamId == 0) break;
            size_t off = 0;
            size_t end = len;
            if ((flags & kH2FlagPadded) != 0) {
                if (len == 0) break;
                end = len - (static_cast<size_t>(payload[0]) + 1);
                off = 1;
            }
            if ((flags & kH2FlagPriority) != 0) off += 5;
            if (off > end || end > len) break;  // corrupt flags
            DirState& d = dir(fromClient);
            d.inHeaders = true;
            d.streamId = streamId;
            d.block.assign(payload + off, payload + end);
            if ((flags & kH2FlagEndHeaders) != 0) {
                completeHeaderBlock(fromClient, (flags & kH2FlagEndStream) != 0);
            }
            break;
        }
        case 0x9: {  // CONTINUATION
            DirState& d = dir(fromClient);
            if (!d.inHeaders) break;
            d.block.insert(d.block.end(), payload, payload + len);
            if ((flags & kH2FlagEndHeaders) != 0) completeHeaderBlock(fromClient, false);
            break;
        }
        case 0x3: {  // RST_STREAM: the stream is dead, flush what we have
            flushStream(streamId);
            break;
        }
        case kH2Goaway: {  // no new streams on this connection; flush all
            for (auto& kv : streams_) {
                kv.second.rec.responseDone = true;
                completed_.push_back(std::move(kv.second.rec));
            }
            streams_.clear();
            break;
        }
        default:
            break;  // SETTINGS / PING / WINDOW_UPDATE / PUSH_PROMISE: ignored
    }
}

void H2StreamTracker::completeHeaderBlock(bool fromClient, bool endStream) {
    DirState& d = dir(fromClient);
    d.inHeaders = false;
    uint32_t streamId = d.streamId;
    std::vector<uint8_t> block = std::move(d.block);
    d.block.clear();

    std::vector<HpackHeader> headers;
    if (d.hpack.decode(block.data(), block.size(), &headers) != HpackStatus::Ok) {
        return;  // undecodable block: drop, keep the stream alive for DATA
    }

    HeaderBlock hb;
    hb.streamId = streamId;
    hb.fromClient = fromClient;
    hb.headers = headers;
    decodedHeaders_.push_back(std::move(hb));

    Stream& st = streamFor(streamId);
    H2StreamMessage& msg = fromClient ? st.rec.request : st.rec.response;
    if (!fromClient && msg.headersComplete) {
        // Second server HEADERS block on the same stream == trailers.
        st.rec.trailers.insert(st.rec.trailers.end(), headers.begin(), headers.end());
    } else {
        msg.headers = std::move(headers);
        msg.headersComplete = true;
    }

    // gRPC detection from either direction's content-type.
    const std::string* reqCt = headerValue(st.rec.request.headers, "content-type");
    const std::string* respCt = headerValue(st.rec.response.headers, "content-type");
    if ((reqCt != nullptr && reqCt->rfind("application/grpc", 0) == 0) ||
        (respCt != nullptr && respCt->rfind("application/grpc", 0) == 0)) {
        st.rec.isGrpc = true;
    }

    if (endStream) finishStream(st, fromClient);
}

void H2StreamTracker::appendData(Stream& st, bool fromClient, const uint8_t* data, size_t len) {
    H2StreamMessage& msg = fromClient ? st.rec.request : st.rec.response;
    if (msg.data.size() >= kMaxDataBytes) {
        if (len > 0) msg.truncated = true;
        return;
    }
    size_t room = kMaxDataBytes - msg.data.size();
    size_t take = len < room ? len : room;
    msg.data.insert(msg.data.end(), data, data + take);
    if (take < len) msg.truncated = true;
}

void H2StreamTracker::finishStream(Stream& st, bool fromClient) {
    H2StreamMessage& msg = fromClient ? st.rec.request : st.rec.response;
    msg.endStream = true;
    if (!fromClient) {
        st.rec.responseDone = true;
        finalizeGrpc(st.rec);
        completed_.push_back(std::move(st.rec));
        streams_.erase(st.rec.streamId);
    }
}

void H2StreamTracker::flushStream(uint32_t streamId) {
    auto it = streams_.find(streamId);
    if (it == streams_.end()) return;
    it->second.rec.responseDone = true;
    finalizeGrpc(it->second.rec);
    completed_.push_back(std::move(it->second.rec));
    streams_.erase(it);
}

void H2StreamTracker::finalizeGrpc(H2StreamRecord& rec) {
    if (!rec.isGrpc) return;
    splitGrpcMessages(rec.response.data, &rec.grpcMessages);
    const std::string* status = headerValue(rec.trailers, "grpc-status");
    if (status != nullptr) {
        rec.grpcStatus = *status;
    } else {
        const std::string* hdrStatus = headerValue(rec.response.headers, "grpc-status");
        if (hdrStatus != nullptr) rec.grpcStatus = *hdrStatus;
    }
}

const std::string* H2StreamTracker::headerValue(const std::vector<HpackHeader>& headers,
                                                const char* name) {
    for (const auto& h : headers) {
        if (h.name == name) return &h.value;
    }
    return nullptr;
}

std::vector<H2StreamRecord> H2StreamTracker::takeCompleted() {
    std::vector<H2StreamRecord> out = std::move(completed_);
    completed_.clear();
    return out;
}

std::vector<H2StreamTracker::HeaderBlock> H2StreamTracker::takeDecodedHeaders() {
    std::vector<HeaderBlock> out = std::move(decodedHeaders_);
    decodedHeaders_.clear();
    return out;
}

void splitGrpcMessages(const std::vector<uint8_t>& data, std::vector<GrpcMessage>* out) {
    if (out == nullptr) return;
    size_t pos = 0;
    while (pos + kGrpcPrefixBytes <= data.size()) {
        if (out->size() >= H2StreamTracker::kMaxGrpcMessages) return;
        GrpcMessage m;
        m.compressed = data[pos] != 0;
        m.length = readBe32(data.data() + pos + 1);
        pos += kGrpcPrefixBytes;
        if (m.length > (1u << 24)) {
            // Hostile length: keep the prefix info, stop parsing.
            m.truncated = true;
            out->push_back(std::move(m));
            return;
        }
        size_t available = data.size() - pos;
        size_t messageLen = m.length;
        bool incomplete = available < messageLen;
        size_t take = incomplete ? available : messageLen;
        if (take > H2StreamTracker::kMaxGrpcPreview) take = H2StreamTracker::kMaxGrpcPreview;
        m.preview.assign(data.data() + pos, data.data() + pos + take);
        if (incomplete || messageLen > H2StreamTracker::kMaxGrpcPreview) m.truncated = true;
        out->push_back(std::move(m));
        if (incomplete) return;
        pos += messageLen;
    }
}

std::vector<uint8_t> buildGrpcMessage(const std::vector<uint8_t>& body, bool compressed) {
    std::vector<uint8_t> out;
    out.reserve(body.size() + kGrpcPrefixBytes);
    out.push_back(compressed ? 1 : 0);
    out.push_back(static_cast<uint8_t>((body.size() >> 24) & 0xFFu));
    out.push_back(static_cast<uint8_t>((body.size() >> 16) & 0xFFu));
    out.push_back(static_cast<uint8_t>((body.size() >> 8) & 0xFFu));
    out.push_back(static_cast<uint8_t>(body.size() & 0xFFu));
    out.insert(out.end(), body.begin(), body.end());
    return out;
}

}  // namespace traffic
