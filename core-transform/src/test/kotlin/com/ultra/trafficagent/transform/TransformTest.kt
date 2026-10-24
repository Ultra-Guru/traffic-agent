package com.ultra.trafficagent.transform

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RuleMatchTest {

    private fun request(
        host: String = "api.example.com",
        path: String = "/v1/users",
        method: String = "GET",
        headers: Map<String, String> = emptyMap(),
    ) = MutableHttpRequest(method, host, path, headers)

    @Test
    fun `empty match accepts everything`() {
        val m = RuleMatch()
        assertTrue(m.matches(request()))
        assertTrue(m.matches(request(host = "x", path = "/", method = "POST")))
    }

    @Test
    fun `host regex filters`() {
        val m = RuleMatch(hostRegex = "example\\.com$")
        assertTrue(m.matches(request()))
        assertFalse(m.matches(request(host = "cdn.fastly.net")))
    }

    @Test
    fun `path regex filters`() {
        val m = RuleMatch(pathRegex = "^/v1/")
        assertTrue(m.matches(request(path = "/v1/items")))
        assertFalse(m.matches(request(path = "/v2/items")))
    }

    @Test
    fun `method set filters`() {
        val m = RuleMatch(methods = setOf("POST", "PUT"))
        assertTrue(m.matches(request(method = "POST")))
        assertFalse(m.matches(request(method = "GET")))
    }

    @Test
    fun `header equality is case-insensitive`() {
        val m = RuleMatch(headerEquals = mapOf("X-Api-Version" to "2"))
        assertTrue(m.matches(request(headers = mapOf("x-api-version" to "2"))))
        assertFalse(m.matches(request(headers = mapOf("x-api-version" to "3"))))
    }

    @Test
    fun `all predicates must hold`() {
        val m = RuleMatch(hostRegex = "api\\..*", methods = setOf("POST"))
        assertFalse(m.matches(request(method = "GET")))
    }
}

class MutableExchangeTest {

    @Test
    fun `headers are case-insensitive`() {
        val req = MutableHttpRequest("GET", "a.com", "/p", mapOf("X-Test" to "1"))
        assertEquals("1", req.header("x-test"))
        req.setHeader("X-TEST", "2")
        assertEquals("2", req.header("x-test"))
        req.removeHeader("x-Test")
        assertNull(req.header("X-Test"))
    }

    @Test
    fun `url composes host and path`() {
        val ex = MutableExchange(MutableHttpRequest("GET", "h.io", "/a?b=1"))
        assertEquals("https://h.io/a?b=1", ex.url)
    }
}

class RuleRegistryTest {

    private fun rule(id: String, priority: Int, host: String = "a.com", enabled: Boolean = true) =
        RewriteRule(id, "rule-$id", enabled, priority, RuleMatch(hostRegex = Regex.escape(host)))

    @Test
    fun `active rules sort by priority descending`() {
        val reg = RuleRegistry()
        reg.add(rule("low", priority = 1))
        reg.add(rule("high", priority = 10))
        reg.add(rule("mid", priority = 5))
        assertEquals(listOf("high", "mid", "low"), reg.activeRules().map { it.id })
    }

    @Test
    fun `disabled rules are excluded`() {
        val reg = RuleRegistry()
        reg.add(rule("on", 1))
        reg.add(rule("off", 5, enabled = false))
        assertEquals(listOf("on"), reg.activeRules().map { it.id })
    }

    @Test
    fun `enable and disable round trip`() {
        val reg = RuleRegistry()
        reg.add(rule("r", 1, enabled = false))
        assertTrue(reg.setEnabled("r", true))
        assertTrue(reg.activeRules().any { it.id == "r" })
        assertTrue(reg.setEnabled("r", false))
        assertTrue(reg.activeRules().isEmpty())
        assertFalse(reg.setEnabled("missing", true))
    }

    @Test
    fun `remove deletes the rule`() {
        val reg = RuleRegistry()
        reg.add(rule("r", 1))
        assertTrue(reg.remove("r"))
        assertFalse(reg.remove("r"))
        assertTrue(reg.allRules().isEmpty())
    }

    @Test
    fun `conflict detection flags close priorities`() {
        val reg = RuleRegistry()
        reg.add(rule("a", 5))
        val conflicting = rule("b", 5)
        assertEquals(1, reg.findConflicts(conflicting).size)
        val far = rule("c", 50)
        assertTrue(reg.findConflicts(far).isEmpty())
    }

    @Test
    fun `same id overwrites`() {
        val reg = RuleRegistry()
        reg.add(rule("r", 1))
        reg.add(rule("r", 9))
        assertEquals(1, reg.allRules().size)
        assertEquals(9, reg.rule("r")!!.priority)
    }
}

class HttpRewriterTest {

