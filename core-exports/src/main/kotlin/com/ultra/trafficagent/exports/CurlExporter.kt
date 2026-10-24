package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest

/** cURL command reproduction (Reqable/Postman-style replay). */
object CurlExporter {

    fun toCurl(req: CapturedRequest, includeBody: Boolean = true): String {
        val parts = mutableListOf("curl", "-X", req.method)
        parts += shellQuote("https://${req.host}${req.path}")
        for ((name, value) in req.requestHeaders) {
            parts += "-H"
            parts += shellQuote("$name: $value")
        }
        if (includeBody && req.requestBody.isNotEmpty()) {
            parts += "--data-raw"
            parts += shellQuote(req.requestBody)
        }
        parts += "--compressed"
        return parts.joinToString(" ")
    }

    /** POSIX single-quote wrapping: embedded quotes close, escape and reopen. */
    fun shellQuote(s: String): String = "'${s.replace("'", "'\\''")}'"
}
