#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace traffic {

struct Http1Headers {
    std::vector<std::pair<std::string, std::string>> entries;

    // Case-insensitive lookup; returns "" when absent.
    std::string get(const std::string& name) const;
    bool has(const std::string& name) const { return !get(name).empty(); }
    size_t size() const { return entries.size(); }
};

struct Http1Request {
    std::string method;
    std::string target;
    std::string version;
    Http1Headers headers;
    size_t headerEnd = 0;  // offset just past the terminating CRLFCRLF
    size_t contentLength = 0;
    bool chunked = false;
    bool keepAlive = true;
};

struct Http1Response {
    std::string version;
    int status = 0;
    std::string reason;
    Http1Headers headers;
    size_t headerEnd = 0;
    size_t contentLength = 0;
    bool chunked = false;
    bool keepAlive = true;
};

enum class Http1Status { Ok, TooShort, MalformedRequestLine, MalformedHeaders, BadContentLength };

Http1Status parseHttpRequest(const uint8_t* data, size_t len, Http1Request* out);
Http1Status parseHttpResponse(const uint8_t* data, size_t len, Http1Response* out);

}  // namespace traffic