    private fun exchange(
        host: String = "api.example.com",
        path: String = "/v1/data",
        body: String = "{\"value\":\"original\"}",
        respBody: String = "{\"ok\":true}",
    ) = MutableExchange(
        MutableHttpRequest("GET", host, path, mapOf("Accept" to "application/json"), body),
        MutableHttpResponse(200, mapOf("Content-Type" to "application/json"), respBody),
    )

    @Test
    fun `no rules means no changes`() {
        val result = HttpRewriter(RuleRegistry()).applyTo(exchange())
        assertTrue(result.appliedRuleIds.isEmpty())
        assertTrue(result.changedFields.isEmpty())
        assertEquals(0, result.delayedByMs)
    }

    @Test
    fun `set and remove headers on both phases`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                id = "r1", name = "auth", priority = 5,
                match = RuleMatch(hostRegex = "example\\.com"),
                actions = listOf(
                    RuleAction.SetHeader(Phase.REQUEST, "Authorization", "Bearer abc"),
                    RuleAction.RemoveHeader(Phase.RESPONSE, "Server"),
                ),
            )
        )
        val ex = exchange()
        val result = HttpRewriter(reg).applyTo(ex)
        assertEquals("Bearer abc", ex.request.header("authorization"))
        assertEquals(listOf("r1"), result.appliedRuleIds)
        assertEquals(2, result.changedFields.size)
    }

    @Test
    fun `path rewrite uses regex`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                id = "rp", name = "v2 migration", priority = 1,
                match = RuleMatch(pathRegex = "^/v1/"),
                actions = listOf(RuleAction.ReplacePath("^/v1/", "/v2/")),
            )
        )
        val ex = exchange()
        HttpRewriter(reg).applyTo(ex)
        assertEquals("/v2/data", ex.request.path)
    }

    @Test
    fun `body rewrite replaces matched pattern`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                id = "rb", name = "body patch", priority = 1,
                actions = listOf(RuleAction.ReplaceBody(Phase.REQUEST, "original", "patched")),
            )
        )
        val ex = exchange()
        HttpRewriter(reg).applyTo(ex)
        assertEquals("{\"value\":\"patched\"}", ex.request.body)
    }

    @Test
    fun `redirect rewrites host and path`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                id = "rd", name = "redirect", priority = 1,
                actions = listOf(RuleAction.Redirect("mirror.example.org", "/mirror/data")),
            )
        )
        val ex = exchange()
        HttpRewriter(reg).applyTo(ex)
        assertEquals("mirror.example.org", ex.request.host)
        assertEquals("/mirror/data", ex.request.path)
    }

    @Test
    fun `set status acts on response`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                id = "st", name = "teapot", priority = 1,
                actions = listOf(RuleAction.SetStatus(418)),
            )
        )
        val ex = exchange()
        HttpRewriter(reg).applyTo(ex)
        assertEquals(418, ex.response!!.status)
    }

    @Test
    fun `delay accumulates across rules`() {
        val reg = RuleRegistry()
        reg.add(RewriteRule("d1", "delay-1", priority = 2, actions = listOf(RuleAction.DelayMs(120))))
        reg.add(RewriteRule("d2", "delay-2", priority = 1, actions = listOf(RuleAction.DelayMs(80))))
        val result = HttpRewriter(reg).applyTo(exchange())
        assertEquals(200, result.delayedByMs)
    }

    @Test
    fun `non-matching rules do not apply`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                id = "nm", name = "other host", priority = 1,
                match = RuleMatch(hostRegex = "^unrelated\\."),
                actions = listOf(RuleAction.SetStatus(500)),
            )
        )
        val ex = exchange()
        val result = HttpRewriter(reg).applyTo(ex)
        assertTrue(result.appliedRuleIds.isEmpty())
        assertEquals(200, ex.response!!.status)
    }

    @Test
    fun `higher priority runs first and lower priority sees rewritten state`() {
        val reg = RuleRegistry()
        reg.add(
            RewriteRule(
                "second", "adds marker", priority = 1,
                match = RuleMatch(pathRegex = "/staging"),
                actions = listOf(RuleAction.SetHeader(Phase.REQUEST, "X-Marker", "seen")),
            )
        )
        reg.add(
            RewriteRule(
                "first", "rewrite to staging", priority = 10,
                actions = listOf(RuleAction.ReplacePath("^/v1/", "/staging/")),
            )
        )
        val ex = exchange()
        HttpRewriter(reg).applyTo(ex)
        assertEquals("/staging/data", ex.request.path)
        assertEquals("seen", ex.request.header("x-marker"))
    }
}

class BreakpointManagerTest {

