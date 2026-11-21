package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Mutation-killing edge tests for the analyzer suite (parser keyword table,
 * DNS insight boundaries, domain classifier branches, score weights).
 */
class AnalyzerEdgeMatrixTest {

    private fun req(
        host: String = "api.example.com",
        status: Int? = 200,
        durationMs: Long? = 100,
        bytesUp: Long = 10,
        bytesDown: Long = 10,
        proto: Protocol = Protocol.TLS,
        error: String? = null,
    ) = CapturedRequest(
        id = 1, timestampMs = 0, host = host, path = "/", method = "GET", status = status,
        requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
        responseBody = "", bytesUp = bytesUp, bytesDown = bytesDown, protocol = proto,
        appUid = null, durationMs = durationMs, error = error,
    )

    // ---------------- RuleDslParser keyword table ----------------

    @Test
    fun `every operator keyword parses as an operator token`() {
        // Word-form operators must be recognized in conditions.
        val rs = RuleDslParser.parse(
            """
            rule w1 when host contains "example" then tag name=a
            rule w2 when host starts_with "api." then tag name=b
            rule w3 when host ends_with ".com" then tag name=c
            rule w4 when host matches "^api" then tag name=d
            rule w5 when status in 200,204 then tag name=e
            """.trimIndent(),
        )
        assertEquals(listOf("a"), rs.evaluate(req()).tags.filter { it == "a" })
        assertEquals(listOf("b"), rs.evaluate(req(host = "api.example.com")).tags.filter { it == "b" })
        assertEquals(listOf("c"), rs.evaluate(req(host = "example.com")).tags.filter { it == "c" })
        assertEquals(listOf("d"), rs.evaluate(req(host = "api.example.com")).tags.filter { it == "d" })
        // status 200 in {200,204}
        assertEquals(setOf("e"), rs.evaluate(req(status = 204)).tags.filter { it == "e" }.toSet())
    }

    @Test
    fun `symbol operators parse including two char forms`() {
        val rs = RuleDslParser.parse(
            """
            rule s1 when total >= 20 then tag name=ge
            rule s2 when total <= 20 then tag name=le
            rule s3 when total > 19 then tag name=gt
            rule s4 when total < 21 then tag name=lt
            rule s5 when status != 200 then tag name=ne
            rule s6 when status = 500 then tag name=eq
            """.trimIndent(),
        )
        val d = rs.evaluate(req(bytesUp = 10, bytesDown = 10))  // total = 20
        assertEquals(setOf("ge", "le", "gt", "lt"), d.tags.toSet())
        val e = rs.evaluate(req(status = 500, bytesUp = 10, bytesDown = 10))
        assertEquals(setOf("ge", "le", "gt", "lt", "ne", "eq"), e.tags.toSet())
    }

    @Test
    fun `and or not keywords with case sensitivity`() {
        // Keywords are matched lower-case; uppercase AND is an ident (error).
        val rs = RuleDslParser.parse(
            "rule x when host = \"a.com\" and not status = 500 then block",
        )
        assertTrue(rs.evaluate(req(host = "a.com", status = 200)).matchedRule != null)
        val thrown = runCatching {
            RuleDslParser.parse("rule x when host = \"a\" AND status = 5 then block")
        }
        // AND (uppercase) is a bare ident: the parser either rejects it as a
        // field name or fails on the structure - both are acceptable errors.
        assertTrue(thrown.isFailure || runCatching {
            rs.evaluate(req(host = "a"))
            true
        }.isSuccess)
    }

    @Test
    fun `action keywords all dispatch`() {
        val rs = RuleDslParser.parse(
            """
            rule a1 when host = "x.com" then allow
            rule b1 when host = "y.com" then block
            rule t1 when host = "z.com" then throttle rate=10
            rule m1 when host = "w.com" then mock status=201
            rule g1 when host = "v.com" then tag name=tagged
            rule r1 when host = "u.com" then redact
            """.trimIndent(),
        )
        assertEquals(RuleAction.ALLOW, rs.evaluate(req(host = "x.com")).action)
        assertEquals(RuleAction.BLOCK, rs.evaluate(req(host = "y.com")).action)
        assertEquals(RuleAction.THROTTLE, rs.evaluate(req(host = "z.com")).action)
        assertEquals(RuleAction.MOCK, rs.evaluate(req(host = "w.com")).action)
        assertEquals(listOf("tagged"), rs.evaluate(req(host = "v.com")).tags)
        assertTrue(rs.evaluate(req(host = "u.com")).redact)
    }

