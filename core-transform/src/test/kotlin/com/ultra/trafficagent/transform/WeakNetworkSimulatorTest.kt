package com.ultra.trafficagent.transform

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class WeakNetworkSimulatorTest {

    @Test
    fun `zero policy delivers everything immediately`() {
        val sim = WeakNetworkSimulator(WeakNetworkPolicy())
        repeat(50) {
            assertEquals(Delivery.Deliver(0), sim.onRequestReady(10_000))
            assertEquals(Delivery.Deliver(0), sim.onResponseReady(10_000))
        }
    }

    @Test
    fun `fixed delay applies per direction`() {
        val sim = WeakNetworkSimulator(WeakNetworkPolicy(upDelayMs = 120, downDelayMs = 45))
        val up = sim.onRequestReady(1)
        val down = sim.onResponseReady(1)
        assertTrue(up is Delivery.Deliver && up.afterMs == 120L, "got $up")
        assertTrue(down is Delivery.Deliver && down.afterMs == 45L, "got $down")
    }

    @Test
    fun `jitter stays within bounds`() {
        val sim = WeakNetworkSimulator(WeakNetworkPolicy(upDelayMs = 100, jitterMs = 50))
        repeat(200) {
            val d = sim.onRequestReady(1) as Delivery.Deliver
            assertTrue(d.afterMs in 100..150, "out of range: ${d.afterMs}")
        }
    }

    @Test
    fun `deterministic loss rate with seed`() {
        val sim = WeakNetworkSimulator(WeakNetworkPolicy(lossPercentDown = 50, seed = 42))
        var dropped = 0
        repeat(2_000) {
            if (sim.onResponseReady(1) is Delivery.Drop) dropped++
        }
        // deterministic seed: same count on every run
        val sim2 = WeakNetworkSimulator(WeakNetworkPolicy(lossPercentDown = 50, seed = 42))
        var dropped2 = 0
        repeat(2_000) {
            if (sim2.onResponseReady(1) is Delivery.Drop) dropped2++
        }
        assertEquals(dropped2, dropped)
        assertTrue(dropped in 800..1200, "loss ratio off: $dropped/2000")
    }

    @Test
    fun `token bucket throttles bursts`() {
        val clock = TestClock()
        // 1000 bytes/second, capacity 1000
        val bucket = TokenBucket(1_000, 1_000, clock::now)
        assertEquals(0, bucket.reserve(500))
        clock.advanceMs(0) // no refill yet
        // 1500 total: 500 left in bucket -> must wait 500ms for the deficit
        val wait = bucket.reserve(1_000)
        assertTrue(wait in 450..550, "expected ~500ms wait, got $wait")
        clock.advanceMs(600)
        assertEquals(0, bucket.reserve(100))
    }

    @Test
    fun `unlimited bucket never waits`() {
        val bucket = TokenBucket(0, 0)
        assertEquals(0, bucket.reserve(1_000_000_000))
    }

    @Test
    fun `bandwidth cap delays bursts beyond the first second`() {
        val sim = WeakNetworkSimulator(WeakNetworkPolicy(downKbps = 64, seed = 1))
        // capacity equals one second of traffic: the first 8KB burst is free
        val burst = sim.onResponseReady(8 * 1024) as Delivery.Deliver
        assertEquals(0, burst.afterMs)
        // 32KB exceeds the bucket: the deficit over 8KB/s must wait ~3s
        val big = sim.onResponseReady(32 * 1024) as Delivery.Deliver
        assertTrue(big.afterMs >= 2_500, "expected throttling, got ${big.afterMs}ms")
    }

    private class TestClock {
        private var t = 0L
        fun now(): Long = t
        fun advanceMs(ms: Long) {
            t += ms * 1_000_000
        }
    }
}

class ShortCircuitActionsTest {

    private fun exchange(body: String = ""): MutableExchange =
        MutableExchange(MutableHttpRequest("GET", "api.example.com", "/x"), null as MutableHttpResponse?)
            .also { it.request.body = body }

    @Test
    fun `mock response creates the response and short circuits`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "m1",
                name = "mock",
                match = RuleMatch(hostRegex = "api.example.com"),
                actions = listOf(RuleAction.MockResponse(201, """{"ok":true}""")),
            ),
        )
        val exchange = exchange()
        val result = HttpRewriter(registry).applyTo(exchange)
        assertTrue(result.shortCircuited)
        assertFalse(result.dropped)
        assertEquals(201, exchange.response?.status)
        assertEquals("""{"ok":true}""", exchange.response?.body)
        assertEquals("application/json", exchange.response?.header("content-type"))
        assertTrue("m1" in result.appliedRuleIds)
    }

    @Test
    fun `block rejects with status and reason`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "b1",
                name = "block",
                actions = listOf(RuleAction.Block(410, "gone")),
            ),
        )
        val exchange = exchange()
        val result = HttpRewriter(registry).applyTo(exchange)
        assertTrue(result.shortCircuited)
        assertEquals(410, exchange.response?.status)
        assertEquals("gone", exchange.response?.body)
    }

    @Test
    fun `abort marks dropped`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "a1",
                name = "abort",
                actions = listOf(RuleAction.Abort(8_000)),
            ),
        )
        val result = HttpRewriter(registry).applyTo(exchange())
        assertTrue(result.shortCircuited)
        assertTrue(result.dropped)
    }

    @Test
    fun `rewrite result keeps binary compatibility defaults`() {
        val r = RewriteResult(listOf("x"), listOf("y"), 5)
        assertFalse(r.shortCircuited)
        assertFalse(r.dropped)
        assertEquals(RewriteResult.NONE.delayedByMs, 0L)
    }
}
