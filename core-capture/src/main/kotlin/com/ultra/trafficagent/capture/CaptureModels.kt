package com.ultra.trafficagent.capture

/**
 * Case-insensitive lookup in a header map (HTTP header names are
 * case-insensitive but the maps we capture keep the original casing).
 */
fun headerValue(headers: Map<String, String>, name: String): String? =
    headers.entries.firstOrNull { it.key.equals(name, ignoreCase = true) }?.value

/** L7 protocol classification for a captured exchange. */
enum class Protocol {
    HTTP1, HTTP2, TLS, WEBSOCKET, QUIC, DNS, TCP, UDP, UNKNOWN
}

/** One captured request/response exchange (the unit shown in the UI list). */
data class CapturedRequest(
    val id: Long,
    val timestampMs: Long,
    val host: String,
    val path: String,
    val method: String,
    val status: Int?,
    val requestHeaders: Map<String, String>,
    val responseHeaders: Map<String, String>,
    val requestBody: String,
    val responseBody: String,
    val bytesUp: Long,
    val bytesDown: Long,
    val protocol: Protocol,
    val appUid: Int?,
    // --- optional enrichment fields (defaulted, binary-compatible additions) ---
    /** TLS ClientHello fingerprint (JA3 MD5) when the ClientHello was parsed. */
    val ja3: String? = null,
    /** Sniffed request MIME type (from Content-Type, params stripped). */
    val requestMime: String? = null,
    /** Sniffed response MIME type (from Content-Type, params stripped). */
    val responseMime: String? = null,
    /** Total exchange duration in milliseconds, when measured. */
    val durationMs: Long? = null,
    /** Request body size after gzip/deflate decompression, when applicable. */
    val requestDecompressedBytes: Long? = null,
    /** Response body size after gzip/deflate decompression, when applicable. */
    val responseDecompressedBytes: Long? = null,
    /** Capture/decode error attached to this exchange, if any. */
    val error: String? = null,
) {
    val isSecure: Boolean get() = protocol == Protocol.TLS || (path.startsWith("https"))
    val requestSize: Long get() = bytesUp
    val responseSize: Long get() = bytesDown
    val totalSize: Long get() = bytesUp + bytesDown

    /** Response content type without parameters ("application/json; charset" -> "application/json"). */
    val contentType: String?
        get() = headerValue(responseHeaders, "content-type")?.substringBefore(';')?.trim()
}

/** Raw IPv4 packet handed to the native engine. */
data class RawPacket(
    val timestampMs: Long,
    val bytes: ByteArray,
    val appUid: Int? = null,
)

/** Capture channel selection (SPEC v2.1: VPN default, root increments). */
enum class CaptureMode { VPN, ROOT_IPTABLES, ROOT_PCAP_FILE }
