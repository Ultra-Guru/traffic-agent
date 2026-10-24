package com.ultra.trafficagent.mitm

/**
 * One decrypted exchange as observed by the MITM proxy — the capture-unit
 * equivalent of what HttpCanary lists per request.
 */
data class ProxyExchange(
    val id: Long,
    val timestampMs: Long,
    val scheme: String,
    val host: String,
    val port: Int,
    val method: String,
    val path: String,
    val requestHeaders: List<Pair<String, String>>,
    val requestBody: ByteArray?,
    val status: Int?,
    val responseHeaders: List<Pair<String, String>>,
    val responseBody: ByteArray?,
    /** Body after decoding Content-Encoding (gzip/deflate); null when not applicable. */
    val responseDecodedBody: ByteArray?,
    val requestBytes: Long,
    val responseBytes: Long,
    val durationMs: Long,
    val tls: Boolean,
    val appliedRuleIds: List<String> = emptyList(),
    val error: String? = null,
    /** True when a captured body was clipped to the configured capture size limit. */
    val truncated: Boolean = false,
)

/** Receives every finished exchange; listener failures never break the capture pipe. */
fun interface CaptureListener {
    fun onExchange(exchange: ProxyExchange)
}

/** How an interceptor resolved the request half of an exchange. */
sealed class ProxyDecision {
    /** Keep piping the (possibly modified) exchange towards the origin. */
    object Forward : ProxyDecision()

    /** Answer the client directly without contacting the origin. */
    data class ShortCircuit(val status: Int, val body: ByteArray, val contentType: String) : ProxyDecision()
}

/**
 * Header list with case-insensitive lookups that preserves the original
 * names, their order, and repeated headers (multi-value fidelity matters
 * for Set-Cookie style responses).
 */
class MutableHeaders() {

    private val entries = ArrayList<Pair<String, String>>()

    constructor(initial: List<Pair<String, String>>) : this() {
        initial.forEach { add(it.first, it.second) }
    }

    fun add(name: String, value: String) {
        require(name.isNotEmpty()) { "header name must not be empty" }
        entries.add(name to value)
    }

    /** First value registered under [name] (case-insensitive), or null. */
    fun get(name: String): String? = entries.firstOrNull { it.first.equals(name, ignoreCase = true) }?.second

    /** Replaces every occurrence of [name] with one entry, keeping its original position. */
    fun set(name: String, value: String) {
        require(name.isNotEmpty()) { "header name must not be empty" }
        val matches = entries.filter { it.first.equals(name, ignoreCase = true) }
        if (matches.isEmpty()) {
            entries.add(name to value)
            return
        }
        val position = entries.indexOf(matches.first())
        entries.removeAll(matches)
        entries.add(position, name to value)
    }

    fun remove(name: String): Boolean = entries.removeAll { it.first.equals(name, ignoreCase = true) }

    /** Snapshot in original order. */
    fun toList(): List<Pair<String, String>> = entries.toList()

    fun clear() = entries.clear()

    /** Replaces the whole header set with [other] (kept in its order). */
    fun replaceWith(other: MutableHeaders) {
        entries.clear()
        entries.addAll(other.entries)
    }

    fun entries(): List<Pair<String, String>> = entries.toList()

    fun isEmpty(): Boolean = entries.isEmpty()

    /** Lowercased single-value view; later duplicates win, mirroring [com.ultra.trafficagent.transform.MutableHttpRequest]. */
    fun lowercased(): Map<String, String> {
        val map = LinkedHashMap<String, String>()
        for ((name, value) in entries) map[name.lowercase()] = value
        return map
    }
}

/**
 * Rewritable view of one exchange flowing through the proxy: request
 * fields are filled before [ExchangeInterceptor.onRequest], response
 * fields before [ExchangeInterceptor.onResponse].
 */
class MutableProxyExchange(
    var scheme: String,
    var host: String,
    var port: Int,
    var method: String,
    var path: String,
    val requestHeaders: MutableHeaders = MutableHeaders(),
    var requestBody: ByteArray? = null,
    var status: Int? = null,
    val responseHeaders: MutableHeaders = MutableHeaders(),
    var responseBody: ByteArray? = null,
    val appliedRuleIds: MutableList<String> = mutableListOf(),
) {
    /** Convenience for interceptors that want to answer the client directly. */
    fun shortCircuit(status: Int, body: ByteArray, contentType: String): ProxyDecision.ShortCircuit =
        ProxyDecision.ShortCircuit(status, body, contentType)
}

/** Hook points for request/response rewriting inside the proxy pipeline. */
interface ExchangeInterceptor {
    /** May modify the request or decide to answer it without forwarding. */
    fun onRequest(ctx: MutableProxyExchange): ProxyDecision

    /** May modify the response before it is written back to the client. */
    fun onResponse(ctx: MutableProxyExchange)
}
