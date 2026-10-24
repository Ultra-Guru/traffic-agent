package com.ultra.trafficagent.transform

enum class BreakpointPhase { REQUEST, RESPONSE }

enum class BreakpointState { PENDING, APPROVED, REJECTED, EXPIRED, RELEASED }

data class Breakpoint(
    val id: Long,
    val flowKey: String,
    val phase: BreakpointPhase,
    val createdAtMs: Long,
    val state: BreakpointState = BreakpointState.PENDING,
)

/**
 * Mobile-native breakpoint engine (SPEC v2.1 L1.5): a matched exchange is
 * parked in PENDING until the user (or the agent, through the risk gate)
 * approves or rejects it, or the hold times out.
 */
class BreakpointManager(private val now: () -> Long = { System.currentTimeMillis() }) {

    private val breakpoints = LinkedHashMap<Long, Breakpoint>()
    private var nextId = 1L

    /** Parks a new breakpoint for [flowKey] and returns it in PENDING state. */
    fun hit(flowKey: String, phase: BreakpointPhase): Breakpoint {
        val bp = Breakpoint(nextId++, flowKey, phase, now())
        breakpoints[bp.id] = bp
        return bp
    }

    fun byId(id: Long): Breakpoint? = breakpoints[id]

    fun pending(): List<Breakpoint> = breakpoints.values.filter { it.state == BreakpointState.PENDING }

    fun all(): List<Breakpoint> = breakpoints.values.toList()

    /** PENDING -> APPROVED. Returns false for any other source state. */
    fun approve(id: Long): Boolean = transition(id) { it == BreakpointState.PENDING } &&
        updateState(id, BreakpointState.APPROVED)

    /** PENDING -> REJECTED. Returns false for any other source state. */
    fun reject(id: Long): Boolean = transition(id) { it == BreakpointState.PENDING } &&
        updateState(id, BreakpointState.REJECTED)

    /** APPROVED -> RELEASED (the exchange continues). */
    fun release(id: Long): Boolean = transition(id) { it == BreakpointState.APPROVED } &&
        updateState(id, BreakpointState.RELEASED)

    /**
     * Expires PENDING breakpoints older than [maxAgeMs]; returns the freshly
     * expired ones.
     */
    fun expireDue(maxAgeMs: Long): List<Breakpoint> {
        val threshold = now() - maxAgeMs
        val expired = mutableListOf<Breakpoint>()
        for ((id, bp) in breakpoints) {
            if (bp.state == BreakpointState.PENDING && bp.createdAtMs <= threshold) {
                breakpoints[id] = bp.copy(state = BreakpointState.EXPIRED)
                expired += bp.copy(state = BreakpointState.EXPIRED)
            }
        }
        return expired
    }

    fun clear() = breakpoints.clear()

    private inline fun transition(id: Long, allowed: (BreakpointState) -> Boolean): Boolean {
        val bp = breakpoints[id] ?: return false
        return allowed(bp.state)
    }

    private fun updateState(id: Long, state: BreakpointState): Boolean {
        val bp = breakpoints[id] ?: return false
        breakpoints[id] = bp.copy(state = state)
        return true
    }
}
