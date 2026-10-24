package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import com.ultra.trafficagent.capture.headerValue

/**
 * HttpCanary-style capture filter: one object covering keyword search,
 * method/status/mime/protocol sets and numeric ranges, plus a compact
 * query DSL (`host:weibo status:4xx size>1024`).
 */
data class CaptureFilter(
    val hostKeyword: String? = null,
    val pathKeyword: String? = null,
    val bodyKeyword: String? = null,
    val methods: Set<String> = emptySet(),
    val statusClasses: Set<Int> = emptySet(),
    val exactStatus: Set<Int> = emptySet(),
    val mimePrefixes: List<String> = emptyList(),
    val minBytes: Long? = null,
    val maxBytes: Long? = null,
    val minDurationMs: Long? = null,
    val maxDurationMs: Long? = null,
    val protocols: Set<Protocol> = emptySet(),
    val secureOnly: Boolean = false,
    val insecureOnly: Boolean = false,
    val appUids: Set<Int> = emptySet(),
    val errorOnly: Boolean = false,
) {
    companion object {
        /**
         * Parses a filter query. Supported tokens:
         * `host:x` `path:x` `body:x` `method:GET,POST` `status:4xx` `status:404`
         * `mime:image/` `size>1024` `size<4096` `time>500` `time<2000`
         * `proto:http2,tls` `secure:true|false` `uid:10085` `error:true`
         * — bare words become a host keyword. Malformed tokens throw
         * [IllegalArgumentException] quoting the token.
         */
        fun parse(query: String): CaptureFilter {
            val f = Builder()
            for (raw in query.trim().split(Regex("\\s+")).filter { it.isNotEmpty() }) {
                val token = raw.lowercase()
                try {
                    when {
                        token.startsWith("host:") -> f.hostKeyword = raw.substring(5)
                        token.startsWith("path:") -> f.pathKeyword = raw.substring(5)
                        token.startsWith("body:") -> f.bodyKeyword = raw.substring(5)
                        token.startsWith("method:") -> f.methods += raw.substring(7).uppercase().split(',')
                        token.startsWith("status:") -> raw.substring(7).split(',').forEach { part ->
                            val p = part.trim()
                            if (p.endsWith("xx", true)) {
                                p.dropLast(2).toIntOrNull()?.let { f.statusClasses += it }
                            } else {
                                p.toIntOrNull()?.let { f.exactStatus += it }
                                    ?: throw IllegalArgumentException("bad status token: $raw")
                            }
                        }
                        token.startsWith("mime:") -> f.mimePrefixes += raw.substring(5).lowercase()
                        token.startsWith("size>") -> f.minBytes = number(raw.substring(5), raw)
                        token.startsWith("size<") -> f.maxBytes = number(raw.substring(5), raw)
                        token.startsWith("time>") -> f.minDurationMs = number(raw.substring(5), raw)
                        token.startsWith("time<") -> f.maxDurationMs = number(raw.substring(5), raw)
                        token.startsWith("proto:") -> raw.substring(6).split(',').forEach { part ->
                            val name = part.trim().uppercase()
                            Protocol.values().firstOrNull { it.name == name }
                                ?.let { f.protocols += it }
                                ?: throw IllegalArgumentException("unknown protocol: $raw")
                        }
                        token.startsWith("secure:") -> when (raw.substring(7).lowercase()) {
                            "true", "yes", "1" -> f.secureOnly = true
                            "false", "no", "0" -> f.insecureOnly = true
                            else -> throw IllegalArgumentException("bad secure token: $raw")
                        }
                        token.startsWith("uid:") -> f.appUids += number(raw.substring(4), raw).toInt()
                        token.startsWith("error:") -> when (raw.substring(6).lowercase()) {
                            "true", "yes", "1" -> f.errorOnly = true
                            "false", "no", "0" -> f.errorOnly = false
                            else -> throw IllegalArgumentException("bad error token: $raw")
                        }
                        else -> f.hostKeyword = raw
                    }
                } catch (e: IllegalArgumentException) {
                    throw e
                }
            }
            return f.build()
        }

        private fun number(text: String, raw: String): Long =
            text.toLongOrNull() ?: throw IllegalArgumentException("bad numeric token: $raw")

        private class Builder {
            var hostKeyword: String? = null
            var pathKeyword: String? = null
            var bodyKeyword: String? = null
            var methods = linkedSetOf<String>()
            var statusClasses = linkedSetOf<Int>()
            var exactStatus = linkedSetOf<Int>()
            var mimePrefixes = mutableListOf<String>()
            var minBytes: Long? = null
            var maxBytes: Long? = null
            var minDurationMs: Long? = null
            var maxDurationMs: Long? = null
            var protocols = linkedSetOf<Protocol>()
            var secureOnly = false
            var insecureOnly = false
            var appUids = linkedSetOf<Int>()
            var errorOnly = false

            fun build() = CaptureFilter(
                hostKeyword, pathKeyword, bodyKeyword, methods, statusClasses, exactStatus,
                mimePrefixes, minBytes, maxBytes, minDurationMs, maxDurationMs, protocols,
                secureOnly, insecureOnly, appUids, errorOnly,
            )
        }
    }

    /** True when [c] passes every configured criterion. */
    fun matches(c: CapturedRequest): Boolean {
        if (hostKeyword != null && !c.host.contains(hostKeyword!!, ignoreCase = true)) return false
        if (pathKeyword != null && !c.path.contains(pathKeyword!!, ignoreCase = true)) return false
        if (bodyKeyword != null &&
            !c.requestBody.contains(bodyKeyword!!, ignoreCase = true) &&
            !c.responseBody.contains(bodyKeyword!!, ignoreCase = true)
        ) {
            return false
        }
        if (methods.isNotEmpty() && c.method.uppercase() !in methods) return false
        val status = c.status
        if (statusClasses.isNotEmpty() && (status == null || status / 100 !in statusClasses)) return false
        if (exactStatus.isNotEmpty() && status !in exactStatus) return false
        if (mimePrefixes.isNotEmpty()) {
            val mime = (c.responseMime ?: contentTypeOf(c))?.lowercase() ?: return false
            if (mimePrefixes.none { mime.startsWith(it) }) return false
        }
        if (minBytes != null && c.totalSize < minBytes!!) return false
        if (maxBytes != null && c.totalSize > maxBytes!!) return false
        val duration = c.durationMs ?: 0L
        if (minDurationMs != null && duration < minDurationMs!!) return false
        if (maxDurationMs != null && duration > maxDurationMs!!) return false
        if (protocols.isNotEmpty() && c.protocol !in protocols) return false
        if (secureOnly && !c.isSecure) return false
        if (insecureOnly && c.isSecure) return false
        if (appUids.isNotEmpty() && c.appUid !in appUids) return false
        if (errorOnly && c.error == null && (status ?: 200) < 500) return false
        return true
    }

    /** [c] filtered down to what matches. */
    fun filter(requests: List<CapturedRequest>): List<CapturedRequest> = requests.filter { matches(it) }

    private fun contentTypeOf(c: CapturedRequest): String? =
        c.contentType ?: headerValue(c.responseHeaders, "content-type")
            ?.substringBefore(';')?.trim()
}
