package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol

/** Action a matched rule asks the capture pipeline to take. */
enum class RuleAction {
    /** Explicitly allow (overrides lower-priority blocks). */
    ALLOW,

    /** Drop the flow / return RST to the app. */
    BLOCK,

    /** Shape the flow to the configured KiB/s rate. */
    THROTTLE,

    /** Serve a canned response instead of reaching the network. */
    MOCK,

    /** Attach a tag used by the UI for grouping and coloring. */
    TAG,

    /** Apply secret redaction to bodies before display/export. */
    REDACT,
}

/** Fields addressable from rule conditions. */
enum class RuleField(val displayName: String) {
    HOST("host"),
    PATH("path"),
    METHOD("method"),
    STATUS("status"),
    BYTES_UP("bytes_up"),
    BYTES_DOWN("bytes_down"),
    TOTAL("total"),
    DURATION("duration"),
    PROTOCOL("protocol"),
    MIME("mime"),
    UID("uid"),
    JA3("ja3"),
    ERROR("error"),
    CATEGORY("category"),
    ;

    companion object {
        fun fromToken(token: String): RuleField? =
            entries.firstOrNull { it.displayName == token.lowercase() }
    }
}

/** Comparison operators available in the DSL. */
enum class RuleOp(val symbol: String) {
    EQ("="),
    NEQ("!="),
    GT(">"),
    LT("<"),
    GTE(">="),
    LTE("<="),
    CONTAINS("contains"),
    STARTS_WITH("starts_with"),
    ENDS_WITH("ends_with"),
    MATCHES("matches"),
    IN("in"),
    ;

    companion object {
        fun fromToken(token: String): RuleOp? =
            entries.firstOrNull { it.symbol == token.lowercase() }
    }
}

/** A parsed rule. */
data class Rule(
    val name: String,
    val priority: Int = 0,
    val enabled: Boolean = true,
    val action: RuleAction,
    val condition: RuleCondition,
    val throttleRateKibPerS: Int? = null,
    val mockStatus: Int? = null,
    val mockBody: String? = null,
    val tagName: String? = null,
) {
    init {
        require(name.isNotBlank()) { "rule name must not be blank" }
        if (action == RuleAction.THROTTLE) {
            require(throttleRateKibPerS != null && throttleRateKibPerS > 0) {
                "throttle rule '$name' needs rate=N (KiB/s) > 0"
            }
        }
        if (action == RuleAction.MOCK) {
            require(mockStatus != null && mockStatus in 100..599) {
                "mock rule '$name' needs status=100..599"
            }
        }
        if (action == RuleAction.TAG) {
            require(!tagName.isNullOrBlank()) { "tag rule '$name' needs name=..." }
        }
    }
}

/** Condition tree. */
sealed class RuleCondition {
    /** Always true (empty `when` clause). */
    object Always : RuleCondition()

    data class Field(val field: RuleField, val op: RuleOp, val value: ConditionValue) : RuleCondition()

    data class And(val left: RuleCondition, val right: RuleCondition) : RuleCondition()

    data class Or(val left: RuleCondition, val right: RuleCondition) : RuleCondition()

    data class Not(val inner: RuleCondition) : RuleCondition()
}

/** A literal value in a condition. */
sealed class ConditionValue {
    data class Str(val text: String) : ConditionValue()

    data class Num(val number: Long) : ConditionValue()

    data class ListOf(val items: List<ConditionValue>) : ConditionValue()
}

/** The outcome of evaluating a rule set against one request. */
data class RuleDecision(
    val action: RuleAction,
    val matchedRule: Rule?,
    val throttleRateKibPerS: Int? = null,
    val mockStatus: Int? = null,
    val mockBody: String? = null,
    val tags: List<String> = emptyList(),
    val redact: Boolean = false,
) {
    companion object {
        val ALLOW_ALL = RuleDecision(RuleAction.ALLOW, null)
    }
}

/**
 * Ordered rule set. Evaluation: rules sorted by descending priority; the
 * first match decides. BLOCK / MOCK / THROTTLE are terminal; TAG / REDACT
 * accumulate and evaluation continues so several tags can fire at once.
 */
class RuleSet(val rules: List<Rule>) {

    private val evaluationOrder: List<Rule> = rules
        .filter { it.enabled }
        .sortedWith(compareByDescending<Rule> { it.priority }.thenBy { it.name })

    /** Evaluates the decision for [request]. */
    fun evaluate(request: CapturedRequest): RuleDecision {
        val tags = mutableListOf<String>()
        var redact = false
        var lastThrottle: Rule? = null
        for (rule in evaluationOrder) {
            if (!rule.condition.matches(request)) continue
            when (rule.action) {
                RuleAction.BLOCK, RuleAction.MOCK, RuleAction.ALLOW -> {
                    return RuleDecision(
                        action = rule.action,
                        matchedRule = rule,
                        throttleRateKibPerS = rule.throttleRateKibPerS,
                        mockStatus = rule.mockStatus,
                        mockBody = rule.mockBody,
                        tags = tags.toList(),
                        redact = redact,
                    )
                }
                RuleAction.THROTTLE -> lastThrottle = rule
                RuleAction.TAG -> rule.tagName?.let { tags.add(it) }
                RuleAction.REDACT -> redact = true
            }
        }
        if (lastThrottle != null) {
            return RuleDecision(
                action = RuleAction.THROTTLE,
                matchedRule = lastThrottle,
                throttleRateKibPerS = lastThrottle.throttleRateKibPerS,
                tags = tags.toList(),
                redact = redact,
            )
        }
        if (tags.isNotEmpty() || redact) {
            return RuleDecision(RuleAction.ALLOW, null, tags = tags.toList(), redact = redact)
        }
        return RuleDecision.ALLOW_ALL
    }

