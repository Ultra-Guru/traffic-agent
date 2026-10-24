#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace traffic {

struct MultipartPart {
    std::vector<std::pair<std::string, std::string>> headers;
    std::string name;         // Content-Disposition name=
    std::string filename;     // Content-Disposition filename= ("" when absent)
    std::string contentType;  // part Content-Type ("" when absent)
    std::vector<uint8_t> body;
};

enum class MultipartStatus {
    Ok,
    NoBoundary,       // Content-Type header carried no boundary parameter
    Malformed         // structural violation (bad delimiter, unterminated part, ...)
};

// Parses a multipart/form-data body given the full Content-Type header value,
// e.g. "multipart/form-data; boundary=----WebKitFormBoundaryX". Handles
// quoted and bare boundary tokens, CRLF and LF line endings, and the
// terminating "--boundary--" delimiter.
MultipartStatus parseMultipart(const uint8_t* data, size_t len,
                               const std::string& contentTypeHeader,
                               std::vector<MultipartPart>* parts);

// Extracts the boundary token from a Content-Type header value (quoted or
// bare); empty string when absent.
std::string multipartBoundary(const std::string& contentTypeHeader);

}  // namespace traffic
