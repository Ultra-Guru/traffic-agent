package com.ultra.trafficagent.transform

/** Operations a sandboxed scriptlet or agent tool may attempt. */
enum class SandboxOperation {
    READ_REQUEST,
    READ_RESPONSE,
    MODIFY_HEADER,
    MODIFY_BODY,
    MODIFY_URL,
    SET_BREAKPOINT,
    EXECUTE_SCRIPT,
    ACCESS_NETWORK,
    ACCESS_DEVICE,
    INSTALL_CERT,
}

/** Verdict of a sandbox policy check. */
data class SandboxDecision(
    val operation: SandboxOperation,
    val allowed: Boolean,
    val reason: String?,
)

/**
 * Declarative capability set for scriptlets and agent-driven mutations
 * (SPEC v2.1 L1.5 script sandbox; enforced again on the Python side).
 */
data class SandboxPolicy(
    val allowedOperations: Set<SandboxOperation>,
    val maxScriptExecutionMs: Long = 1000,
    val maxScriptMemoryMb: Int = 64,
    val networkDenied: Boolean = true,
) {
    companion object {
        /** Safe default: read-only plus header/body rewrites, no network/device. */
        val DEFAULT = SandboxPolicy(
            allowedOperations = setOf(
                SandboxOperation.READ_REQUEST,
                SandboxOperation.READ_RESPONSE,
                SandboxOperation.MODIFY_HEADER,
                SandboxOperation.MODIFY_BODY,
                SandboxOperation.SET_BREAKPOINT,
            ),
        )

        val READ_ONLY = SandboxPolicy(
            allowedOperations = setOf(SandboxOperation.READ_REQUEST, SandboxOperation.READ_RESPONSE),
        )

        val FULL = SandboxPolicy(
            allowedOperations = SandboxOperation.entries.toSet(),
            networkDenied = false,
        )
    }
}

class SandboxEnforcer(private val policy: SandboxPolicy) {

    fun check(operation: SandboxOperation): SandboxDecision {
        if (operation in policy.allowedOperations) {
            return SandboxDecision(operation, true, null)
        }
        return SandboxDecision(operation, false, "operation not allowed by sandbox policy")
    }

    /** True when [elapsedMs] exceeds the configured script timeout. */
    fun timedOut(elapsedMs: Long): Boolean = elapsedMs > policy.maxScriptExecutionMs

    /** True when a memory estimate [mb] exceeds the configured cap. */
    fun overMemory(mb: Int): Boolean = mb > policy.maxScriptMemoryMb

    fun networkBlocked(): Boolean = policy.networkDenied
}
