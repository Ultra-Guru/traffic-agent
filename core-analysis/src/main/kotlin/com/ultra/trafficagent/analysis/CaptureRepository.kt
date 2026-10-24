package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest

/**
 * In-memory ring buffer of captured exchanges (SPEC v2.1 L3): fixed
 * capacity, O(1) eviction of the oldest, filtered snapshots and an
 * incremental [TrafficStats] view.
 */
class CaptureRepository(private val capacity: Int = 5_000) {
    init {
        require(capacity > 0) { "capacity must be positive" }
    }

    private val items = ArrayDeque<CapturedRequest>(capacity.coerceAtMost(1024))
    private val byId = HashMap<Long, CapturedRequest>()
    private val stats = TrafficStats()

    /** Optional observer invoked after every [add]; failures are swallowed. */
    @Volatile
    var onAdded: ((CapturedRequest) -> Unit)? = null

    val size: Int get() = synchronized(this) { items.size }

    fun add(c: CapturedRequest) {
        val evicted: CapturedRequest?
        val fire: ((CapturedRequest) -> Unit)?
        synchronized(this) {
            evicted = if (items.size >= capacity) items.removeFirst() else null
            if (evicted != null) byId.remove(evicted!!.id)
            items.addLast(c)
            byId[c.id] = c
            stats.record(c)
            fire = onAdded
        }
        fire?.let {
            try {
                it(c)
            } catch (_: RuntimeException) {
            }
        }
    }

    fun get(id: Long): CapturedRequest? = synchronized(this) { byId[id] }

    /** Newest-first snapshot. */
    fun snapshot(): List<CapturedRequest> = synchronized(this) { items.toList().asReversed() }

    fun apply(filter: CaptureFilter): List<CapturedRequest> = filter.filter(snapshot())

    fun clear() = synchronized(this) {
        items.clear()
        byId.clear()
        stats.reset()
    }

    /** Aggregated totals over everything currently buffered. */
    fun stats(): TrafficStats.Summary = synchronized(this) {
        TrafficStats.Summary(
            requests = stats.totalRequests(),
            bytesUp = stats.totalBytesUp(),
            bytesDown = stats.totalBytesDown(),
        )
    }

    /** Top hosts by traffic (see [TrafficStats.topHosts]). */
    fun topHosts(n: Int): List<HostStat> = synchronized(this) { stats.topHosts(n) }
}