    companion object {
        val EMPTY = RuleSet(emptyList())
    }
}

/** Matching entry points used by both the engine and unit tests. */
fun RuleCondition.matches(request: CapturedRequest): Boolean = when (this) {
    is RuleCondition.Always -> true
    is RuleCondition.Field -> evaluateField(request)
    is RuleCondition.And -> left.matches(request) && right.matches(request)
    is RuleCondition.Or -> left.matches(request) || right.matches(request)
    is RuleCondition.Not -> !inner.matches(request)
}

private fun RuleCondition.Field.evaluateField(request: CapturedRequest): Boolean {
    val actual: Any? = when (field) {
        RuleField.HOST -> request.host.lowercase()
        RuleField.PATH -> request.path
        RuleField.METHOD -> request.method.uppercase()
        RuleField.STATUS -> request.status?.toLong()
        RuleField.BYTES_UP -> request.bytesUp
        RuleField.BYTES_DOWN -> request.bytesDown
        RuleField.TOTAL -> request.totalSize
        RuleField.DURATION -> request.durationMs ?: 0L
        RuleField.PROTOCOL -> request.protocol.name.lowercase()
        RuleField.MIME -> (request.responseMime ?: request.contentType)?.lowercase()
        RuleField.UID -> request.appUid?.toLong()
        RuleField.JA3 -> request.ja3?.lowercase()
        RuleField.ERROR -> request.error?.lowercase()
        RuleField.CATEGORY -> DomainClassifier.classify(request.host).category.name.lowercase()
    }
    if (actual == null) {
        // Missing field: only "!=" and "not in" can be true.
        return op == RuleOp.NEQ
    }
    return when (op) {
        RuleOp.EQ -> compareEquals(actual, value)
        RuleOp.NEQ -> !compareEquals(actual, value)
        RuleOp.GT -> compareOrder(actual, value) > 0
        RuleOp.LT -> compareOrder(actual, value) < 0
        RuleOp.GTE -> compareOrder(actual, value) >= 0
        RuleOp.LTE -> compareOrder(actual, value) <= 0
        RuleOp.CONTAINS -> actual.toString().contains(value.asText(), ignoreCase = true)
        RuleOp.STARTS_WITH -> actual.toString().startsWith(value.asText(), ignoreCase = true)
        RuleOp.ENDS_WITH -> actual.toString().endsWith(value.asText(), ignoreCase = true)
        RuleOp.MATCHES -> Regex(value.asText()).containsMatchIn(actual.toString())
        RuleOp.IN -> when (value) {
            is ConditionValue.ListOf -> value.items.any { compareEquals(actual, it) }
            else -> compareEquals(actual, value)
        }
    }
}

private fun compareEquals(actual: Any?, value: ConditionValue): Boolean = when (value) {
    is ConditionValue.Str -> actual.toString().equals(value.text, ignoreCase = true)
    is ConditionValue.Num -> (actual as? Number)?.toLong() == value.number
    is ConditionValue.ListOf -> value.items.any { compareEquals(actual, it) }
}

private fun compareOrder(actual: Any?, value: ConditionValue): Int {
    val rhs: Comparable<*> = when (value) {
        is ConditionValue.Str -> value.text
        is ConditionValue.Num -> value.number
        is ConditionValue.ListOf -> return 0
    }
    @Suppress("UNCHECKED_CAST")
    return when {
        actual is Number && rhs is Number ->
            (actual.toLong()).compareTo((rhs as Number).toLong())
        actual is String && rhs is String ->
            (actual as String).compareTo(rhs as String, ignoreCase = true)
        else -> actual.toString().compareTo(rhs.toString())
    }
}

private fun ConditionValue.asText(): String = when (this) {
    is ConditionValue.Str -> text
    is ConditionValue.Num -> number.toString()
    is ConditionValue.ListOf -> items.joinToString(",")
}

/** Helper for tests and callers building rules programmatically. */
fun fieldCond(field: RuleField, op: RuleOp, value: String): RuleCondition.Field =
    RuleCondition.Field(field, op, ConditionValue.Str(value))

fun fieldCond(field: RuleField, op: RuleOp, value: Long): RuleCondition.Field =
    RuleCondition.Field(field, op, ConditionValue.Num(value))

fun fieldCond(field: RuleField, op: RuleOp, vararg values: Long): RuleCondition.Field =
    RuleCondition.Field(field, op, ConditionValue.ListOf(values.map { ConditionValue.Num(it) }))

fun fieldCond(field: RuleField, op: RuleOp, vararg values: String): RuleCondition.Field =
    RuleCondition.Field(field, op, ConditionValue.ListOf(values.map { ConditionValue.Str(it) }))