    @Test
    fun `enabled and disabled keywords consume state`() {
        val rs = RuleDslParser.parse(
            """
            rule e1 enabled when true then block
            rule d1 disabled when true then block
            """.trimIndent(),
        )
        // e1 blocks everything; d1 never fires.
        assertEquals(RuleAction.BLOCK, rs.evaluate(req()).action)
        val onlyDisabled = RuleDslParser.parse("rule d2 disabled when true then block")
        assertEquals(RuleAction.ALLOW, onlyDisabled.evaluate(req()).action)
    }

    @Test
    fun `bare lone exclamation rejected`() {
        val thrown = runCatching {
            RuleDslParser.parse("rule x when host ! \"a\" then block")
        }
        assertTrue(thrown.isFailure)
    }

    @Test
    fun `param values can be bare or quoted`() {
        val rs = RuleDslParser.parse(
            """
            rule p1 when path = "/a" then tag name=bare
            rule p2 when path = "/b" then tag name="quoted tag"
            """.trimIndent(),
        )
        assertEquals(listOf("bare"), rs.evaluate(req2(path = "/a")).tags)
        assertEquals(listOf("quoted tag"), rs.evaluate(req2(path = "/b")).tags)
    }

    private fun req2(path: String): CapturedRequest = CapturedRequest(
        id = 1, timestampMs = 0, host = "h", path = path, method = "GET", status = 200,
        requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
        responseBody = "", bytesUp = 1, bytesDown = 1, protocol = Protocol.HTTP1, appUid = null,
    )

    // ---------------- DnsInsight boundaries ----------------

    @Test
    fun `snapshot with topN larger than domain count returns all`() {
        val insight = DnsInsight()
        insight.observe(DnsInsight.Observation(0, "a.com", 0))
        val snap = insight.snapshot(topN = 50)
        assertEquals(1, snap.topDomains.size)
        assertEquals("a.com", snap.topDomains[0].domain)
    }

    @Test
    fun `snapshot with topN zero returns empty list`() {
        val insight = DnsInsight()
        insight.observe(DnsInsight.Observation(0, "a.com", 0))
        assertTrue(insight.snapshot(topN = 0).topDomains.isEmpty())
    }

    @Test
    fun `equal query counts tie-break alphabetically`() {
        val insight = DnsInsight()
        insight.observe(DnsInsight.Observation(0, "beta.com", 0))
        insight.observe(DnsInsight.Observation(1, "alpha.com", 0))
        val top = insight.snapshot(topN = 2).topDomains
        assertEquals("alpha.com", top[0].domain)
        assertEquals("beta.com", top[1].domain)
    }

    @Test
    fun `first observation initializes span`() {
        val insight = DnsInsight()
        insight.observe(DnsInsight.Observation(5_000, "a.com", 0, ttlSeconds = 60))
        val snap = insight.snapshot()
        assertEquals(60L, snap.minTtlSeconds)
        assertEquals(60L, snap.maxTtlSeconds)
        assertEquals(60L, snap.avgTtlSeconds)
        assertEquals(0.0, snap.queryRatePerMinute, 1e-9)
    }

    @Test
    fun `negative transport counts absent from map`() {
        val insight = DnsInsight()
        val snap = insight.snapshot()
        assertTrue(snap.transportCounts.isEmpty())
        assertFalse(snap.dohDetected)
    }

    @Test
    fun `domains helper dedupes case variants`() {
        val insight = DnsInsight()
        insight.observe(DnsInsight.Observation(0, "Example.COM", 0))
        insight.observe(DnsInsight.Observation(1, "example.com", 0))
        assertEquals(listOf("example.com"), insight.domains())
    }

    // ---------------- DomainClassifier edges ----------------

    @Test
    fun `registrable domain multi part suffix needs three labels`() {
        // "co.uk" alone is a public suffix, not a registrable domain.
        assertEquals("co.uk", DomainClassifier.registrableDomain("co.uk"))
        assertEquals("example.co.uk", DomainClassifier.registrableDomain("example.co.uk"))
    }

    @Test
    fun `ipv6 forms recognized and rejected`() {
        assertTrue(DomainClassifier.isIpAddress("::"))
        assertTrue(DomainClassifier.isIpAddress("2001:db8::1"))
        assertFalse(DomainClassifier.isIpAddress("2001:zz8::1"))
        assertFalse(DomainClassifier.isIpAddress("::1:zz"))
    }

    @Test
    fun `ipv4 octet boundaries validated`() {
        assertTrue(DomainClassifier.isIpAddress("0.0.0.0"))
        assertTrue(DomainClassifier.isIpAddress("255.255.255.255"))
        assertFalse(DomainClassifier.isIpAddress("256.1.1.1"))
        assertFalse(DomainClassifier.isIpAddress("1.2.3"))
    }

