package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest

/**
 * Human-readable share formats: the raw HTTP/1.1 request+response pair as
 * plain text (HttpCanary's "share as text") plus a HAR-friendly single
 * request dump.
 */
object RawHttpExporter {

    /** Full request/response pair separated by a marker line. */
    fun toShareText(c: CapturedRequest): String =
        toRawHttpRequest(c) + "\n\n=== RESPONSE ===\n\n" + toRawHttpResponse(c)

    /** Wire-format request reproduction. */
    fun toRawHttpRequest(c: CapturedRequest): String {
        val sb = StringBuilder()
        sb.append(c.method).append(' ').append(c.path).append(" HTTP/1.1\r\n")
        sb.append("Host: ").append(c.host).append("\r\n")
        for ((name, value) in c.requestHeaders) {
            if (name.equals("host", true)) continue
            sb.append(name).append(": ").append(value).append("\r\n")
        }
        if (c.requestBody.isNotEmpty()) {
            sb.append("Content-Length: ").append(c.requestBody.length).append("\r\n")
        }
        sb.append("\r\n")
        sb.append(c.requestBody)
        return sb.toString()
    }

    /** Wire-format response reproduction. */
    fun toRawHttpResponse(c: CapturedRequest): String {
        val sb = StringBuilder()
        val status = c.status ?: 0
        sb.append("HTTP/1.1 ").append(status).append(' ').append(reason(status)).append("\r\n")
        for ((name, value) in c.responseHeaders) {
            sb.append(name).append(": ").append(value).append("\r\n")
        }
        sb.append("\r\n")
        sb.append(c.responseBody)
        return sb.toString()
    }

    private fun reason(status: Int): String = when (status) {
        200 -> "OK"
        201 -> "Created"
        204 -> "No Content"
        301 -> "Moved Permanently"
        302 -> "Found"
        304 -> "Not Modified"
        400 -> "Bad Request"
        401 -> "Unauthorized"
        403 -> "Forbidden"
        404 -> "Not Found"
        429 -> "Too Many Requests"
        500 -> "Internal Server Error"
        502 -> "Bad Gateway"
        503 -> "Service Unavailable"
        else -> "Status"
    }
}
