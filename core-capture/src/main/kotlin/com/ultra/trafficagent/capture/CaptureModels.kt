package com.ultra.trafficagent.capture

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
) {
    val isSecure: Boolean get() = protocol == Protocol.TLS || (path.startsWith("https"))
    val requestSize: Long get() = bytesUp
    val responseSize: Long get() = bytesDown
    val totalSize: Long get() = bytesUp + bytesDown
}

/** Raw IPv4 packet handed to the native engine. */
data class RawPacket(
    val timestampMs: Long,
    val bytes: ByteArray,
    val appUid: Int? = null,
)

/** Capture channel selection (SPEC v2.1: VPN default, root increments). */
enum class CaptureMode { VPN, ROOT_IPTABLES, ROOT_PCAP_FILE }
