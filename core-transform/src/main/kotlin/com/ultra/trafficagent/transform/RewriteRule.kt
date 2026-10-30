package com.ultra.trafficagent.transform

/** Which half of the exchange an action applies to. */
enum class Phase { REQUEST, RESPONSE }

/** Rewritable snapshot of an exchange flowing through the transform layer. */
class MutableHttpRequest(
    var method: String,
    var host: String,
    var path: String,
    headers: Map<String, String> = emptyMap(),
    var body: String = "",
    /** Override port for MapRemote; null = scheme default. */
    var port: Int? = null,
) {
    private val headerMap = LinkedHashMap<String, String>()

    init {
        headers.forEach { (k, v) -> headerMap[k.lowercase()] = v }
    }

    fun header(name: String): String? = headerMap[name.lowercase()]

    fun setHeader(name: String, value: String) {
        headerMap[name.lowercase()] = value
    }

    fun removeHeader(name: String) {
        headerMap.remove(name.lowercase())
    }

    fun headers(): Map<String, String> = LinkedHashMap(headerMap)
}

class MutableHttpResponse(
    var status: Int,
    headers: Map<String, String> = emptyMap(),
    var body: String = "",
) {
    private val headerMap = LinkedHashMap<String, String>()

    init {
        headers.forEach { (k, v) -> headerMap[k.lowercase()] = v }
    }

    fun header(name: String): String? = headerMap[name.lowercase()]

    fun setHeader(name: String, value: String) {
        headerMap[name.lowercase()] = value
    }

    fun removeHeader(name: String) {
        headerMap.remove(name.lowercase())
    }

    /** Lowercased single-value snapshot of the current headers. */
    fun headers(): Map<String, String> = LinkedHashMap(headerMap)
}

class MutableExchange(
    val request: MutableHttpRequest,
    var response: MutableHttpResponse? = null,
) {
    val url: String get() = "https://${request.host}${request.path}"
}

/** A single transformation applied to a matched exchange. */
sealed class RuleAction {
    data class SetHeader(val phase: Phase, val name: String, val value: String) : RuleAction()
    data class RemoveHeader(val phase: Phase, val name: String) : RuleAction()
    data class ReplacePath(val pattern: String, val replacement: String) : RuleAction()
    data class ReplaceBody(val phase: Phase, val pattern: String, val replacement: String, val maxReplacements: Int = 10) : RuleAction()
    data class Redirect(val host: String, val path: String) : RuleAction()
    data class SetStatus(val code: Int) : RuleAction()
    data class DelayMs(val millis: Long) : RuleAction()

    /** Serves a canned answer without contacting the origin (HttpCanary "请求模拟"). */
    data class MockResponse(
        val status: Int = 200,
        val body: String = "",
        val contentType: String = "application/json",
    ) : RuleAction()

    /** Rejects the request outright. */
    data class Block(val status: Int = 403, val reason: String = "Blocked by Traffic Agent") : RuleAction()

    /** Pretends the origin never answers within [timeoutMs] (simulated hangup). */
    data class Abort(val timeoutMs: Long) : RuleAction()

    /** Sets or replaces one query parameter on the request path. */
    data class ReplaceQueryParam(val name: String, val value: String) : RuleAction()

    /** HttpCanary-style Map Remote: serve the request from another host. */
    data class MapRemote(
        val targetHost: String,
        val targetPort: Int? = null,
        val keepHostHeader: Boolean = false,
    ) : RuleAction()
}

