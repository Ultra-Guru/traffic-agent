package com.ultra.trafficagent.session

import com.ultra.trafficagent.analysis.CaptureRepository
import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.TapEvent
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.concurrent.atomic.AtomicLong

/** Lifecycle of the VPN capture data plane. */
enum class CaptureState {
    IDLE,
    PREPARING,
    ACTIVE,
    STOPPED,
}

/** Aggregated live statistics for the capture banner. */
data class LiveStats(
    val requests: Int,
    val bytesUp: Long,
    val bytesDown: Long,
    val flowsActive: Int,
    val packetsFromTun: Long,
    val packetsToTun: Long,
    val mitmEnabled: Boolean,
    val recordingPcap: Boolean,
    val pcapPath: String? = null,
)

/** Recent protocol events surfaced from the analysis tap. */
data class TapFeed(val events: List<TapEvent>)

/**
 * Process-wide capture session (service <-> UI bridge): the VpnService
 * feeds captured exchanges and stats in, Compose screens observe
 * [requests]/[stats]/[state] as StateFlows. One object per process —
 * the service and the activity share it by construction.
 */
object CaptureSession {

    private val idSeq = AtomicLong(1)

    val repository = CaptureRepository(capacity = 5_000)

    private val requestsFlow = MutableStateFlow<List<CapturedRequest>>(emptyList())
    val requests: StateFlow<List<CapturedRequest>> = requestsFlow

    private val stateFlow = MutableStateFlow(CaptureState.IDLE)
    val state: StateFlow<CaptureState> = stateFlow

    private val statsFlow = MutableStateFlow(
        LiveStats(0, 0, 0, 0, 0, 0, mitmEnabled = false, recordingPcap = false),
    )
    val stats: StateFlow<LiveStats> = statsFlow

    private val eventsFlow = MutableStateFlow(TapFeed(emptyList()))
    val events: StateFlow<TapFeed> = eventsFlow

    /** Last stop reason shown under the capture toggle. */
    val lastStopReason = MutableStateFlow<String?>(null)

    fun nextId(): Long = idSeq.getAndIncrement()

    /** Adds one captured exchange from any capture channel (MITM or tap). */
    fun add(request: CapturedRequest) {
        repository.add(request)
        requestsFlow.value = repository.snapshot()
    }

    fun updateState(state: CaptureState) {
        stateFlow.value = state
    }

    fun updateStats(stats: LiveStats) {
        statsFlow.value = stats
    }

    fun publishEvents(events: List<TapEvent>) {
        if (events.isNotEmpty()) {
            eventsFlow.value = TapFeed(events.takeLast(50))
        }
    }

    fun stopped(reason: String?) {
        lastStopReason.value = reason
        stateFlow.value = CaptureState.STOPPED
    }

    fun clear() {
        repository.clear()
        requestsFlow.value = emptyList()
        eventsFlow.value = TapFeed(emptyList())
    }
}
