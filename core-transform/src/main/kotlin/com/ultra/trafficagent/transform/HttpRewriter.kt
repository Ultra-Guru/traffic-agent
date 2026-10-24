package com.ultra.trafficagent.transform

/** Outcome of running the rewrite pipeline over one exchange. */
data class RewriteResult(
    val appliedRuleIds: List<String>,
    val changedFields: List<String>,
    val delayedByMs: Long,
    /** A rule produced a local answer; the origin must not be contacted. */
    val shortCircuited: Boolean = false,
    /** A rule aborted the exchange entirely (simulated timeout). */
    val dropped: Boolean = false,
) {
    companion object {
        val NONE = RewriteResult(emptyList(), emptyList(), 0)
    }
}

/**
 * Applies active rules from a [RuleRegistry] to exchanges in priority
 * order, recording every mutated field.
 */
class HttpRewriter(private val registry: RuleRegistry) {

    fun applyTo(exchange: MutableExchange): RewriteResult {
        val applied = mutableListOf<String>()
        val changes = mutableListOf<String>()
        var delay = 0L
        var shortCircuit = false
        var dropped = false

        for (rule in registry.activeRules()) {
            if (!rule.match.matches(exchange.request)) continue
            applied += rule.id
            for (action in rule.actions) {
                when (action) {
                    is RuleAction.SetHeader -> {
                        when (action.phase) {
                            Phase.REQUEST -> exchange.request.setHeader(action.name, action.value)
                            Phase.RESPONSE -> exchange.response?.setHeader(action.name, action.value)
                        }
                        changes += "${rule.id}:set-header[${action.phase}/${action.name}]"
                    }
                    is RuleAction.RemoveHeader -> {
                        when (action.phase) {
                            Phase.REQUEST -> exchange.request.removeHeader(action.name)
                            Phase.RESPONSE -> exchange.response?.removeHeader(action.name)
                        }
                        changes += "${rule.id}:remove-header[${action.phase}/${action.name}]"
                    }
                    is RuleAction.ReplacePath -> {
                        val regex = Regex(action.pattern)
                        if (regex.containsMatchIn(exchange.request.path)) {
                            exchange.request.path = regex.replace(
                                exchange.request.path,
                                action.replacement,
                            )
                            changes += "${rule.id}:replace-path"
                        }
                    }
                    is RuleAction.ReplaceBody -> {
                        val regex = Regex(action.pattern)
                        var count = 0
                        val apply: (MatchResult) -> CharSequence = { m ->
                            if (count < action.maxReplacements) {
                                count++
                                m.value.replace(regex, action.replacement)
                            } else {
                                m.value
                            }
                        }
                        when (action.phase) {
                            Phase.REQUEST -> {
                                if (regex.containsMatchIn(exchange.request.body)) {
                                    exchange.request.body = regex.replace(exchange.request.body, action.replacement)
                                    changes += "${rule.id}:replace-body[request]"
                                }
                            }
                            Phase.RESPONSE -> {
                                val resp = exchange.response
                                if (resp != null && regex.containsMatchIn(resp.body)) {
                                    resp.body = regex.replace(resp.body, action.replacement)
                                    changes += "${rule.id}:replace-body[response]"
                                }
                            }
                        }
                    }
                    is RuleAction.Redirect -> {
                        exchange.request.host = action.host
                        exchange.request.path = action.path
                        changes += "${rule.id}:redirect->${action.host}"
                    }
                    is RuleAction.SetStatus -> {
                        exchange.response?.status = action.code
                        changes += "${rule.id}:set-status[${action.code}]"
                    }
                    is RuleAction.DelayMs -> {
                        delay += action.millis
                        changes += "${rule.id}:delay[${action.millis}ms]"
                    }
                    is RuleAction.MockResponse -> {
                        val resp = exchange.response
                            ?: MutableHttpResponse(action.status).also { exchange.response = it }
                        resp.status = action.status
                        resp.body = action.body
                        resp.setHeader("content-type", action.contentType)
                        changes += "${rule.id}:mock[${action.status}]"
                        shortCircuit = true
                    }
                    is RuleAction.Block -> {
                        val resp = exchange.response
                            ?: MutableHttpResponse(action.status).also { exchange.response = it }
                        resp.status = action.status
                        resp.body = action.reason
                        changes += "${rule.id}:block[${action.status}]"
                        shortCircuit = true
                    }
                    is RuleAction.Abort -> {
                        changes += "${rule.id}:abort[${action.timeoutMs}ms]"
                        shortCircuit = true
                        dropped = true
                    }
                }
            }
            if (shortCircuit) break
        }
        return RewriteResult(applied, changes, delay, shortCircuited = shortCircuit, dropped = dropped)
    }
}
