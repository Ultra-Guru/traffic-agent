package com.ultra.trafficagent.analysis

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DnsInsightTest {

    private fun obs(
        ts: Long,
        domain: String,
        rcode: Int = 0,
        ttl: Long? = null,
        transport: DnsInsight.Transport = DnsInsight.Transport.UDP53,
        answers: Int = 1,
    ) = DnsInsight.Observation(ts, domain, rcode, "A", answers, ttl, transport)

    @Test
    fun `empty session reports zeros`() {
        val insight = DnsInsight()
        val snap = insight.snapshot()
        assertEquals(0, snap.totalQueries)
        assertEquals(0, snap.uniqueDomains)
        assertEquals(0.0, snap.nxdomainRatio, 1e-9)
        assertNull(snap.minTtlSeconds)
        assertNull(snap.avgTtlSeconds)
        assertFalse(snap.dohDetected)
        assertTrue(snap.topDomains.isEmpty())
        assertTrue(suspiciousEmpty(snap))
    }

    private fun suspiciousEmpty(snap: DnsInsight.Snapshot): Boolean = snap.suspiciousDomains.isEmpty()

    @Test
    fun `counts unique domains and nxdomain ratio`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "example.com"))
        insight.observe(obs(2000, "example.com"))
        insight.observe(obs(3000, "tracker.ad", rcode = 3))
        val snap = insight.snapshot()
        assertEquals(3, snap.totalQueries)
        assertEquals(2, snap.uniqueDomains)
        assertEquals(1, snap.nxdomainCount)
        assertEquals(1.0 / 3.0, snap.nxdomainRatio, 1e-9)
    }

    @Test
    fun `top domains sorted by query count then name`() {
        val insight = DnsInsight()
        repeat(3) { insight.observe(obs(it.toLong(), "b.com")) }
        repeat(5) { insight.observe(obs(it.toLong(), "a.com")) }
        insight.observe(obs(99, "c.com"))
        val top = insight.snapshot(topN = 3).topDomains
        assertEquals(listOf("a.com", "b.com", "c.com"), top.map { it.domain })
        assertEquals(5, top[0].queries)
        assertEquals(3, top[1].queries)
        assertEquals(1, top[2].queries)
    }

    @Test
    fun `ttl statistics aggregate min max avg`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "a.com", ttl = 60))
        insight.observe(obs(2000, "a.com", ttl = 30))
        insight.observe(obs(3000, "b.com", ttl = 90))
        val snap = insight.snapshot()
        assertEquals(30L, snap.minTtlSeconds)
        assertEquals(90L, snap.maxTtlSeconds)
        assertEquals(60L, snap.avgTtlSeconds) // (60+30+90)/3
    }

    @Test
    fun `doh detection flags transport`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "dns.google", transport = DnsInsight.Transport.DOH))
        val snap = insight.snapshot()
        assertTrue(snap.dohDetected)
        assertEquals(1, snap.transportCounts[DnsInsight.Transport.DOH])
    }

    @Test
    fun `suspicious domains require repeated nxdomain`() {
        val insight = DnsInsight()
        // 1 failed lookup alone is not suspicious.
        insight.observe(obs(1000, "once.tracker", rcode = 3))
        assertFalse(insight.snapshot().suspiciousDomains.contains("once.tracker"))

        // 3 queries, 2 NXDOMAIN -> ratio 2/3 >= 0.5 -> flagged.
        insight.observe(obs(2000, "many.tracker", rcode = 3))
        insight.observe(obs(3000, "many.tracker", rcode = 3))
        insight.observe(obs(4000, "many.tracker", rcode = 0))
        val suspicious = insight.snapshot().suspiciousDomains
        assertTrue(suspicious.contains("many.tracker"))
        assertFalse(suspicious.contains("once.tracker"))
    }

    @Test
    fun `high volume domain is suspicious regardless of rcode`() {
        val insight = DnsInsight()
        repeat(25) { insight.observe(obs(it.toLong(), "chatty.io", rcode = 0)) }
        assertTrue(insight.snapshot().suspiciousDomains.contains("chatty.io"))
    }

    @Test
    fun `query rate uses session span`() {
        val insight = DnsInsight()
        // 10 queries across 4.5 minutes (0 .. 270s) -> 10/4.5 per minute.
        for (i in 0 until 10) {
            insight.observe(obs(i * 30_000L, "rate.com"))
        }
        assertEquals(10.0 / 4.5, insight.snapshot().queryRatePerMinute, 1e-6)
    }

    @Test
    fun `single observation has zero rate`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "single.com"))
        assertEquals(0.0, insight.snapshot().queryRatePerMinute, 1e-9)
    }

    @Test
    fun `reset clears state`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "a.com"))
        assertEquals(1, insight.size)
        insight.reset()
        assertEquals(0, insight.size)
        assertEquals(0, insight.snapshot().totalQueries)
    }

    @Test
    fun `domains list is deduplicated and sorted`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "zeta.com"))
        insight.observe(obs(2000, "alpha.com"))
        insight.observe(obs(3000, "alpha.com"))
        assertEquals(listOf("alpha.com", "zeta.com"), insight.domains())
    }

    @Test
    fun `transport classification rules`() {
        val t = DnsInsight.Companion::classifyTransport
        assertEquals(DnsInsight.Transport.UDP53, t(51000, 53, false, 80))
        assertEquals(DnsInsight.Transport.UDP53, t(53, 51000, false, 80))
        // >512 bytes on port 53 means the resolver fell back to TCP.
        assertEquals(DnsInsight.Transport.TCP53, t(51000, 53, false, 800))
        assertEquals(DnsInsight.Transport.DOH, t(51000, 443, false, 300))
        assertEquals(DnsInsight.Transport.UNKNOWN, t(51000, 443, true, 300))
        assertEquals(DnsInsight.Transport.DOT, t(51000, 853, false, 100))
        assertEquals(DnsInsight.Transport.DOT, t(853, 51000, false, 100))
        assertEquals(DnsInsight.Transport.UNKNOWN, t(51000, 8080, false, 100))
    }

    @Test
    fun `domain stats expose nxdomain ratio`() {
        val insight = DnsInsight()
        insight.observe(obs(1000, "a.com", rcode = 3))
        insight.observe(obs(2000, "a.com", rcode = 3))
        insight.observe(obs(3000, "a.com", rcode = 0))
        val stats = insight.snapshot().topDomains.first { it.domain == "a.com" }
        assertEquals(3, stats.queries)
        assertEquals(2, stats.nxDomainCount)
        assertEquals(2.0 / 3.0, stats.nxdomainRatio, 1e-9)
        assertEquals(1000L, stats.firstSeenMs)
        assertEquals(3000L, stats.lastSeenMs)
    }
}
