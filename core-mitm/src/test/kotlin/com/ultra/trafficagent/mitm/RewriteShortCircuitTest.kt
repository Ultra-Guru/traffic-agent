package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.transform.Phase
import com.ultra.trafficagent.transform.RuleAction
import com.ultra.trafficagent.transform.RuleMatch
import com.ultra.trafficagent.transform.RuleRegistry
import com.ultra.trafficagent.transform.RewriteRule
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.nio.charset.StandardCharsets

/**
 * Request-phase short-circuit semantics of [MitmRewriteInterceptor]: Block /
 * MockResponse / Abort must answer the client locally — the origin is never
 * contacted (regression: the pre-0.5 pipeline always returned Forward).
 */
class RewriteShortCircuitTest {

    private fun ctx(host: String, path: String = "/x") = MutableProxyExchange(
        scheme = "https",
        host = host,
        port = 443,
        method = "GET",
        path = path,
    )

    @Test
    fun `block rule answers locally with its status`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "block", name = "block", priority = 10,
                match = RuleMatch(hostRegex = "ads\\.example\\.net"),
                actions = listOf(RuleAction.Block(403, "nope")),
            ),
        )
        val decision = MitmRewriteInterceptor(registry, maxDelayMs = 100).onRequest(ctx("ads.example.net"))
        assertTrue(decision is ProxyDecision.ShortCircuit)
        decision as ProxyDecision.ShortCircuit
        assertEquals(403, decision.status)
        assertEquals("nope", decision.body.toString(StandardCharsets.UTF_8))
    }

    @Test
    fun `mock rule serves the canned body`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "mock", name = "mock", priority = 10,
                match = RuleMatch(hostRegex = "api\\.example\\.com"),
                actions = listOf(RuleAction.MockResponse(201, "{\"ok\":true}", "application/json")),
            ),
        )
        val decision = MitmRewriteInterceptor(registry, maxDelayMs = 100).onRequest(ctx("api.example.com"))
        assertTrue(decision is ProxyDecision.ShortCircuit)
        decision as ProxyDecision.ShortCircuit
        assertEquals(201, decision.status)
        assertEquals("application/json", decision.contentType)
        assertEquals("{\"ok\":true}", decision.body.toString(StandardCharsets.UTF_8))
    }

    @Test
    fun `abort rule simulates an upstream timeout`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "abort", name = "abort", priority = 10,
                match = RuleMatch(hostRegex = "slow\\.example\\.com"),
                actions = listOf(RuleAction.Abort(120)),
            ),
        )
        val started = System.currentTimeMillis()
        val decision = MitmRewriteInterceptor(registry, maxDelayMs = 1_000).onRequest(ctx("slow.example.com"))
        val elapsed = System.currentTimeMillis() - started
        assertTrue(decision is ProxyDecision.ShortCircuit)
        decision as ProxyDecision.ShortCircuit
        assertEquals(504, decision.status)
        assertTrue(elapsed >= 100)  // the simulated hang actually happened
    }

    @Test
    fun `non-matching rules forward to the origin`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "block", name = "block", priority = 10,
                match = RuleMatch(hostRegex = "ads\\.example\\.net"),
                actions = listOf(RuleAction.Block(403, "nope")),
            ),
        )
        val decision = MitmRewriteInterceptor(registry).onRequest(ctx("ok.example.com"))
        assertTrue(decision is ProxyDecision.Forward)
    }

    @Test
    fun `request rewrites are copied into the context`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "edit", name = "edit", priority = 10,
                match = RuleMatch(hostRegex = "api\\.example\\.com"),
                actions = listOf(
                    RuleAction.SetHeader(Phase.REQUEST, "Authorization", "Bearer tok"),
                    RuleAction.ReplaceQueryParam("env", "staging"),
                ),
            ),
        )
        val context = ctx("api.example.com", path = "/data?env=prod")
        val decision = MitmRewriteInterceptor(registry).onRequest(context)
        assertTrue(decision is ProxyDecision.Forward)
        assertEquals("Bearer tok", context.requestHeaders.get("Authorization"))
        assertEquals("/data?env=staging", context.path)
        assertEquals(listOf("edit"), context.appliedRuleIds)
    }
}
