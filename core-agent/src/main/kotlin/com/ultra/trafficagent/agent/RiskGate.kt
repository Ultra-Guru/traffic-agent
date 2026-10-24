package com.ultra.trafficagent.agent

/**
 * Kotlin mirror of the Python risk gate. The Python side remains the
 * enforcement point for tool execution; this copy powers the in-app risk
 * badges and pre-flight checks so obviously-disallowed calls never spawn.
 */
enum class RiskLevel(val rank: Int) {
    SAFE(0),
    CAUTION(1),
    DANGEROUS(2),
    CRITICAL(3),
}

object ToolRisk {
    val map: Map<String, RiskLevel> = mapOf(
        // read-only
        "list_requests" to RiskLevel.SAFE,
        "read_request" to RiskLevel.SAFE,
        "filter_requests" to RiskLevel.SAFE,
        "stats_summary" to RiskLevel.SAFE,
        "audit_tail" to RiskLevel.SAFE,
        "pending_breakpoints" to RiskLevel.SAFE,
        // local rewrites
        "modify_header" to RiskLevel.CAUTION,
        "remove_header" to RiskLevel.CAUTION,
        "rewrite_url" to RiskLevel.CAUTION,
        "set_breakpoint" to RiskLevel.CAUTION,
        // behaviour-changing
        "modify_body" to RiskLevel.DANGEROUS,
        "replay_request" to RiskLevel.DANGEROUS,
        "block_host" to RiskLevel.DANGEROUS,
        // device-level
        "install_cert" to RiskLevel.CRITICAL,
        "clear_rules" to RiskLevel.CRITICAL,
    )

    fun of(tool: String): RiskLevel? = map[tool]
}

data class RiskPolicy(
    val maxLevel: RiskLevel = RiskLevel.CAUTION,
    val requireApprovalFrom: RiskLevel = RiskLevel.CRITICAL,
)

data class GateDecision(
    val tool: String,
    val allowed: Boolean,
    val risk: RiskLevel?,
    val reason: String? = null,
    val requiresApproval: Boolean = false,
)

class RiskGate(private val policy: RiskPolicy = RiskPolicy()) {

    fun evaluate(tool: String, approved: Boolean = false): GateDecision {
        val risk = ToolRisk.of(tool)
            ?: return GateDecision(tool, false, null, "unknown tool: $tool")
        if (risk.rank >= policy.requireApprovalFrom.rank && !approved) {
            return GateDecision(
                tool, false, risk,
                "$tool is ${risk.name} and needs approval",
                requiresApproval = true,
            )
        }
        if (risk.rank > policy.maxLevel.rank) {
            return GateDecision(tool, false, risk, "$tool exceeds policy level ${policy.maxLevel.name}")
        }
        return GateDecision(tool, true, risk)
    }
}
