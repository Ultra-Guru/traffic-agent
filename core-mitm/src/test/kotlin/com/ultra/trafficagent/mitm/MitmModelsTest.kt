package com.ultra.trafficagent.mitm

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/** Pure-logic coverage for the models and rewriting bridge. */
class MitmModelsTest {

    @Test
    fun `mutable headers preserve order and replace case-insensitively`() {
        val h = MutableHeaders()
        h.add("Content-Type", "application/json")
        h.add("X-A", "1")
        h.add("x-a", "2") // repeated names survive
        assertEquals("application/json", h.get("content-type"))
        assertEquals("application/json", h.get("CONTENT-TYPE"))
        assertEquals("1", h.get("x-a"))
        assertEquals(3, h.toList().size)

        h.set("X-A", "3") // replaces every occurrence, keeps position
        assertEquals("3", h.get("x-a"))
        assertEquals(2, h.toList().size)
        assertEquals("Content-Type", h.toList()[0].first)

        assertTrue(h.remove("x-a"))
        assertFalse(h.remove("x-a"))
        assertEquals(1, h.toList().size)
        assertNull(h.get("x-a"))
    }

    @Test
    fun `mutable headers replaceWith copies and clears`() {
        val a = MutableHeaders(listOf("a" to "1", "b" to "2"))
        val b = MutableHeaders(listOf("c" to "3"))
        a.replaceWith(b)
        assertEquals(listOf("c" to "3"), a.toList())
        assertEquals("3", a.get("c"))
        assertEquals(null, a.get("a"))
    }

    @Test
    fun `proxy exchange data surface`() {
        val e = ProxyExchange(
            id = 7, timestampMs = 1, scheme = "https", host = "h.io", port = 443,
            method = "GET", path = "/x", requestHeaders = listOf("a" to "b"),
            requestBody = null, status = 200, responseHeaders = emptyList(),
            responseBody = null, responseDecodedBody = null, requestBytes = 1,
            responseBytes = 2, durationMs = 3, tls = true,
        )
        assertEquals(7, e.id)
        assertTrue(e.tls)
        assertEquals(200, e.status)
        assertEquals("GET", e.method)
    }

    @Test
    fun `mitm config validation rejects bad values`() {
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            MitmConfig(captureMaxBodyBytes = -1)
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            MitmConfig(connectTimeoutMs = 0)
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            MitmConfig(workers = 0)
        }
        // defaults hold
        val d = MitmConfig()
        assertEquals(1 shl 20, d.captureMaxBodyBytes)
        assertEquals(8, d.workers)
        assertFalse(d.trustOriginAll)
        assertEquals(0, d.interceptors.size)
    }

    @Test
    fun `short circuit decision carries the answer`() {
        val ctx = MutableProxyExchange(
            scheme = "http", host = "x", port = 80, method = "GET", path = "/",
        )
        ctx.requestHeaders.add("q", "1")
        ctx.requestBody = ByteArray(3)
        ctx.status = 500
        ctx.responseHeaders.add("r", "2")
        ctx.responseBody = ByteArray(5)
        ctx.appliedRuleIds += "rule-1"
        val decision = ctx.shortCircuit(418, "no".toByteArray(), "text/plain")
        assertTrue(decision is ProxyDecision.ShortCircuit)
        val sc = decision as ProxyDecision.ShortCircuit
        assertEquals(418, sc.status)
        assertEquals("no", String(sc.body))
        assertEquals("text/plain", sc.contentType)
        assertEquals(listOf("rule-1"), ctx.appliedRuleIds)
        assertEquals(500, ctx.status)
        assertEquals(3, ctx.requestBody?.size)
        assertEquals(5, ctx.responseBody?.size)
        // mutate surfaces
        ctx.status = 302
        assertEquals(302, ctx.status)
        ctx.host = "other"
        assertEquals("other", ctx.host)
    }
}

class MitmRewriteInterceptorTest {

    private fun rule(id: String, vararg actions: com.ultra.trafficagent.transform.RuleAction) =
        com.ultra.trafficagent.transform.RewriteRule(
            id = id, name = id,
            match = com.ultra.trafficagent.transform.RuleMatch(hostRegex = "h\\.io"),
            actions = actions.toList(),
        )

    @Test
    fun `on request applies request-phase rules and delays`() {
        val registry = com.ultra.trafficagent.transform.RuleRegistry()
        registry.add(
            rule(
                "r1",
                com.ultra.trafficagent.transform.RuleAction.SetHeader(
                    com.ultra.trafficagent.transform.Phase.REQUEST, "X-Rewritten", "yes",
                ),
                com.ultra.trafficagent.transform.RuleAction.DelayMs(80),
            ),
        )
        val interceptor = MitmRewriteInterceptor(registry)
        val ctx = MutableProxyExchange(
            scheme = "http", host = "h.io", port = 80, method = "POST", path = "/submit",
        )
        ctx.requestHeaders.add("content-length", "0")
        ctx.requestBody = "abc".toByteArray()
        val t0 = System.nanoTime()
        val decision = interceptor.onRequest(ctx)
        val elapsedMs = (System.nanoTime() - t0) / 1_000_000
        assertTrue(decision is ProxyDecision.Forward)
        assertTrue(elapsedMs >= 70, "delay observed")
        assertEquals("yes", ctx.requestHeaders.get("x-rewritten"))
        assertEquals("POST", ctx.method)
        assertTrue("r1" in ctx.appliedRuleIds)
        assertEquals("abc", String(ctx.requestBody!!))
    }

    @Test
    fun `on response applies response-phase rules`() {
        val registry = com.ultra.trafficagent.transform.RuleRegistry()
        registry.add(
            rule(
                "r2",
                com.ultra.trafficagent.transform.RuleAction.ReplaceBody(
                    com.ultra.trafficagent.transform.Phase.RESPONSE, "world", "universe", 1,
                ),
            ),
        )
        val interceptor = MitmRewriteInterceptor(registry)
        val ctx = MutableProxyExchange(
            scheme = "http", host = "h.io", port = 80, method = "GET", path = "/",
        )
        ctx.status = 200
        ctx.responseHeaders.add("content-type", "text/plain")
        ctx.responseBody = "hello world".toByteArray()
        interceptor.onResponse(ctx)
        assertEquals("hello universe", String(ctx.responseBody!!))
        assertEquals(200, ctx.status)
        assertTrue("r2" in ctx.appliedRuleIds)
    }

    @Test
    fun `non matching rules leave the exchange untouched`() {
        val registry = com.ultra.trafficagent.transform.RuleRegistry()
        registry.add(
            com.ultra.trafficagent.transform.RewriteRule(
                id = "r3", name = "other host",
                match = com.ultra.trafficagent.transform.RuleMatch(hostRegex = "elsewhere\\.net"),
                actions = listOf(
                    com.ultra.trafficagent.transform.RuleAction.SetHeader(
                        com.ultra.trafficagent.transform.Phase.REQUEST, "X-X", "1",
                    ),
                ),
            ),
        )
        val interceptor = MitmRewriteInterceptor(registry)
        val ctx = MutableProxyExchange(
            scheme = "http", host = "h.io", port = 80, method = "GET", path = "/",
        )
        interceptor.onRequest(ctx)
        interceptor.onResponse(ctx)
        assertNull(ctx.requestHeaders.get("x-x"))
        assertEquals(0, ctx.appliedRuleIds.size)
        assertNull(ctx.responseBody)
    }
}
