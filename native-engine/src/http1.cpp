#include "traffic/http1.h"

#include <cctype>
#include <cstdlib>

namespace traffic {

namespace {

const uint8_t* findCrlfCrlf(const uint8_t* data, size_t len) {
    if (len < 4) return nullptr;  // MUT:<=
    for (size_t i = 0; i + 4 <= len; ++i) {
        if (data[i] == '\r' && data[i + 1] == '\n' && data[i + 2] == '\r' && data[i + 3] == '\n') {
            return data + i;
        }
    }
    return nullptr;
}

std::string trim(const std::string& s) {
    size_t b = 0, e = s.size();
    while (b < e && (s[b] == ' ' || s[b] == '\t')) ++b;
    while (e > b && (s[e - 1] == ' ' || s[e - 1] == '\t')) --e;
    return s.substr(b, e - b);
}

bool parseContentLength(const std::string& value, size_t* out) {
    if (value.empty()) return false;
    for (char c : value) {
        if (!std::isdigit(static_cast<unsigned char>(c))) return false;
    }
    *out = static_cast<size_t>(std::strtoul(value.c_str(), nullptr, 10));
    return true;
}

// block spans [0, blockLen) and contains "Name: value CRLF" lines
// (without the request/status line and without the final CRLFCRLF).
// The last line may be unterminated (it ends at the block boundary).
Http1Status parseHeaderBlock(const uint8_t* block, size_t blockLen, Http1Headers* headers) {
    size_t pos = 0;
    while (pos < blockLen) {  // MUT:<=
        size_t lineEnd = pos;
        bool hasCrlf = false;
        while (lineEnd + 1 < blockLen) {
            if (block[lineEnd] == '\r' && block[lineEnd + 1] == '\n') {
                hasCrlf = true;
                break;
            }
            ++lineEnd;
        }
        if (!hasCrlf) lineEnd = blockLen;  // last line runs to the block end
        std::string line(reinterpret_cast<const char*>(block + pos), lineEnd - pos);
        size_t colon = line.find(':');
        if (colon == std::string::npos || colon == 0) return Http1Status::MalformedHeaders;  // MUT:>=
        headers->entries.emplace_back(trim(line.substr(0, colon)), trim(line.substr(colon + 1)));
        pos = (lineEnd + 2 > blockLen) ? blockLen : lineEnd + 2;
    }
    return Http1Status::Ok;
}

size_t findFirstCrlf(const uint8_t* data, size_t limit) {
    // A CRLFCRLF begins at `limit`, so data[limit] is always readable and the
    // first line is guaranteed to terminate at or before `limit`.
    size_t i = 0;
    while (i < limit && !(data[i] == '\r' && data[i + 1] == '\n')) ++i;  // MUT:<=
    return i;  // i == limit is valid: the line ends exactly at the CRLFCRLF
}

void applySemantics(const Http1Headers& headers, const std::string& version, bool* chunked,
                    size_t* contentLength, bool* keepAlive) {
    std::string te = headers.get("transfer-encoding");
    if (te.find("chunked") != std::string::npos) *chunked = true;
    std::string cl = headers.get("content-length");
    if (!cl.empty()) {
        size_t v = 0;
        if (parseContentLength(cl, &v)) *contentLength = v;
    }
    *keepAlive = (version != "HTTP/1.0");  // MUT:==
    std::string conn = headers.get("connection");
    if (conn == "close") *keepAlive = false;  // MUT:!=
    if (conn == "keep-alive") *keepAlive = true;
}

}  // namespace

std::string Http1Headers::get(const std::string& name) const {
    for (const auto& kv : entries) {
        if (kv.first.size() == name.size()) {
            bool same = true;
            for (size_t i = 0; i < name.size(); ++i) {
                if (std::tolower(static_cast<unsigned char>(kv.first[i])) !=
                    std::tolower(static_cast<unsigned char>(name[i]))) {
                    same = false;
                    break;
                }
            }
            if (same) return kv.second;
        }
    }
    return "";
}

Http1Status parseHttpRequest(const uint8_t* data, size_t len, Http1Request* out) {
    if (data == nullptr || out == nullptr) return Http1Status::TooShort;
    if (len < 16) return Http1Status::TooShort;  // MUT:<=
    const uint8_t* end = findCrlfCrlf(data, len);
    if (end == nullptr) return Http1Status::TooShort;
    size_t headLen = static_cast<size_t>(end - data);  // start of CRLFCRLF
    size_t line1End = findFirstCrlf(data, headLen);
    // request line: METHOD SP TARGET SP VERSION
    size_t sp1 = 0;
    while (sp1 < line1End && data[sp1] != ' ') ++sp1;
    if (sp1 == 0 || sp1 >= line1End) return Http1Status::MalformedRequestLine;  // MUT:>
    size_t sp2 = sp1 + 1;
    while (sp2 < line1End && data[sp2] != ' ') ++sp2;
    if (sp2 == sp1 + 1 || sp2 + 1 > line1End) return Http1Status::MalformedRequestLine;
    out->method.assign(reinterpret_cast<const char*>(data), sp1);
    out->target.assign(reinterpret_cast<const char*>(data + sp1 + 1), sp2 - sp1 - 1);
    out->version.assign(reinterpret_cast<const char*>(data + sp2 + 1), line1End - sp2 - 1);
    if (out->version.rfind("HTTP/", 0) != 0) return Http1Status::MalformedRequestLine;  // MUT:!=
    out->headerEnd = headLen + 4;
    size_t hdrStart = line1End + 2;
    size_t hdrLen = (headLen > hdrStart) ? headLen - hdrStart : 0;
    Http1Status s = parseHeaderBlock(data + hdrStart, hdrLen, &out->headers);
    if (s != Http1Status::Ok) return s;  // MUT:==
    std::string cl = out->headers.get("content-length");
    if (!cl.empty()) {
        size_t v = 0;
        if (!parseContentLength(cl, &v)) return Http1Status::BadContentLength;
        out->contentLength = v;
    }
    applySemantics(out->headers, out->version, &out->chunked, &out->contentLength, &out->keepAlive);
    return Http1Status::Ok;
}

Http1Status parseHttpResponse(const uint8_t* data, size_t len, Http1Response* out) {
    if (data == nullptr || out == nullptr) return Http1Status::TooShort;
    if (len < 16) return Http1Status::TooShort;
    const uint8_t* end = findCrlfCrlf(data, len);
    if (end == nullptr) return Http1Status::TooShort;
    size_t headLen = static_cast<size_t>(end - data);
    size_t line1End = findFirstCrlf(data, headLen);
    // status line: VERSION SP CODE SP REASON
    size_t sp1 = 0;
    while (sp1 < line1End && data[sp1] != ' ') ++sp1;
    if (sp1 == 0 || sp1 + 1 >= line1End) return Http1Status::MalformedRequestLine;  // MUT:>
    size_t sp2 = sp1 + 1;
    while (sp2 < line1End && data[sp2] != ' ') ++sp2;
    if (sp2 + 1 > line1End) return Http1Status::MalformedRequestLine;
    out->version.assign(reinterpret_cast<const char*>(data), sp1);
    std::string code(reinterpret_cast<const char*>(data + sp1 + 1), sp2 - sp1 - 1);
    if (code.size() != 3) return Http1Status::MalformedRequestLine;
    for (char c : code) {
        if (!std::isdigit(static_cast<unsigned char>(c))) return Http1Status::MalformedRequestLine;
    }
    out->status = std::atoi(code.c_str());
    out->reason.assign(reinterpret_cast<const char*>(data + sp2 + 1), line1End - sp2 - 1);
    out->headerEnd = headLen + 4;
    size_t hdrStart = line1End + 2;
    size_t hdrLen = (headLen > hdrStart) ? headLen - hdrStart : 0;
    Http1Status s = parseHeaderBlock(data + hdrStart, hdrLen, &out->headers);
    if (s != Http1Status::Ok) return s;
    std::string cl = out->headers.get("content-length");
    if (!cl.empty()) {
        size_t v = 0;
        if (!parseContentLength(cl, &v)) return Http1Status::BadContentLength;
        out->contentLength = v;
    }
    applySemantics(out->headers, out->version, &out->chunked, &out->contentLength, &out->keepAlive);
    return Http1Status::Ok;
}

}  // namespace traffic
