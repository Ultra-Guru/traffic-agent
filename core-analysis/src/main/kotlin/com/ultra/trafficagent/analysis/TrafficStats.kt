package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol

/** Aggregated traffic for a single host. */
data class HostStat(
    val host: String,
    val requests: Int,
    val bytesUp: Long,
    val bytesDown: Long,
) {
    val totalBytes: Long get() = bytesUp + bytesDown
}

/**
 * Streaming traffic statistics over captured exchanges: per-host aggregates,
 * protocol mix, per-app shares and windowed bandwidth (SPEC v2.1 L3).
 */
class TrafficStats {

    private val hosts = LinkedHashMap<String, HostStat>()
    private val protocols = LinkedHashMap<Protocol, Int>()
    private val appRequestCount = LinkedHashMap<Int?, Int>()
    private var requestsTotal = 0
    private var bytesUpTotal = 0L
    private var bytesDownTotal = 0L
    private var firstTs = Long.MAX_VALUE
    private var lastTs = Long.MIN_VALUE

    /** Records one captured exchange. */
    fun record(request: CapturedRequest) {
        val current = hosts[request.host]
        hosts[request.host] = HostStat(
            host = request.host,
            requests = (current?.requests ?: 0) + 1,
            bytesUp = (current?.bytesUp ?: 0) + request.bytesUp,
            bytesDown = (current?.bytesDown ?: 0) + request.bytesDown,
        )
        protocols[request.protocol] = (protocols[request.protocol] ?: 0) + 1
        val statusClass = (request.status ?: 0) / 100
        statusClasses[statusClass] = (statusClasses[statusClass] ?: 0) + 1
        appRequestCount[request.appUid] = (appRequestCount[request.appUid] ?: 0) + 1
        requestsTotal++
        bytesUpTotal += request.bytesUp
        bytesDownTotal += request.bytesDown
        if (request.timestampMs < firstTs) firstTs = request.timestampMs
        if (request.timestampMs > lastTs) lastTs = request.timestampMs
    }

    /** Host stats sorted by total bytes, descending. */
    fun hostStats(): List<HostStat> = hosts.values.sortedByDescending { it.totalBytes }

    /** Top [n] hosts by total traffic. */
    fun topHosts(n: Int): List<HostStat> = hostStats().take(n.coerceAtLeast(0))

    fun hostStat(host: String): HostStat? = hosts[host]

    fun totalRequests(): Int = requestsTotal

    fun totalBytesUp(): Long = bytesUpTotal

    fun totalBytesDown(): Long = bytesDownTotal

    fun protocolCounts(): Map<Protocol, Int> = protocols.toMap()

    /** Share of requests per app uid (null uid grouped under the unknown bucket). */
    fun appShares(): Map<Int?, Double> {
        if (requestsTotal == 0) return emptyMap()
        return appRequestCount.mapValues { it.value.toDouble() / requestsTotal }
    }

    /**
     * Average bandwidth in bits per second over the observation window.
     * Falls back to [fallbackWindowMs] when fewer than two timestamps exist.
     */
    fun bandwidthBps(fallbackWindowMs: Long = 1000): Double {
        if (requestsTotal == 0) return 0.0
        val span = if (lastTs > firstTs) (lastTs - firstTs).toDouble() else fallbackWindowMs.toDouble()
        val seconds = span / 1000.0
        if (seconds <= 0.0) return 0.0
        return (bytesUpTotal + bytesDownTotal) * 8.0 / seconds
    }

    fun firstTimestamp(): Long? = if (requestsTotal == 0) null else firstTs

    fun lastTimestamp(): Long? = if (requestsTotal == 0) null else lastTs

    fun reset() {
        hosts.clear()
        protocols.clear()
        appRequestCount.clear()
        statusClasses.clear()
        requestsTotal = 0
        bytesUpTotal = 0
        bytesDownTotal = 0
        firstTs = Long.MAX_VALUE
        lastTs = Long.MIN_VALUE
    }

    /** Requests per status class (1..5); statusless errors fall under 0. */
    fun statusClassCounts(): Map<Int, Int> = synchronized(this) { statusClasses.toMap() }

    /** Immutable totals snapshot for UI/agent tooling. */
    data class Summary(val requests: Int, val bytesUp: Long, val bytesDown: Long)

    private val statusClasses = LinkedHashMap<Int, Int>()
}
