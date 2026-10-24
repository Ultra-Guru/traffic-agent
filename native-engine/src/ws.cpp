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

WsStatus decodeWsFrame(const uint8_t* data, size_t len, WsFrameInfo* out,
                       std::vector<uint8_t>* unmaskedPayload) {
    if (data == nullptr || out == nullptr || unmaskedPayload == nullptr) {
        return WsStatus::TooShort;
    }
    unmaskedPayload->clear();
    WsStatus s = parseWsFrame(data, len, out);
    if (s != WsStatus::Ok) return s;
    if (out->masked && out->headerLength < 6) return WsStatus::BadMask;  // mask key missing
    if (out->headerLength > len) return WsStatus::TooShort;  // mask key truncated
    uint64_t need = out->headerLength + out->payloadLength;
    if (need > len) return WsStatus::TooShort;  // payload truncated  // MUT:>=
    const uint8_t* payload = data + out->headerLength;
    if (out->masked) {
        const uint8_t* key = data + out->headerLength - 4;
        unmaskedPayload->reserve(static_cast<size_t>(out->payloadLength));
        for (uint64_t i = 0; i < out->payloadLength; ++i) {
            unmaskedPayload->push_back(payload[i] ^ key[i % 4]);  // MUT:|
        }
    } else {
        unmaskedPayload->assign(payload, payload + out->payloadLength);
    }
    return WsStatus::Ok;
}

// ---------------- WsMessageAssembler ----------------

void WsMessageAssembler::feed(const uint8_t* data, size_t len) {
    if (data == nullptr || len == 0) return;
    buf_.insert(buf_.end(), data, data + len);
    tryParse();
}

void WsMessageAssembler::tryParse() {
    while (true) {
        WsFrameInfo info{};
        WsStatus s = parseWsFrame(buf_.data(), buf_.size(), &info);
        if (s != WsStatus::Ok) break;  // incomplete header: wait for more bytes
        uint64_t total = info.headerLength + info.payloadLength;
        if (total > buf_.size()) break;  // incomplete payload  // MUT:<
        std::vector<uint8_t> payload;
        s = decodeWsFrame(buf_.data(), buf_.size(), &info, &payload);
        if (s != WsStatus::Ok) {
            // unrecoverable (bad mask / oversized): drop the frame and stop
            buf_.clear();
            return;
        }
        const uint8_t opcode = info.opcode;
        const bool control = (opcode & 0x8u) != 0;
        if (control) {
            // Control frames interleave freely with fragmented data frames.
            WsMessage m;
            m.opcode = opcode;
            m.payload = std::move(payload);
            m.fin = true;
            messages_.push_back(std::move(m));
        } else if (opcode == kWsContinuation) {
            if (!fragmenting_) {
                // protocol violation: drop everything buffered so far
                buf_.clear();
                return;
            }
            pendingPayload_.insert(pendingPayload_.end(), payload.begin(), payload.end());
            if (info.fin) {
                WsMessage m;
                m.opcode = pendingOpcode_;
                m.payload = std::move(pendingPayload_);
                m.fin = true;
                messages_.push_back(std::move(m));
                fragmenting_ = false;
                pendingPayload_.clear();
            }
        } else {
            // text/binary frame
            if (info.fin) {
                WsMessage m;
                m.opcode = opcode;
                m.payload = std::move(payload);
                m.fin = true;
                messages_.push_back(std::move(m));
            } else {
                // start of a fragmented message
                fragmenting_ = true;
                pendingOpcode_ = opcode;
                pendingPayload_ = std::move(payload);
            }
        }
        buf_.erase(buf_.begin(),
                   buf_.begin() + static_cast<std::ptrdiff_t>(total));
    }
}

std::vector<WsMessage> WsMessageAssembler::takeMessages() {
    std::vector<WsMessage> out = std::move(messages_);
    messages_.clear();
    return out;
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
