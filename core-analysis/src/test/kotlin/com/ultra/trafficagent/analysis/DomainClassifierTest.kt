package com.ultra.trafficagent.analysis

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DomainClassifierTest {

    @Test
    fun `registrable domain strips subdomains`() {
        assertEquals("example.com", DomainClassifier.registrableDomain("example.com"))
        assertEquals("example.com", DomainClassifier.registrableDomain("a.b.example.com"))
        assertEquals("example.co.uk", DomainClassifier.registrableDomain("a.b.example.co.uk"))
        assertEquals("example.co.uk", DomainClassifier.registrableDomain("example.co.uk"))
        // Trailing dot normalization.
        assertEquals("example.com", DomainClassifier.registrableDomain("www.example.com."))
        // Case normalization.
        assertEquals("example.com", DomainClassifier.registrableDomain("WWW.Example.COM"))
    }

    @Test
    fun `short hosts pass through unchanged`() {
        assertEquals("com", DomainClassifier.registrableDomain("com"))
        assertEquals("a.b", DomainClassifier.registrableDomain("a.b"))
        assertEquals("", DomainClassifier.registrableDomain(""))
    }

    @Test
    fun `ip literals are returned as-is`() {
        assertEquals("192.168.1.1", DomainClassifier.registrableDomain("192.168.1.1"))
        assertEquals("fe80::1", DomainClassifier.registrableDomain("fe80::1"))
        assertTrue(DomainClassifier.isIpAddress("10.0.0.1"))
        assertTrue(DomainClassifier.isIpAddress("::1"))
        assertFalse(DomainClassifier.isIpAddress("1.2.3.4.5"))
        assertFalse(DomainClassifier.isIpAddress("999.1.1.1"))
        assertFalse(DomainClassifier.isIpAddress("example.com"))
    }

    @Test
    fun `ads category with risk boost`() {
        val r = DomainClassifier.classify("ad.doubleclick.net")
        assertEquals(DomainClassifier.Category.ADS, r.category)
        assertEquals("doubleclick.net", r.matchedRule)
        assertEquals("doubleclick.net", r.registrableDomain)
        assertTrue(r.riskScore >= 40)
    }

    @Test
    fun `tracker category fires on suffix match`() {
        val r = DomainClassifier.classify("sdk.appsflyer.com")
        assertEquals(DomainClassifier.Category.TRACKER, r.category)
        assertEquals("appsflyer.com", r.matchedRule)
    }

    @Test
    fun `cdn and social stay low risk`() {
        val cdn = DomainClassifier.classify("cdn.cloudflare.net")
        assertEquals(DomainClassifier.Category.CDN, cdn.category)
        assertTrue(cdn.riskScore <= 20)

        val social = DomainClassifier.classify("api.x.com")
        assertEquals(DomainClassifier.Category.SOCIAL, social.category)
        assertTrue(social.riskScore <= 20)
    }

    @Test
    fun `normal domain has zero risk`() {
        val r = DomainClassifier.classify("www.wikipedia.org")
        assertEquals(DomainClassifier.Category.NORMAL, r.category)
        assertEquals(0, r.riskScore)
        assertNull(r.matchedRule)
        assertFalse(r.punycode)
        assertFalse(r.suspiciousTld)
    }

    @Test
    fun `punycode and suspicious tld add risk`() {
        val puny = DomainClassifier.classify("xn--80ak6aa92e.com")
        assertTrue(puny.punycode)
        assertTrue(puny.riskScore >= 20)

        val tld = DomainClassifier.classify("free-money.top")
        assertTrue(tld.suspiciousTld)
        assertTrue(tld.riskScore >= 15)
    }

    @Test
    fun `deep subdomain chains add risk`() {
        val r = DomainClassifier.classify("a.b.c.d.e.f.deepchain.org")
        assertTrue(r.riskScore >= 10)
    }

    @Test
    fun `ads take priority over social`() {
        // A host matching both lists resolves to ADS.
        val r = DomainClassifier.classify("ads.facebook.com")
        // facebook.com is social, ads.facebook.com does not suffix-match ads list...
        // it matches "facebook.com" in the social list.
        assertEquals(DomainClassifier.Category.SOCIAL, r.category)
    }

    @Test
    fun `metrics endpoints recognized`() {
        val r = DomainClassifier.classify("play.googleapis.com")
        assertEquals(DomainClassifier.Category.METRICS, r.category)
    }

    @Test
    fun `risk score clamped to 100`() {
        // ads(50) + punycode(25) + deep chain(10+15) = 100 before clamping.
        val r = DomainClassifier.classify("a.b.c.d.e.f.g.h.xn--80ak6aa92e.doubleclick.net")
        assertEquals(DomainClassifier.Category.ADS, r.category)
        assertTrue(r.punycode)
        assertEquals(100, r.riskScore)
    }

    @Test
    fun `registrable domain of tracker suffix domains`() {
        assertEquals("doubleclick.net", DomainClassifier.registrableDomain("ad.doubleclick.net"))
        assertEquals("appsflyer.com", DomainClassifier.registrableDomain("sdk.appsflyer.com"))
        // com.au is a multi-part suffix.
        assertEquals("example.com.au", DomainClassifier.registrableDomain("shop.example.com.au"))
    }
}
