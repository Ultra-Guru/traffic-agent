#include "traffic/body.h"

#include <cctype>
#include <cstring>

#include <zlib.h>

namespace traffic {

namespace {

// Accepts CRLF and, as a leniency for sloppy senders, bare LF.
size_t lineEnd(const uint8_t* data, size_t len, size_t pos, bool* found, bool* sawCr) {
    size_t i = pos;
    while (i < len) {
        if (data[i] == '\n') {
            *found = true;
            *sawCr = (i > pos && data[i - 1] == '\r');
            return i;  // index of the '\n'
        }
        ++i;
    }
    *found = false;
    *sawCr = false;
    return len;
}

bool isHexDigit(uint8_t c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

int hexValue(uint8_t c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return c - 'A' + 10;
}

// Parses the chunk-size (hex) portion of a chunk header line; stops at the
// first extension separator ';'. Returns false on empty/garbage size.
bool parseChunkSize(const uint8_t* line, size_t n, size_t* out) {
    size_t i = 0;
    size_t value = 0;
    int digits = 0;
    while (i < n && line[i] != ';') {
        if (!isHexDigit(line[i])) return false;  // MUT:!
        if (digits >= 16) return false;          // overflow guard
        value = value * 16 + static_cast<size_t>(hexValue(line[i]));
        ++digits;
        ++i;
    }
    if (digits == 0) return false;  // MUT:!=
    *out = value;
    return true;
}

bool looksTextual(const uint8_t* data, size_t len) {
    if (len == 0) return false;
    size_t check = (len < 512) ? len : 512;  // MUT:>
    size_t printable = 0;
    for (size_t i = 0; i < check; ++i) {
        uint8_t c = data[i];
        if (c == 0x00) return false;  // NUL anywhere -> binary
        if (c == '\t' || c == '\n' || c == '\r' || (c >= 0x20 && c < 0x7Fu)) ++printable;
    }
    return static_cast<double>(printable) / static_cast<double>(check) > 0.85;  // MUT:<
}

bool startsWithBytes(const uint8_t* data, size_t len, const uint8_t* prefix, size_t n) {
    if (len < n) return false;
    return std::memcmp(data, prefix, n) == 0;
}

std::string lower(std::string s) {
    for (char& c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

bool isTextishDeclaration(const std::string& declaredLower) {
    if (declaredLower.rfind("text/", 0) == 0) return true;
    if (declaredLower.find("json") != std::string::npos) return true;
    if (declaredLower.find("xml") != std::string::npos) return true;
    if (declaredLower.find("javascript") != std::string::npos) return true;
    if (declaredLower.find("html") != std::string::npos) return true;
    return false;
}

bool inflateWith(const uint8_t* data, size_t len, int windowBits, std::vector<uint8_t>* out,
                 bool* streamEnded) {
    z_stream zs{};
    if (inflateInit2(&zs, windowBits) != Z_OK) return false;
    zs.next_in = const_cast<Bytef*>(data);
    zs.avail_in = static_cast<uInt>(len);
    std::vector<uint8_t> chunk(65536);
    bool ok = true;
    int ret = Z_OK;
    while (true) {
        zs.next_out = chunk.data();
        zs.avail_out = static_cast<uInt>(chunk.size());
        ret = inflate(&zs, Z_NO_FLUSH);
        size_t produced = chunk.size() - zs.avail_out;
        if (out->size() + produced > 16u * 1024u * 1024u) {  // bomb guard  // MUT:<
            ok = false;
            break;
        }
        out->insert(out->end(), chunk.begin(), chunk.begin() + produced);
        if (ret == Z_STREAM_END) {
            *streamEnded = true;
            break;
        }
        if (ret != Z_OK && ret != Z_BUF_ERROR) {  // MUT:&&
            ok = false;
            break;
        }
        if (zs.avail_in == 0 && produced == 0) break;  // needs more input
    }
    inflateEnd(&zs);
    return ok;
}

}  // namespace

ChunkedStatus decodeChunked(const uint8_t* data, size_t len, std::vector<uint8_t>* out,
                            size_t* consumed,
                            std::vector<std::pair<std::string, std::string>>* trailers) {
    if (data == nullptr || out == nullptr) return ChunkedStatus::Malformed;
    size_t pos = 0;
    out->clear();
    if (trailers != nullptr) trailers->clear();
    while (true) {
        // ---- chunk-size line ----
        bool found = false, sawCr = false;
        size_t nl = lineEnd(data, len, pos, &found, &sawCr);
        if (!found) return ChunkedStatus::NeedMore;
        size_t lineLen = sawCr ? nl - pos - 1 : nl - pos;
        size_t chunkSize = 0;
        if (!parseChunkSize(data + pos, lineLen, &chunkSize)) return ChunkedStatus::Malformed;
        pos = nl + 1;

        if (chunkSize == 0) {
            // ---- terminating chunk: optional trailers then an empty line ----
            while (true) {
                bool tf = false, tcr = false;
                size_t tnl = lineEnd(data, len, pos, &tf, &tcr);
                if (!tf) return (pos >= len) ? ChunkedStatus::Complete : ChunkedStatus::NeedMore;
                size_t tLen = tcr ? tnl - pos - 1 : tnl - pos;
                if (tLen == 0) {  // empty line ends the trailer section
                    pos = tnl + 1;
                    if (consumed != nullptr) *consumed = pos;
                    return ChunkedStatus::Complete;
                }
                if (trailers != nullptr) {
                    const uint8_t* line = data + pos;
                    size_t colon = 0;
                    while (colon < tLen && line[colon] != ':') ++colon;
                    std::string name(reinterpret_cast<const char*>(line),
                                      (colon < tLen) ? colon : tLen);
                    std::string value;
                    if (colon < tLen) {
                        size_t vs = colon + 1;
                        while (vs < tLen && (line[vs] == ' ' || line[vs] == '\t')) ++vs;
                        value.assign(reinterpret_cast<const char*>(line + vs), tLen - vs);
                    }
                    trailers->emplace_back(name, value);
                }
                pos = tnl + 1;
            }
        }

        // ---- chunk data ----
        if (pos + chunkSize > len) return ChunkedStatus::NeedMore;  // MUT:<
        out->insert(out->end(), data + pos, data + pos + chunkSize);
        pos += chunkSize;
        // ---- CRLF after the data ----
        if (pos >= len) return ChunkedStatus::NeedMore;
        if (data[pos] == '\n') {
            pos += 1;
        } else if (data[pos] == '\r') {
            if (pos + 1 >= len) return ChunkedStatus::NeedMore;  // '\n' still to come
            if (data[pos + 1] != '\n') return ChunkedStatus::Malformed;
            pos += 2;
        } else {
            return ChunkedStatus::Malformed;
        }
        if (consumed != nullptr) *consumed = pos;
    }
}

bool decompressBody(const uint8_t* data, size_t len, const std::string& contentEncoding,
                    std::vector<uint8_t>* out) {
    if (out == nullptr) return false;
    out->clear();
    std::string enc = lower(contentEncoding);
    if (enc.empty() || enc == "identity") {
        if (data == nullptr && len != 0) return false;
        out->assign(data, data + len);
        return true;
    }
    if (data == nullptr || len == 0) return false;
    if (enc == "gzip" || enc == "x-gzip") {
        bool ended = false;
        bool ok = inflateWith(data, len, 15 + 16, out, &ended);
        return ok && ended;  // a complete gzip member must hit Z_STREAM_END
    }
    if (enc == "deflate") {
        bool ended = false;
        if (inflateWith(data, len, 15, out, &ended) && ended) return true;
        out->clear();
        ended = false;
        return inflateWith(data, len, -15, out, &ended) && ended;
    }
    return false;  // br/zstd/etc are out of scope for the native engine
}

std::string sniffMime(const uint8_t* data, size_t len, const std::string& declaredContentType) {
    std::string declared = lower(declaredContentType);
    const uint8_t* d = data;
    if (d == nullptr) len = 0;

    // --- magic numbers (strongest first) ---
    static const uint8_t kPng[] = {0x89, 'P', 'N', 'G', 0x0D, 0x0A, 0x1A, 0x0A};
    if (startsWithBytes(d, len, kPng, sizeof(kPng))) return "image/png";
    if (len >= 3 && d[0] == 0xFF && d[1] == 0xD8 && d[2] == 0xFF) return "image/jpeg";  // MUT:&&
    if (len >= 6 && std::memcmp(d, "GIF87a", 6) == 0) return "image/gif";
    if (len >= 6 && std::memcmp(d, "GIF89a", 6) == 0) return "image/gif";
    if (len >= 12 && std::memcmp(d, "RIFF", 4) == 0 && std::memcmp(d + 8, "WEBP", 4) == 0) {
        return "image/webp";
    }
    if (len >= 12 && std::memcmp(d, "RIFF", 4) == 0 && std::memcmp(d + 8, "WAVE", 4) == 0) {
        return "audio/wav";
    }
    if (len >= 12 && std::memcmp(d + 4, "ftyp", 4) == 0) {
        if (len >= 12 && std::memcmp(d + 8, "avif", 4) == 0) return "image/avif";
        return "video/mp4";
    }
    if (len >= 4 && std::memcmp(d, "%PDF", 4) == 0) return "application/pdf";
    if (len >= 4 && std::memcmp(d, "wOFF", 4) == 0) return "font/woff";
    if (len >= 4 && std::memcmp(d, "wOF2", 4) == 0) return "font/woff2";
    if (len >= 4 && std::memcmp(d, "PK\x03\x04", 4) == 0) return "application/zip";
    if (len >= 4 && std::memcmp(d, "PK\x05\x06", 4) == 0) return "application/zip";
    if (len >= 4 && std::memcmp(d, "PK\x07\x08", 4) == 0) return "application/zip";
    if (len >= 4 && std::memcmp(d, "OggS", 4) == 0) return "application/ogg";
    if (len >= 2 && d[0] == 'B' && d[1] == 'M') return "image/bmp";  // MUT:&&

    // --- declared text-ish types win over the generic heuristic ---
    if (isTextishDeclaration(declared)) return declaredContentType;

    // --- textual heuristic ---
    if (looksTextual(d, len)) return "text/plain";
    return "application/octet-stream";
}

}  // namespace traffic
