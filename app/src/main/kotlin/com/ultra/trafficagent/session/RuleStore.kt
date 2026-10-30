package com.ultra.trafficagent.session

import com.ultra.trafficagent.transform.RuleCodec
import com.ultra.trafficagent.transform.RuleRegistry
import com.ultra.trafficagent.transform.RewriteRule
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * Process-wide rule store: the Rules screen edits rule sets, the MITM
 * pipeline applies them to live traffic.
 *
 * Concurrency model: every edit rebuilds an immutable [RuleRegistry]
 * snapshot and publishes it atomically (copy-on-write). Readers either
 * see the old set or the new set — never a half-applied mutation, and
 * never a ConcurrentModificationException against a live rewriter.
 *
 * Persistence: edits are mirrored to `<filesDir>/rules.tarule.json` and
 * reloaded on app start, so rules survive process death (the seed only
 * runs when no persisted pack exists).
 */
object RuleStore {

    private const val RULEPACK_FILE = "rules.tarule.json"

    private val registryFlow = MutableStateFlow<RuleRegistry>(RuleRegistry())
    val registry: StateFlow<RuleRegistry> = registryFlow

    private val rulesFlow = MutableStateFlow<List<RewriteRule>>(emptyList())
    val rules: StateFlow<List<RewriteRule>> = rulesFlow

    private val hitsFlow = MutableStateFlow<Map<String, Long>>(emptyMap())

    /** Live per-rule hit counters, refreshed by the capture pipeline. */
    val hits: StateFlow<Map<String, Long>> = hitsFlow

    /** Pulls the current counters into [hits] (called from the stats loop). */
    fun refreshHits() {
        hitsFlow.value = registryFlow.value.hitCounts()
    }

    /** Directory for [RULEPACK_FILE]; attach from the Application scope. */
    @Volatile
    private var persistenceDir: File? = null

    /** Wires persistence and loads the persisted rulepack (or seeds once). */
    fun attach(dir: File, seedRules: List<RewriteRule> = emptyList()) {
        persistenceDir = dir
        val persisted = loadPersisted(dir)
        if (persisted != null) {
            replaceAll(persisted)
        } else {
            seed(seedRules)
        }
    }

    /** Snapshot the live pipeline should consult right now. */
    fun current(): RuleRegistry = registryFlow.value

    fun seed(rules: List<RewriteRule>) {
        if (rulesFlow.value.isNotEmpty()) return
        publish({ it -> rules.forEach(it::add) }, persist = true)
    }

    fun add(rule: RewriteRule) = publish({ it.add(rule) }, persist = true)

    fun toggle(id: String, enabled: Boolean) =
        publish({ it.setEnabled(id, enabled) }, persist = true)

    fun remove(id: String) = publish({ it.remove(id) }, persist = true)

    /** Replaces the whole set (imported rulepacks use this). */
    fun replaceAll(rules: List<RewriteRule>) =
        publish({ next -> rules.forEach(next::add) }, persist = true)

    /** Current set rendered as a portable rulepack document. */
    fun exportRulepack(): String = RuleCodec.encodeRulepack(rulesFlow.value)

    /** Parses and installs a rulepack, returning a soft error message. */
    fun importRulepack(text: String): String? {
        val rules = try {
            RuleCodec.decodeRulepack(text)
        } catch (e: RuleCodec.RuleFormatException) {
            return e.message
        }
        if (rules.isEmpty()) return "Rulepack contains no usable rules"
        replaceAll(rules)
        return null
    }

    private fun loadPersisted(dir: File): List<RewriteRule>? {
        val file = File(dir, RULEPACK_FILE)
        if (!file.isFile) return null
        return try {
            RuleCodec.decodeRulepack(file.readText())
        } catch (_: Exception) {
            null  // corrupt pack: fall back to the seed
        }
    }

    private fun persist(rules: List<RewriteRule>) {
        val dir = persistenceDir ?: return
        try {
            dir.mkdirs()
            File(dir, RULEPACK_FILE).writeText(RuleCodec.encodeRulepack(rules))
        } catch (_: Exception) {
            // Persistence is best-effort; live traffic still sees the change.
        }
    }

    private fun publish(mutate: (RuleRegistry) -> Unit, persist: Boolean = false) {
        val next = RuleRegistry()
        registryFlow.value.allRules().forEach(next::add)
        // Hit counters survive the copy-on-write swap.
        registryFlow.value.hitCounts().forEach { (id, count) ->
            repeat(count.toInt()) { next.recordHit(id) }
        }
        mutate(next)
        registryFlow.value = next
        rulesFlow.value = next.allRules()
        if (persist) persist(next.allRules())
    }
}
