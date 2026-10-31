package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol

/**
 * Bucketed traffic timeline powering the dashboard charts.
 *
 * Each bucket spans [bucketMs] and tracks request counts plus bytes split
 * by direction and protocol family, so the UI can render stacked area
 * charts (up vs down) and a request-per-bucket bar series.
 */
class TimeSeriesStats(private val bucketMs: Long = 1_000L) {

    /** One time bucket. [startMs] is inclusive, end is exclusive. */
    data class Bucket(
        val startMs: Long,
        var requests: Int = 0,
        var bytesUp: Long = 0,
        var bytesDown: Long = 0,
        var httpCount: Int = 0,
        var tlsCount: Int = 0,
        var quicCount: Int = 0,
        var otherCount: Int = 0,
        var errorCount: Int = 0,
    ) {
        val totalBytes: Long get() = bytesUp + bytesDown
    }

    private val buckets = LinkedHashMap<Long, Bucket>()
    private var originMs: Long = -1

    /** Records one exchange into its bucket. */
    fun record(request: CapturedRequest) {
        if (originMs < 0) originMs = request.timestampMs
        val bucketStart = align(request.timestampMs)
        val b = buckets.getOrPut(bucketStart) { Bucket(bucketStart) }
        b.requests++
        b.bytesUp += request.bytesUp
        b.bytesDown += request.bytesDown
        when (request.protocol) {
            Protocol.HTTP1, Protocol.HTTP2, Protocol.WEBSOCKET -> b.httpCount++
            Protocol.TLS -> b.tlsCount++
            Protocol.QUIC -> b.quicCount++
            else -> b.otherCount++
        }
        if ((request.status ?: 0) >= 500 || request.error != null) b.errorCount++
    }

    /** Total exchanges recorded. */
    val requestCount: Int get() = buckets.values.sumOf { it.requests }

    /** Buckets sorted by time, gaps filled with empty buckets. */
    fun series(): List<Bucket> {
        if (buckets.isEmpty()) return emptyList()
        val first = buckets.keys.min()
        val last = buckets.keys.max()
        val out = mutableListOf<Bucket>()
        var t = first
        while (t <= last) {
            out.add(buckets[t] ?: Bucket(t))
            t += bucketMs
        }
        return out
    }

    /** Compact CSV rendering (time,reqs,up,down,errors) for quick exports. */
    fun toCsv(): String {
        val sb = StringBuilder("time_ms,requests,bytes_up,bytes_down,errors\n")
        for (b in series()) {
            sb.append(b.startMs).append(',')
                .append(b.requests).append(',')
                .append(b.bytesUp).append(',')
                .append(b.bytesDown).append(',')
                .append(b.errorCount).append('\n')
        }
        return sb.toString()
    }

    /** Peak bytes-per-second observed in any bucket (double for fractions). */
    fun peakBytesPerSecond(): Double {
        val seconds = bucketMs / 1000.0
        return buckets.values.maxOfOrNull { it.totalBytes / seconds } ?: 0.0
    }

    /** Reset for a new session. */
    fun reset() {
        buckets.clear()
        originMs = -1
    }

    private fun align(ts: Long): Long = if (ts >= 0) ts / bucketMs * bucketMs else 0
}

/**
 * Weighted session health score (0..100) summarizing capture quality:
 * error rate, slow-exchange share, TLS/QUIC adoption and DNS health.
 */
object SessionScore {

    data class Components(
        val errorRate: Double,
        val slowShare: Double,
        val secureShare: Double,
        val nxdomainRate: Double,
        val exchangeCount: Int,
    )

    /**
     * Computes the score. Weights:
     *  - 45 points: 1 - errorRate (server 5xx + capture errors)
     *  - 25 points: 1 - slowShare (exchanges over [slowThresholdMs])
     *  - 20 points: secureShare (TLS + QUIC + HTTPS traffic share)
     *  - 10 points: 1 - nxdomainRate (DNS resolution failures)
     */
    fun compute(
        requests: List<CapturedRequest>,
        nxdomainRate: Double = 0.0,
        slowThresholdMs: Long = 1_000L,
    ): Int {
        if (requests.isEmpty()) return 100
        val errors = requests.count { (it.status ?: 0) >= 500 || it.error != null }
        val slow = requests.count { (it.durationMs ?: 0L) > slowThresholdMs }
        val secure = requests.count {
            it.protocol == Protocol.TLS || it.protocol == Protocol.QUIC || it.isSecure
        }
        val comps = Components(
            errorRate = errors.toDouble() / requests.size,
            slowShare = slow.toDouble() / requests.size,
            secureShare = secure.toDouble() / requests.size,
            nxdomainRate = nxdomainRate.coerceIn(0.0, 1.0),
            exchangeCount = requests.size,
        )
        return compute(comps)
    }

    fun compute(c: Components): Int {
        val score = 45.0 * (1.0 - c.errorRate.coerceIn(0.0, 1.0)) +
            25.0 * (1.0 - c.slowShare.coerceIn(0.0, 1.0)) +
            20.0 * c.secureShare.coerceIn(0.0, 1.0) +
            10.0 * (1.0 - c.nxdomainRate.coerceIn(0.0, 1.0))
        return score.toInt().coerceIn(0, 100)
    }

    /** Letter grade for the score (A+ .. D). */
    fun grade(score: Int): String = when {
        score >= 97 -> "A+"
        score >= 93 -> "A"
        score >= 90 -> "A-"
        score >= 87 -> "B+"
        score >= 83 -> "B"
        score >= 80 -> "B-"
        score >= 70 -> "C"
        score >= 60 -> "D"
        else -> "F"
    }
}
