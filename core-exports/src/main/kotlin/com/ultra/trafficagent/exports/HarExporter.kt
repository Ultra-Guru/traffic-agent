package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest
import java.time.Instant

/**
 * HTTP Archive (HAR) 1.2 export — the interchange format shared with
 * Chrome DevTools, Charles and Reqable.
 */
object HarExporter {

    fun export(
        requests: List<CapturedRequest>,
        creator: String = "traffic-agent",
        creatorVersion: String = "0.1.0",
        title: String = "traffic-agent capture",
    ): String {
        val entries = requests.joinToString(",\n") { entry(it) }
        return """
{
  "log": {
    "version": "1.2",
    "creator": ${JsonWriter.obj("name" to JsonWriter.str(creator), "version" to JsonWriter.str(creatorVersion))},
    "pages": [],
    "entries": [
${entries.indentJson()}
    ]
  }
}
""".trim()
    }

    fun entry(req: CapturedRequest): String {
        val startedAt = Instant.ofEpochMilli(req.timestampMs).toString()
        val requestHeaders = headerArray(req.requestHeaders)
        val responseHeaders = headerArray(req.responseHeaders)
        val request = JsonWriter.obj(
            "method" to JsonWriter.str(req.method),
            "url" to JsonWriter.str(urlOf(req)),
            "httpVersion" to JsonWriter.str("HTTP/1.1"),
            "cookies" to "[]",
            "headers" to requestHeaders,
            "queryString" to "[]",
            "headersSize" to JsonWriter.num(-1),
            "bodySize" to JsonWriter.num(req.bytesUp),
        )
        val response = JsonWriter.obj(
            "status" to JsonWriter.num((req.status ?: 0).toLong()),
            "statusText" to JsonWriter.str(req.status?.let { "" } ?: "pending"),
            "httpVersion" to JsonWriter.str("HTTP/1.1"),
            "cookies" to "[]",
            "headers" to responseHeaders,
            "content" to JsonWriter.obj(
                "size" to JsonWriter.num(req.bytesDown),
                "mimeType" to JsonWriter.str(req.responseHeaders["Content-Type"] ?: ""),
                "text" to JsonWriter.str(req.responseBody.take(4096)),
            ),
            "redirectURL" to JsonWriter.str(""),
            "headersSize" to JsonWriter.num(-1),
            "bodySize" to JsonWriter.num(req.bytesDown),
        )
        return JsonWriter.obj(
            "startedDateTime" to JsonWriter.str(startedAt),
            "time" to JsonWriter.num(0),
            "request" to request,
            "response" to response,
            "cache" to "{}",
            "timings" to JsonWriter.obj("send" to "0", "wait" to "0", "receive" to "0"),
        )
    }

    private fun headerArray(headers: Map<String, String>): String =
        JsonWriter.arr(headers.map { (k, v) ->
            JsonWriter.obj("name" to JsonWriter.str(k), "value" to JsonWriter.str(v))
        })

    private fun urlOf(req: CapturedRequest): String =
        "https://${req.host}${req.path}"

    private fun String.indentJson(): String =
        lines().joinToString("\n") { "    $it" }
}