/** Matching criteria deciding which exchanges a rule applies to. */
data class RuleMatch(
    val hostRegex: String? = null,
    val pathRegex: String? = null,
    val methods: Set<String> = emptySet(),
    val headerEquals: Map<String, String> = emptyMap(),
) {
    fun matches(request: MutableHttpRequest): Boolean {
        if (hostRegex != null && !Regex(hostRegex).containsMatchIn(request.host)) return false
        if (pathRegex != null && !Regex(pathRegex).containsMatchIn(request.path)) return false
        if (methods.isNotEmpty() && request.method !in methods) return false
        for ((name, value) in headerEquals) {
            if (request.header(name) != value) return false
        }
        return true
    }

    /** Whether two matches can overlap on the same request set (conflict check).
     *
     * Sound-but-incomplete: a definite *disjointness* on any single axis
     * (methods, header equality, literal host/path regexes) proves the two
     * matches never select the same request; anything else is conservatively
     * reported as overlapping so the UI never hides a real conflict.
     */
    fun overlaps(other: RuleMatch): Boolean {
        // Disjoint method sets can never match the same request.
        if (methods.isNotEmpty() && other.methods.isNotEmpty() &&
            methods.intersect(other.methods).isEmpty()
        ) {
            return false
        }
        // Same header constrained to different values -> disjoint
        // (header names compare case-insensitively, as everywhere else).
        val otherHeaders = other.headerEquals.mapKeys { (k, _) -> k.lowercase() }
        for ((name, value) in headerEquals) {
            val otherValue = otherHeaders[name.lowercase()] ?: continue
            if (!value.equals(otherValue, ignoreCase = true)) return false
        }
        if (hostRegex != null && other.hostRegex != null &&
            literalRegexesDisjoint(hostRegex, other.hostRegex)
        ) {
            return false
        }
        if (pathRegex != null && other.pathRegex != null &&
            literalRegexesDisjoint(pathRegex, other.pathRegex)
        ) {
            return false
        }
        return true
    }

    private companion object {
        /** Metacharacters that make a regex non-literal for the overlap check. */
        private const val REGEX_META = ".[]{}()*+?^$|"

        /** True when [s] can only match its own literal text: every
         *  metacharacter is escaped (the usual `api\.example\.com` form). */
        fun isLiteralRegex(s: String): Boolean {
            var i = 0
            while (i < s.length) {
                if (s[i] == '\\') {
                    i += 2  // escaped character: literal by definition
                    continue
                }
                if (s[i] in REGEX_META) return false
                i++
            }
            return true
        }

        /** The literal text [s] matches when it is a literal regex. */
        fun literalOf(s: String): String {
            val sb = StringBuilder()
            var i = 0
            while (i < s.length) {
                if (s[i] == '\\' && i + 1 < s.length) {
                    sb.append(s[i + 1])
                    i += 2
                } else {
                    sb.append(s[i])
                    i += 1
                }
            }
            return sb.toString()
        }

        /** Two literal regexes share a subject iff one's literal contains
         *  the other's. Non-literals are never claimed disjoint. */
        fun literalRegexesDisjoint(a: String, b: String): Boolean {
            if (!isLiteralRegex(a) || !isLiteralRegex(b)) return false
            val la = literalOf(a)
            val lb = literalOf(b)
            return !la.contains(lb) && !lb.contains(la)
        }
    }
}

data class RewriteRule(
    val id: String,
    val name: String,
    val enabled: Boolean = true,
    val priority: Int = 0,
    val match: RuleMatch = RuleMatch(),
    val actions: List<RuleAction> = emptyList(),
)

/**
 * Ordered registry of rewrite rules with enable/disable and conflict
 * detection (SPEC v2.1 L1.5).
 */
class RuleRegistry {

    private val rules = LinkedHashMap<String, RewriteRule>()
    private val hits = java.util.concurrent.ConcurrentHashMap<String, Long>()

    fun add(rule: RewriteRule) {
        require(rule.id.isNotEmpty()) { "rule id must not be empty" }
        rules[rule.id] = rule
    }

    fun remove(id: String): Boolean {
        hits.remove(id)
        return rules.remove(id) != null
    }

    fun setEnabled(id: String, enabled: Boolean): Boolean {
        val rule = rules[id] ?: return false
        rules[id] = rule.copy(enabled = enabled)
        return true
    }

    fun rule(id: String): RewriteRule? = rules[id]

    fun allRules(): List<RewriteRule> = rules.values.toList()

    /** Times a rule's actions were applied to live traffic. */
    fun hitCount(id: String): Long = hits[id] ?: 0L

    /** Per-rule hit snapshot for UI rendering. */
    fun hitCounts(): Map<String, Long> = hits.toMap()

    /** Records one application of [id] (called by [HttpRewriter]). */
    fun recordHit(id: String) {
        hits.merge(id, 1L) { a, b -> a + b }
    }

    fun resetHits() = hits.clear()

    /** Enabled rules ordered by descending priority (stable for equal keys). */
    fun activeRules(): List<RewriteRule> =
        rules.values.filter { it.enabled }.sortedByDescending { it.priority }

    /**
     * Rules that share a priority band and can overlap with [candidate]'s
     * match — candidates for ambiguity warnings in the rules UI.
     */
    fun findConflicts(candidate: RewriteRule): List<RewriteRule> =
        rules.values.filter {
            it.id != candidate.id && it.enabled == candidate.enabled &&
                kotlin.math.abs(it.priority - candidate.priority) <= 1 &&
                it.match.overlaps(candidate.match)
        }

    fun clear() = rules.clear()
}
