package com.ultra.trafficagent.analysis

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TlsFingerprintRegistryTest {

    @Test
    fun `exact ja3 match returns client with full confidence`() {
        val m = TlsFingerprintRegistry.lookup(
            ja3Md5 = "CD08E31494F9531F560D64C695473DA9", // Chrome 110-120, upper case
        )
        assertNotNull(m.client)
        assertEquals("Chrome 110-120 (Windows)", m.client!!.name)
        assertEquals("chrome", m.client!!.family)
        assertEquals("windows", m.client!!.platform)
        assertEquals(1.0, m.confidence, 1e-9)
        assertEquals("ja3-exact", m.method)
    }

    @Test
    fun `exact ja4 match returns client`() {
        val m = TlsFingerprintRegistry.lookup(
            ja4 = "t13d1516h2_8daaf6152771_b0da82dd1658",
        )
        assertNotNull(m.client)
        assertEquals("chrome", m.client!!.family)
        assertEquals(0.9, m.confidence, 1e-9)
        assertEquals("ja4-exact", m.method)
    }

    @Test
    fun `ja3 wins over ja4 when both match`() {
        val m = TlsFingerprintRegistry.lookup(
            ja3Md5 = "cd08e31494f9531f560d64c695473da9",
            ja4 = "t13d1715h2_5b5ae14b22d0_e3f3e04ba110", // firefox ja4
        )
        assertEquals("ja3-exact", m.method)
        assertEquals("chrome", m.client!!.family)
    }

    @Test
    fun `unknown fingerprints report null client`() {
        val m = TlsFingerprintRegistry.lookup(
            ja3Md5 = "00000000000000000000000000000000",
            ja4 = "t99z9999zz_000000000000_000000000000",
        )
        assertNull(m.client)
        assertEquals(0.0, m.confidence, 1e-9)
        assertEquals("unknown", m.method)
    }

    @Test
    fun `null inputs are rejected safely`() {
        val m = TlsFingerprintRegistry.lookup()
        assertNull(m.client)
        assertEquals("unknown", m.method)
    }

    @Test
    fun `partA-only heuristic matches shared shape`() {
        // Not an exact JA4 (hash differs) but the a-part matches a unique
        // registered shape: okhttp 4.x "t13d1700-".
        val m = TlsFingerprintRegistry.lookup(
            ja4 = "t13d1700-_ffffffffffff_85b7a4c36f6d",
        )
        assertNotNull(m.client)
        assertEquals("okhttp", m.client!!.family)
        assertEquals(0.6, m.confidence, 1e-9)
        assertEquals("ja4-partA", m.method)
    }

    @Test
    fun `ambiguous partA falls through to unknown`() {
        // Two chrome-family entries share the partA t13d1516h2_8daaf6152771:
        // a different cipher-hash entry must not pick a winner.
        val m = TlsFingerprintRegistry.lookup(
            ja4 = "t13d1516h2_8daaf6152771_aaaaaaaaaaaa",
        )
        // Chrome 110-120 and Edge 120 share this a-part; ambiguous -> unknown.
        assertEquals("unknown", m.method)
        assertNull(m.client)
    }

    @Test
    fun `shape heuristics classify client families`() {
        assertEquals(
            "modern-browser",
            TlsFingerprintRegistry.guessFromShape(cipherCount = 15, extensionCount = 12, alpnPresent = true),
        )
        assertEquals(
            "legacy-browser",
            TlsFingerprintRegistry.guessFromShape(cipherCount = 20, extensionCount = 15, alpnPresent = false),
        )
        assertEquals(
            "http-library",
            TlsFingerprintRegistry.guessFromShape(cipherCount = 5, extensionCount = 6, alpnPresent = true),
        )
        assertEquals(
            "http-library",
            TlsFingerprintRegistry.guessFromShape(cipherCount = 2, extensionCount = 3, alpnPresent = false),
        )
        assertEquals(
            "minimal-or-scanner",
            TlsFingerprintRegistry.guessFromShape(cipherCount = 1, extensionCount = 0, alpnPresent = false),
        )
        assertEquals(
            "minimal-or-scanner",
            TlsFingerprintRegistry.guessFromShape(cipherCount = 0, extensionCount = 5, alpnPresent = true),
        )
    }

    @Test
    fun `registry contains a useful number of clients`() {
        val all = TlsFingerprintRegistry.all()
        assertTrue(all.size >= 25, "expected >= 25 known clients, got ${all.size}")
        // Every entry must have at least one fingerprint.
        assertTrue(all.all { it.ja3 != null || it.ja4 != null })
        // Families cover the majors.
        val families = all.map { it.family }.toSet()
        assertTrue(families.containsAll(listOf("chrome", "firefox", "safari", "curl", "okhttp")))
    }

    @Test
    fun `ja3 lookups are case insensitive`() {
        val lower = TlsFingerprintRegistry.lookup(ja3Md5 = "cd08e31494f9531f560d64c695473da9")
        val upper = TlsFingerprintRegistry.lookup(ja3Md5 = "CD08E31494F9531F560D64C695473DA9")
        assertEquals(lower.client?.name, upper.client?.name)
        assertEquals("Chrome 110-120 (Windows)", upper.client?.name)
    }

    @Test
    fun `ja4 lookups are case insensitive`() {
        val m = TlsFingerprintRegistry.lookup(ja4 = "T13D1516H2_8DAAF6152771_B0DA82DD1658")
        assertNotNull(m.client)
        assertEquals("ja4-exact", m.method)
    }
}