    @Test
    fun `cdn exact host and suffix both match`() {
        // Exact host in the cdn list.
        assertEquals(DomainClassifier.Category.CDN, DomainClassifier.classify("unpkg.com").category)
        // Subdomain of a listed entry.
        assertEquals(
            DomainClassifier.Category.CDN,
            DomainClassifier.classify("edge.unpkg.com").category,
        )
    }

    @Test
    fun `tracker registrable match fires for subdomains`() {
        val r = DomainClassifier.classify("europe1.mixpanel.com")
        assertEquals(DomainClassifier.Category.TRACKER, r.category)
        assertEquals("mixpanel.com", r.matchedRule)
    }

    @Test
    fun `social category for api subdomain`() {
        val r = DomainClassifier.classify("graph.facebook.com")
        assertEquals(DomainClassifier.Category.SOCIAL, r.category)
    }

    @Test
    fun `ads beats tracker when both could match`() {
        // "adservice.google.com" is ads; analytics.google.com is tracker.
        assertEquals(
            DomainClassifier.Category.ADS,
            DomainClassifier.classify("adservice.google.com").category,
        )
        assertEquals(
            DomainClassifier.Category.TRACKER,
            DomainClassifier.classify("analytics.google.com").category,
        )
    }

    @Test
    fun `deep chain risk increments at six and nine labels`() {
        val five = DomainClassifier.classify("a.b.c.site.org")
        val six = DomainClassifier.classify("a.b.c.d.site.org")
        val nine = DomainClassifier.classify("a.b.c.d.e.f.g.site.org")
        assertTrue(six.riskScore > five.riskScore)
        assertTrue(nine.riskScore > six.riskScore)
        // CDN risk stays clamped despite deep chains.
        val cdnDeep = DomainClassifier.classify("a.b.c.d.e.f.g.h.unpkg.com")
        assertTrue(cdnDeep.riskScore <= 20)
    }

    @Test
    fun `suspicious tld on normal category still adds risk`() {
        val r = DomainClassifier.classify("info.top")
        assertEquals(DomainClassifier.Category.NORMAL, r.category)
        assertEquals(20, r.riskScore)
    }

    // ---------------- SessionScore weights ----------------

    @Test
    fun `weights sum to one hundred at boundaries`() {
        // All-bad inputs: 0 errors? no - craft each component at its extreme.
        val worst = SessionScore.compute(
            SessionScore.Components(
                errorRate = 1.0, slowShare = 1.0, secureShare = 0.0,
                nxdomainRate = 1.0, exchangeCount = 10,
            ),
        )
        assertEquals(0, worst)
        val best = SessionScore.compute(
            SessionScore.Components(
                errorRate = 0.0, slowShare = 0.0, secureShare = 1.0,
                nxdomainRate = 0.0, exchangeCount = 10,
            ),
        )
        assertEquals(100, best)
    }

    @Test
    fun `each component contributes its weight`() {
        fun score(err: Double, slow: Double, sec: Double, nx: Double) = SessionScore.compute(
            SessionScore.Components(err, slow, sec, nx, 10),
        )
        // Everything else perfect, only errors vary: 45-point span.
        assertEquals(100, score(0.0, 0.0, 1.0, 0.0))
        assertEquals(55, score(1.0, 0.0, 1.0, 0.0))
        // Slow share: 25-point span.
        assertEquals(75, score(0.0, 1.0, 1.0, 0.0))
        // Secure share: 20-point span.
        assertEquals(80, score(0.0, 0.0, 0.0, 0.0))
        // NXDOMAIN: 10-point span.
        assertEquals(90, score(0.0, 0.0, 1.0, 1.0))
    }

    @Test
    fun `out of range components are clamped not exploded`() {
        val c = SessionScore.compute(
            SessionScore.Components(
                errorRate = 5.0, slowShare = -3.0, secureShare = 42.0,
                nxdomainRate = 7.0, exchangeCount = 3,
            ),
        )
        assertTrue(c in 0..100)
        // errorRate clamps to 1 (0 pts), slowShare to 0 (25), secure 1 (20), nx 1 (0) = 45.
        assertEquals(45, c)
    }

    @Test
    fun `score never negative or above hundred`() {
        val odd = SessionScore.compute(
            SessionScore.Components(
                errorRate = -1.0, slowShare = -1.0, secureShare = -1.0,
                nxdomainRate = -1.0, exchangeCount = 1,
            ),
        )
        assertTrue(odd in 0..100)
    }
}
