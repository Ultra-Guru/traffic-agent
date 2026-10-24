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
}

class MutableExchange(
    val request: MutableHttpRequest,
    val response: MutableHttpResponse? = null,
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

    /** Whether two matches can overlap on the same request set (conflict check). */
    fun overlaps(other: RuleMatch): Boolean {
        val bothHaveHost = hostRegex != null && other.hostRegex != null
        if (bothHaveHost && !Regex(hostRegex!!).toString().let { hostRegex == other.hostRegex }) {
            // conservative: identical regexes definitely overlap; different
            // regexes may still overlap, so treat any pair as potential overlap
            return true
        }
        return true
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

    fun add(rule: RewriteRule) {
        require(rule.id.isNotEmpty()) { "rule id must not be empty" }
        rules[rule.id] = rule
    }

    fun remove(id: String): Boolean = rules.remove(id) != null

    fun setEnabled(id: String, enabled: Boolean): Boolean {
        val rule = rules[id] ?: return false
        rules[id] = rule.copy(enabled = enabled)
        return true
    }

    fun rule(id: String): RewriteRule? = rules[id]

    fun allRules(): List<RewriteRule> = rules.values.toList()

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
