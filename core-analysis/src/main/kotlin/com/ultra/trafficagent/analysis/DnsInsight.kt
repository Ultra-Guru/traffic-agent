package com.ultra.trafficagent.analysis

/**
 * Passive DNS profiling over a capture session.
 *
 * Observes (timestamp, domain, rcode) tuples extracted from DNS messages and
 * aggregates them into session-level insight: NXDOMAIN ratio, cache-relevant
 * TTL statistics, per-domain query counts and DoH/DoT transport detection
 * (UDP/443 traffic that does not parse as QUIC is almost always DoH).
 */
public class DnsInsight {

    /** One observed DNS transaction. */
    public data class Observation(
        val timestampMs: Long,
        val domain: String,
        val rcode: Int,
        val queryType: String = "A",
        val answerCount: Int = 0,
        val ttlSeconds: Long? = null,
        val transport: Transport = Transport.UDP53,
    )

    /** DNS transport classification. */
    public enum class Transport { UDP53, TCP53, DOH, DOT, UNKNOWN }

    /** Aggregated per-domain statistics. */
    public data class DomainStats(
        val domain: String,
        val queries: Int,
        val nxDomainCount: Int,
        val lastSeenMs: Long,
        val firstSeenMs: Long,
        val avgTtlSeconds: Long?,
        val answersObserved: Int,
    ) {
        val nxdomainRatio: Double get() = if (queries == 0) 0.0 else nxDomainCount.toDouble() / queries
    }

    /** Session-wide snapshot (immutable). */
    public data class Snapshot(
        val totalQueries: Int,
        val uniqueDomains: Int,
        val nxdomainCount: Int,
        val transportCounts: Map<Transport, Int>,
        val topDomains: List<DomainStats>,
        val minTtlSeconds: Long?,
        val maxTtlSeconds: Long?,
        val avgTtlSeconds: Long?,
        val dohDetected: Boolean,
        val suspiciousDomains: List<String>,
        val queryRatePerMinute: Double,
    ) {
        val nxdomainRatio: Double
            get() = if (totalQueries == 0) 0.0 else nxdomainCount.toDouble() / totalQueries
    }

    private val observations = mutableListOf<Observation>()
    private var sessionStartMs: Long = -1
    private var sessionEndMs: Long = -1

    /** Records one DNS observation. */
    public fun observe(observation: Observation) {
        observations.add(observation)
        if (sessionStartMs < 0 || observation.timestampMs < sessionStartMs) {
            sessionStartMs = observation.timestampMs
        }
        if (observation.timestampMs > sessionEndMs) {
            sessionEndMs = observation.timestampMs
        }
    }

    /** Number of raw observations so far. */
    public val size: Int get() = observations.size

    /** Clears all observations (new capture session). */
    public fun reset() {
        observations.clear()
        sessionStartMs = -1
        sessionEndMs = -1
    }

    /** Computes the current snapshot. */
    public fun snapshot(topN: Int = 10): Snapshot {
        val byDomain = observations.groupBy { it.domain.lowercase() }
        val stats = byDomain.map { (domain, obs) ->
            val ttls = obs.mapNotNull { it.ttlSeconds }
            DomainStats(
                domain = domain,
                queries = obs.size,
                nxDomainCount = obs.count { it.rcode == NXDOMAIN },
                lastSeenMs = obs.maxOf { it.timestampMs },
                firstSeenMs = obs.minOf { it.timestampMs },
                avgTtlSeconds = if (ttls.isEmpty()) null else ttls.average().toLong(),
                answersObserved = obs.sumOf { it.answerCount },
            )
        }
        val top = stats.sortedWith(
            compareByDescending<DomainStats> { it.queries }.thenBy { it.domain },
        ).take(topN)

        val ttlsAll = observations.mapNotNull { it.ttlSeconds }
        val transports = observations.groupingBy { it.transport }.eachCount()
        val spanMinutes = sessionSpanMinutes()

        return Snapshot(
            totalQueries = observations.size,
            uniqueDomains = byDomain.size,
            nxdomainCount = observations.count { it.rcode == NXDOMAIN },
            transportCounts = transports,
            topDomains = top,
            minTtlSeconds = ttlsAll.minOrNull(),
            maxTtlSeconds = ttlsAll.maxOrNull(),
            avgTtlSeconds = if (ttlsAll.isEmpty()) null else ttlsAll.average().toLong(),
            dohDetected = (transports[Transport.DOH] ?: 0) > 0,
            suspiciousDomains = stats.filter { isSuspicious(it) }
                .sortedByDescending { it.nxdomainRatio }
                .map { it.domain },
            queryRatePerMinute = if (spanMinutes > 0) observations.size / spanMinutes else 0.0,
        )
    }

    /** All observed domains, sorted alphabetically. */
    public fun domains(): List<String> = observations.map { it.domain.lowercase() }.distinct().sorted()

    private fun sessionSpanMinutes(): Double {
        if (sessionStartMs < 0 || sessionEndMs <= sessionStartMs) return 0.0
        return (sessionEndMs - sessionStartMs) / 60_000.0
    }

    /**
     * A domain is flagged when a large share of its queries fail to resolve
     * (typical for tracker wildcards) or it is queried at an abnormal rate.
     */
    private fun isSuspicious(stats: DomainStats): Boolean {
        if (stats.queries >= 3 && stats.nxdomainRatio >= 0.5) return true
        if (stats.queries >= 20) return true
        return false
    }

    public companion object {
        /** DNS rcode 3: name does not exist. */
        public const val NXDOMAIN: Int = 3

        /**
         * Classifies an observed UDP flow: port 443 payload that is neither
         * QUIC nor DNS/53 is presumed DNS-over-HTTPS.
         */
        public fun classifyTransport(
            srcPort: Int,
            dstPort: Int,
            looksLikeQuic: Boolean,
            payloadLength: Int,
        ): Transport {
            if (dstPort == 53 || srcPort == 53) {
                return if (payloadLength > 512) Transport.TCP53 else Transport.UDP53
            }
            if (dstPort == 443) {
                return if (looksLikeQuic) Transport.UNKNOWN else Transport.DOH
            }
            if (dstPort == 853 || srcPort == 853) return Transport.DOT
            return Transport.UNKNOWN
        }
    }
}