    @Test
    fun `hit creates pending breakpoint`() {
        val mgr = BreakpointManager { 1000 }
        val bp = mgr.hit("flow-1", BreakpointPhase.REQUEST)
        assertEquals(BreakpointState.PENDING, bp.state)
        assertEquals(1000, bp.createdAtMs)
        assertEquals(listOf(bp.id), mgr.pending().map { it.id })
    }

    @Test
    fun `approve then release`() {
        val mgr = BreakpointManager { 0 }
        val bp = mgr.hit("f", BreakpointPhase.REQUEST)
        assertTrue(mgr.approve(bp.id))
        assertEquals(BreakpointState.APPROVED, mgr.byId(bp.id)!!.state)
        assertTrue(mgr.release(bp.id))
        assertEquals(BreakpointState.RELEASED, mgr.byId(bp.id)!!.state)
        // released is terminal
        assertFalse(mgr.approve(bp.id))
    }

    @Test
    fun `reject is terminal`() {
        val mgr = BreakpointManager { 0 }
        val bp = mgr.hit("f", BreakpointPhase.RESPONSE)
        assertTrue(mgr.reject(bp.id))
        assertEquals(BreakpointState.REJECTED, mgr.byId(bp.id)!!.state)
        assertFalse(mgr.approve(bp.id))
        assertFalse(mgr.release(bp.id))
    }

    @Test
    fun `unknown ids are rejected`() {
        val mgr = BreakpointManager { 0 }
        assertFalse(mgr.approve(999))
        assertFalse(mgr.reject(999))
        assertFalse(mgr.release(999))
        assertNull(mgr.byId(999))
    }

    @Test
    fun `pending breakpoints expire after max age`() {
        var clock = 10_000L
        val mgr = BreakpointManager { clock }
        val bp = mgr.hit("f", BreakpointPhase.REQUEST)
        clock += 5_000
        val fresh = mgr.hit("f2", BreakpointPhase.REQUEST)
        val expired = mgr.expireDue(maxAgeMs = 3_000)
        assertEquals(listOf(bp.id), expired.map { it.id })
        assertEquals(BreakpointState.EXPIRED, mgr.byId(bp.id)!!.state)
        assertEquals(BreakpointState.PENDING, mgr.byId(fresh.id)!!.state)
    }

    @Test
    fun `expired breakpoints cannot be approved`() {
        var clock = 0L
        val mgr = BreakpointManager { clock }
        val bp = mgr.hit("f", BreakpointPhase.REQUEST)
        clock += 10_000
        mgr.expireDue(maxAgeMs = 5_000)
        assertFalse(mgr.approve(bp.id))
    }
}

class SandboxPolicyTest {

    @Test
    fun `default policy allows reads and rewrites`() {
        val e = SandboxEnforcer(SandboxPolicy.DEFAULT)
        assertTrue(e.check(SandboxOperation.READ_REQUEST).allowed)
        assertTrue(e.check(SandboxOperation.MODIFY_HEADER).allowed)
        assertTrue(e.check(SandboxOperation.SET_BREAKPOINT).allowed)
    }

    @Test
    fun `default policy denies network device and cert ops`() {
        val e = SandboxEnforcer(SandboxPolicy.DEFAULT)
        assertFalse(e.check(SandboxOperation.ACCESS_NETWORK).allowed)
        assertFalse(e.check(SandboxOperation.ACCESS_DEVICE).allowed)
        assertFalse(e.check(SandboxOperation.INSTALL_CERT).allowed)
        val decision = e.check(SandboxOperation.INSTALL_CERT)
        assertEquals("operation not allowed by sandbox policy", decision.reason)
    }

    @Test
    fun `read only policy denies writes`() {
        val e = SandboxEnforcer(SandboxPolicy.READ_ONLY)
        assertFalse(e.check(SandboxOperation.MODIFY_BODY).allowed)
        assertFalse(e.check(SandboxOperation.MODIFY_URL).allowed)
    }

    @Test
    fun `full policy allows everything`() {
        val e = SandboxEnforcer(SandboxPolicy.FULL)
        assertTrue(SandboxOperation.entries.all { e.check(it).allowed })
        assertFalse(e.networkBlocked())
    }

    @Test
    fun `timeout and memory thresholds`() {
        val e = SandboxEnforcer(SandboxPolicy.DEFAULT)
        assertFalse(e.timedOut(999))
        assertTrue(e.timedOut(1001))
        assertFalse(e.overMemory(64))
        assertTrue(e.overMemory(65))
        assertTrue(e.networkBlocked())
    }

    @Test
    fun `custom policy bounds`() {
        val e = SandboxEnforcer(
            SandboxPolicy(emptySet(), maxScriptExecutionMs = 100, maxScriptMemoryMb = 8)
        )
        assertTrue(e.timedOut(101))
        assertTrue(e.overMemory(9))
        assertFalse(e.check(SandboxOperation.READ_REQUEST).allowed)
    }
}
