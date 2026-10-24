#include "traffic/multipart.h"

#include <cctype>

namespace traffic {

namespace {

std::string lower(std::string s) {
    for (char& c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

std::string trim(const std::string& s) {
    size_t b = 0, e = s.size();
    while (b < e && (s[b] == ' ' || s[b] == '\t')) ++b;
    while (e > b && (s[e - 1] == ' ' || s[e - 1] == '\t')) --e;
    return s.substr(b, e - b);
}

// Finds the next delimiter that sits at the start of a line at or after
// `from`. Returns len when none is found.
size_t findLineStartDelimiter(const uint8_t* data, size_t len, const std::string& delim,
                              size_t from) {
    if (delim.empty()) return len;
    for (size_t i = from; i + delim.size() <= len; ++i) {
        if (i > 0 && data[i - 1] != '\n') continue;  // must start a line
        bool match = true;
        for (size_t j = 0; j < delim.size(); ++j) {
            if (data[i + j] != static_cast<uint8_t>(delim[j])) {
                match = false;
                break;
            }
        }
        if (match) return i;
    }
    return len;
}

// Consumes a LF or CRLF at data[pos]; returns the new position, or `len`
// (with *ok=false) when neither is present.
size_t skipLineEnd(const uint8_t* data, size_t len, size_t pos, bool* ok) {
    if (pos >= len) {
        *ok = false;
        return len;
    }
    if (data[pos] == '\n') {
        *ok = true;  // MUT:!
        return pos + 1;
    }
    if (data[pos] == '\r' && pos + 1 < len && data[pos + 1] == '\n') {
        *ok = true;
        return pos + 2;
    }
    *ok = false;
    return len;
}

// Extracts a `key=value` parameter (value possibly quoted) from a
// Content-Disposition style header value.
std::string dispositionParam(const std::string& value, const std::string& key) {
    std::string needle = key + "=";
    std::string v = lower(value);
    size_t pos = 0;
    while (true) {
        size_t hit = v.find(needle, pos);
        if (hit == std::string::npos) return "";
        // must be at a parameter boundary ("; " or start)
        if (hit != 0 && v[hit - 1] != ' ' && v[hit - 1] != ';' && v[hit - 1] != '\t') {
            pos = hit + 1;
            continue;
        }
        size_t vs = hit + needle.size();
        if (vs < value.size() && value[vs] == '"') {
            size_t end = value.find('"', vs + 1);
            if (end == std::string::npos) end = value.size();
            return value.substr(vs + 1, end > vs + 1 ? end - vs - 1 : 0);
        }
        size_t vend = value.find(';', vs);
        if (vend == std::string::npos) vend = value.size();
        return trim(value.substr(vs, vend - vs));
    }
}

}  // namespace

std::string multipartBoundary(const std::string& contentTypeHeader) {
    std::string low = lower(contentTypeHeader);
    size_t hit = low.find("boundary=");
    if (hit == std::string::npos) return "";
    size_t vs = hit + 9;  // strlen("boundary=")
    if (vs < contentTypeHeader.size() && contentTypeHeader[vs] == '"') {
        size_t end = contentTypeHeader.find('"', vs + 1);
        if (end == std::string::npos) end = contentTypeHeader.size();
        return contentTypeHeader.substr(vs + 1, end > vs + 1 ? end - vs - 1 : 0);
    }
    size_t vend = contentTypeHeader.find(';', vs);
    if (vend == std::string::npos) vend = contentTypeHeader.size();
    return trim(contentTypeHeader.substr(vs, vend - vs));
}

MultipartStatus parseMultipart(const uint8_t* data, size_t len,
                               const std::string& contentTypeHeader,
                               std::vector<MultipartPart>* parts) {
    if (parts == nullptr) return MultipartStatus::Malformed;
    parts->clear();
    std::string boundary = multipartBoundary(contentTypeHeader);
    if (boundary.empty()) return MultipartStatus::NoBoundary;
    if (data == nullptr) return MultipartStatus::Malformed;

    std::string delim = "--" + boundary;
    size_t pos = findLineStartDelimiter(data, len, delim, 0);
    if (pos >= len) return MultipartStatus::Malformed;  // no opening delimiter

    while (true) {
        bool ok = false;
        size_t after = skipLineEnd(data, len, pos + delim.size(), &ok);
        // `--boundary--` terminates the body.
        if (!ok && pos + delim.size() + 2 <= len &&
            data[pos + delim.size()] == '-' && data[pos + delim.size() + 1] == '-') {
            return MultipartStatus::Ok;  // terminator without trailing newline
        }
        if (!ok) return MultipartStatus::Malformed;
        if (pos + delim.size() + 2 <= len && data[pos + delim.size()] == '-' &&
            data[pos + delim.size() + 1] == '-') {
            return MultipartStatus::Ok;  // clean terminator  // MUT:&&
        }

        // ---- part header block ----
        MultipartPart part;
        while (true) {
            bool lf = false, cr = false;
            size_t e = after;
            while (e < len) {
                if (data[e] == '\n') {
                    lf = true;
                    cr = (e > after && data[e - 1] == '\r');
                    break;
                }
                ++e;
            }
            if (!lf) return MultipartStatus::Malformed;  // unterminated header line
            size_t lineLen = cr ? e - after - 1 : e - after;
            if (lineLen == 0) {  // empty line: end of headers
                after = e + 1;
                break;
            }
            std::string line(reinterpret_cast<const char*>(data + after), lineLen);
            size_t colon = line.find(':');
            if (colon != std::string::npos) {
                part.headers.emplace_back(trim(line.substr(0, colon)),
                                          trim(line.substr(colon + 1)));
            }
            after = e + 1;
        }

        // ---- part body: runs until the next line-start delimiter ----
        size_t next = findLineStartDelimiter(data, len, delim, after);
        if (next >= len) return MultipartStatus::Malformed;  // unterminated part
        size_t bodyEnd = next;
        if (bodyEnd > after && data[bodyEnd - 1] == '\n') --bodyEnd;
        if (bodyEnd > after && data[bodyEnd - 1] == '\r') --bodyEnd;  // MUT:&&
        part.body.assign(data + after, data + bodyEnd);

        // ---- header semantics ----
        for (const auto& kv : part.headers) {
            std::string n = lower(kv.first);
            if (n == "content-disposition") {
                part.name = dispositionParam(kv.second, "name");
                part.filename = dispositionParam(kv.second, "filename");
            } else if (n == "content-type") {
                part.contentType = kv.second;
            }
        }
        parts->push_back(std::move(part));
        pos = next;
    }
}

}  // namespace traffic
