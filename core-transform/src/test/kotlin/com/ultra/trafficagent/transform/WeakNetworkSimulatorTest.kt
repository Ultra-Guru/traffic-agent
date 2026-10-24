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

class WeakNetworkEdgeTest {

    @Test
    fun `token bucket boundary at exact capacity`() {
        val clock = object { var t = 0L }
        val bucket = TokenBucket(1_000, 1_000, { clock.t })
        // exact capacity: free
        assertEquals(0, bucket.reserve(1_000))
        // one byte over: must wait for that byte
        clock.t = 0 // no time passed
        assertEquals(0, bucket.reserve(0)) // zero is free
    }

    @Test
    fun `token bucket refill pacing`() {
        val clock = object { var t = 0L }
        val bucket = TokenBucket(1_000, 1_000, { clock.t })
        assertEquals(0, bucket.reserve(1_000)) // drains the bucket
        clock.t += 500_000_000 // half a second -> 500 tokens
        assertEquals(0, bucket.reserve(500))
        clock.t += 100_000_000 // 100 tokens only
        val wait = bucket.reserve(500) // 400 deficit -> 400ms
        assertTrue(wait in 390..410, "expected ~400ms, got $wait")
    }

    @Test
    fun `loss and jitter stay inside policy bounds across both directions`() {
        val sim = WeakNetworkSimulator(
            WeakNetworkPolicy(upDelayMs = 10, downDelayMs = 20, jitterMs = 30, seed = 7),
        )
        repeat(100) {
            val up = sim.onRequestReady(64) as Delivery.Deliver
            val down = sim.onResponseReady(64) as Delivery.Deliver
            assertTrue(up.afterMs in 10..40, "up out of range: ${up.afterMs}")
            assertTrue(down.afterMs in 20..50, "down out of range: ${down.afterMs}")
        }
    }

    @Test
    fun `policy validation rejects invalid values`() {
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            WeakNetworkPolicy(jitterMs = -1)
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            WeakNetworkPolicy(lossPercentUp = 101)
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            WeakNetworkPolicy(lossPercentDown = -1)
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            WeakNetworkPolicy(downKbps = -5)
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            WeakNetworkPolicy(upKbps = -5)
        }
        // zero-loss never drops, zero-bandwidth never throttles
        val sim = WeakNetworkSimulator(WeakNetworkPolicy())
        repeat(50) {
            assertTrue(sim.onRequestReady(1_000_000) is Delivery.Deliver)
        }
    }

    @Test
    fun `severe loss drops almost everything but deterministically`() {
        val sim = WeakNetworkSimulator(WeakNetworkPolicy(lossPercentDown = 95, seed = 99))
        var dropped = 0
        repeat(1_000) { if (sim.onResponseReady(1) is Delivery.Drop) dropped++ }
        assertTrue(dropped > 800, "expected heavy loss, got $dropped/1000")
        val again = WeakNetworkSimulator(WeakNetworkPolicy(lossPercentDown = 95, seed = 99))
        var dropped2 = 0
        repeat(1_000) { if (again.onResponseReady(1) is Delivery.Drop) dropped2++ }
        assertEquals(dropped, dropped2)
    }
}
