package com.ultra.trafficagent.session

import com.ultra.trafficagent.transform.RuleRegistry
import com.ultra.trafficagent.transform.RewriteRule
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Process-wide rule store: the Rules screen edits rule sets, the MITM
 * pipeline applies them to live traffic.
 *
 * Concurrency model: every edit rebuilds an immutable [RuleRegistry]
 * snapshot and publishes it atomically (copy-on-write). Readers either
 * see the old set or the new set — never a half-applied mutation, and
 * never a ConcurrentModificationException against a live rewriter.
 */
object RuleStore {

    private val registryFlow = MutableStateFlow<RuleRegistry>(RuleRegistry())
    val registry: StateFlow<RuleRegistry> = registryFlow

    private val rulesFlow = MutableStateFlow<List<RewriteRule>>(emptyList())
    val rules: StateFlow<List<RewriteRule>> = rulesFlow

    /** Snapshot the live pipeline should consult right now. */
    fun current(): RuleRegistry = registryFlow.value

    fun seed(rules: List<RewriteRule>) {
        if (rulesFlow.value.isNotEmpty()) return
        publish { it -> rules.forEach(it::add) }
    }

    fun add(rule: RewriteRule) = publish { it.add(rule) }

    fun toggle(id: String, enabled: Boolean) = publish { it.setEnabled(id, enabled) }

    fun remove(id: String) = publish { it.remove(id) }

    private fun publish(mutate: (RuleRegistry) -> Unit) {
        val next = RuleRegistry()
        registryFlow.value.allRules().forEach(next::add)
        mutate(next)
        registryFlow.value = next
        rulesFlow.value = next.allRules()
    }
}
