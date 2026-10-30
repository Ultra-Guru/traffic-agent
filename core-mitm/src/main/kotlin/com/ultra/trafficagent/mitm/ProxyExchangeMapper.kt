package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import com.ultra.trafficagent.capture.headerValue

/**
 * ProxyExchange -> CapturedRequest conversion: the bridge between the MITM
 * capture unit and the repository/UI list model. Bodies are rendered as
 * UTF-8 when they decode losslessly, otherwise a placeholder keeps the row
 * readable (raw bytes stay available through [ProxyExchange.responseBody]).
 */
object ProxyExchangeMapper {

    private const val BINARY_PLACEHOLDER = "«binary body: N bytes»"

    fun toCapturedRequest(
        exchange: ProxyExchange,
        id: Long,
        appUid: Int? = null,
    ): CapturedRequest {
        val requestHeaders = exchange.requestHeaders.associate { it.first to it.second }
        val responseHeaders = exchange.responseHeaders.associate { it.first to it.second }
        val requestMime = headerValue(requestHeaders, "content-type")?.substringBefore(';')?.trim()
        val responseMime = headerValue(responseHeaders, "content-type")?.substringBefore(';')?.trim()
            ?: exchange.responseDecodedBody?.let { sniffTextMime(it) }
            ?: exchange.responseBody?.let { sniffTextMime(it) }

        return CapturedRequest(
            id = id,
            timestampMs = exchange.timestampMs,
            host = exchange.host,
            path = exchange.path,
            method = exchange.method,
            status = exchange.status,
            requestHeaders = requestHeaders,
            responseHeaders = responseHeaders,
            requestBody = bodyText(exchange.requestBody),
            responseBody = bodyText(exchange.responseDecodedBody ?: exchange.responseBody),
            bytesUp = exchange.requestBytes,
            bytesDown = exchange.responseBytes,
            // The MITM path terminates TLS and speaks HTTP/1.1 inside; the
            // protocol column reflects the wire protocol the client used.
            protocol = if (exchange.tls) Protocol.TLS else Protocol.HTTP1,
            appUid = appUid,
            ja3 = null,
            requestMime = requestMime?.takeIf { it.isNotEmpty() },
            responseMime = responseMime?.takeIf { it.isNotEmpty() },
            durationMs = exchange.durationMs,
            requestDecompressedBytes = null,
            responseDecompressedBytes = exchange.responseDecodedBody?.size?.toLong(),
            error = exchange.error,
        )
    }

    /** Renders a body for the UI: lossless UTF-8 or a readable placeholder. */
    fun bodyText(body: ByteArray?): String {
        if (body == null || body.isEmpty()) return ""
        val decoded = decodeUtf8(body)
        return decoded ?: BINARY_PLACEHOLDER.replace("N", body.size.toString())
    }

    private fun decodeUtf8(body: ByteArray): String? {
        return try {
            val text = String(body, Charsets.UTF_8)
            // Round-trip check: the decoder replaced invalid sequences with
            // U+FFFD, which round-tripping exposes.
            if (text.toByteArray(Charsets.UTF_8).size == body.size &&
                !text.contains('\uFFFD')
            ) {
                text
            } else {
                null
            }
        } catch (_: Exception) {
            null
        }
    }

    private fun sniffTextMime(body: ByteArray): String? {
        val text = decodeUtf8(body) ?: return null
        val trimmed = text.trimStart()
        return when {
            trimmed.startsWith("{") || trimmed.startsWith("[") -> "application/json"
            trimmed.startsWith("<") -> "text/html"
            else -> "text/plain"
        }
    }
}
