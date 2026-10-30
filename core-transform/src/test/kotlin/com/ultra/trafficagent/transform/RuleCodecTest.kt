package com.ultra.trafficagent.transform

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RuleCodecTest {

    private fun sampleRules(): List<RewriteRule> = listOf(
        RewriteRule(
            id = "block-ads", name = "Block ad trackers", enabled = true, priority = 90,
            match = RuleMatch(hostRegex = "(ads|tracker)\\.net", methods = setOf("GET", "POST")),
            actions = listOf(
                RuleAction.SetStatus(403),
                RuleAction.SetHeader(Phase.RESPONSE, "x-blocked-by", "traffic-agent"),
            ),
        ),
        RewriteRule(
            id = "rewrite-body", name = "Body rewrite", enabled = false, priority = 10,
            match = RuleMatch(
                hostRegex = "api\\.example\\.com",
                pathRegex = "^/v1/",
                headerEquals = mapOf("x-env" to "staging"),
            ),
            actions = listOf(
                RuleAction.ReplaceBody(Phase.RESPONSE, "old", "new", 3),
                RuleAction.DelayMs(250),
                RuleAction.Abort(1500),
            ),
        ),
        RewriteRule(
            id = "map-remote", name = "Map to staging", priority = 5,
            match = RuleMatch(pathRegex = "^/mirror"),
            actions = listOf(
                RuleAction.MapRemote("staging.example.com", 8443, keepHostHeader = true),
                RuleAction.ReplaceQueryParam("env", "staging"),
                RuleAction.MockResponse(201, "{\"ok\":true}", "application/json"),
                RuleAction.Block(418, "teapot"),
                RuleAction.Redirect("other.example.com", "/x"),
                RuleAction.RemoveHeader(Phase.REQUEST, "cookie"),
            ),
        ),
    )

    @Test
    fun `rulepack round trip preserves every rule`() {
        val text = RuleCodec.encodeRulepack(sampleRules())
        val decoded = RuleCodec.decodeRulepack(text)
        assertEquals(sampleRules(), decoded)
    }

    @Test
    fun `single rule round trip`() {
        val rule = sampleRules()[0]
        val decoded = RuleCodec.decodeRule(RuleCodec.encodeRule(rule), 0)
        assertEquals(rule, decoded)
    }

    @Test
    fun `encoded document contains readable fields`() {
        val text = RuleCodec.encodeRulepack(sampleRules())
        assertTrue(text.contains("\"version\":1"))
        assertTrue(text.contains("\"block-ads\""))
        assertTrue(text.contains("\"type\":\"setStatus\""))
        assertTrue(text.contains("\"type\":\"mapRemote\""))
        assertTrue(text.contains("\"keepHostHeader\":true"))
    }

    @Test
    fun `decode assigns ids to id-less imported rules`() {
        val text = """
            {"version":1,"rules":[
              {"name":"no id","match":{"host":"a.com"},
               "actions":[{"type":"setStatus","code":500}]}
            ]}
        """.trimIndent()
        val decoded = RuleCodec.decodeRulepack(text)
        assertEquals(1, decoded.size)
        assertEquals("imported-0", decoded[0].id)
        assertEquals("no id", decoded[0].name)
    }

    @Test
    fun `decode rejects newer versions`() {
        val text = """{"version":99,"rules":[]}"""
        val error = runCatching { RuleCodec.decodeRulepack(text) }.exceptionOrNull()
        assertNotNull(error)
        assertTrue(error is RuleCodec.RuleFormatException)
        assertTrue(error!!.message!!.contains("newer"))
    }

    @Test
    fun `decode rejects non-json and non-object roots`() {
        assertNotNull(runCatching { RuleCodec.decodeRulepack("not json") }.exceptionOrNull())
        assertNotNull(runCatching { RuleCodec.decodeRulepack("[1,2,3]") }.exceptionOrNull())
        assertNotNull(runCatching { RuleCodec.decodeRulepack("""{"rules":{}}""") }.exceptionOrNull())
    }

    @Test
    fun `rules without actions are dropped as malformed`() {
        val text = """
            {"version":1,"rules":[
              {"id":"empty","name":"no actions","actions":[]}
            ]}
        """.trimIndent()
        val error = runCatching { RuleCodec.decodeRulepack(text) }.exceptionOrNull()
        assertNotNull(error)
    }

    @Test
    fun `unknown action types decode to null without failing the pack`() {
        val json = MiniJson.parse(
            """{"id":"mixed","name":"mixed","actions":[
                {"type":"warpSpeed"},
                {"type":"delay","millis":10}
            ]}""",
        )
        val rule = RuleCodec.decodeRule(json, 0)
        assertNotNull(rule)
        assertEquals(1, rule!!.actions.size)
        assertEquals(RuleAction.DelayMs(10), rule.actions[0])
    }

    @Test
    fun `unicode and escapes survive the round trip`() {
        val rule = RewriteRule(
            id = "unicode", name = "中文 \"规则\" \\ 测试\n",
            match = RuleMatch(hostRegex = "例子\\.com"),
            actions = listOf(RuleAction.MockResponse(200, "体 \"body\" ✓", "text/plain")),
        )
        val decoded = RuleCodec.decodeRulepack(RuleCodec.encodeRulepack(listOf(rule)))
        assertEquals(rule, decoded[0])
    }
}

class RuleMatchOverlapTest {

    @Test
    fun `disjoint method sets never overlap`() {
        val a = RuleMatch(methods = setOf("GET"))
        val b = RuleMatch(methods = setOf("POST"))
        assertFalse(a.overlaps(b))
        assertFalse(b.overlaps(a))
    }

    @Test
    fun `same header with different values never overlap`() {
        val a = RuleMatch(headerEquals = mapOf("x-env" to "staging"))
        val b = RuleMatch(headerEquals = mapOf("X-Env" to "production"))
        assertFalse(a.overlaps(b))
    }

    @Test
    fun `disjoint literal hosts never overlap`() {
        val a = RuleMatch(hostRegex = "api\\.example\\.com")
        val b = RuleMatch(hostRegex = "cdn\\.example\\.net")
        assertFalse(a.overlaps(b))
    }

    @Test
    fun `nested literal hosts do overlap`() {
        val a = RuleMatch(hostRegex = "example\\.com")
        val b = RuleMatch(hostRegex = "api\\.example\\.com")
        assertTrue(a.overlaps(b))
        assertTrue(b.overlaps(a))
    }

    @Test
    fun `regex hosts are conservatively overlapping`() {
        val a = RuleMatch(hostRegex = "^api\\.")
        val b = RuleMatch(hostRegex = "^cdn\\.")
        // Neither is literal: sound check cannot prove disjointness.
        assertTrue(a.overlaps(b))
    }

    @Test
    fun `disjoint literal paths never overlap`() {
        val a = RuleMatch(pathRegex = "/v1/users")
        val b = RuleMatch(pathRegex = "/v2/items")
        assertFalse(a.overlaps(b))
    }

    @Test
    fun `unconstrained matches always overlap`() {
        assertTrue(RuleMatch().overlaps(RuleMatch()))
        assertTrue(RuleMatch().overlaps(RuleMatch(hostRegex = "a.com")))
    }

    @Test
    fun `findConflicts uses the real overlap check`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "a", name = "a", priority = 10,
                match = RuleMatch(pathRegex = "/v1/users", methods = setOf("GET")),
                actions = listOf(RuleAction.SetStatus(500)),
            ),
        )
        val candidate = RewriteRule(
            id = "b", name = "b", priority = 10,
            match = RuleMatch(pathRegex = "/v1/users", methods = setOf("DELETE")),
            actions = listOf(RuleAction.SetStatus(500)),
        )
        assertTrue(registry.findConflicts(candidate).isEmpty())

        val overlapping = candidate.copy(
            match = RuleMatch(pathRegex = "/v1/users", methods = setOf("GET", "DELETE")),
        )
        assertEquals(1, registry.findConflicts(overlapping).size)
    }
}

class NewActionsTest {

    private fun request(path: String = "/search?q=old&keep=1") = MutableHttpRequest(
        method = "GET", host = "example.com", path = path,
    )

    @Test
    fun `replaceQueryParam replaces an existing value`() {
        val rewriter = HttpRewriter(RuleRegistry())
        val path = rewriter.setQueryParam("/search?q=old&keep=1", "q", "new")
        assertEquals("/search?q=new&keep=1", path)
    }

    @Test
    fun `replaceQueryParam appends a missing value`() {
        val path = HttpRewriter(RuleRegistry()).setQueryParam("/items", "page", "2")
        assertEquals("/items?page=2", path)
    }

    @Test
    fun `replaceQueryParam keeps the fragment`() {
        val path = HttpRewriter(RuleRegistry()).setQueryParam("/a?x=1#frag", "x", "2")
        assertEquals("/a?x=2#frag", path)
    }

    @Test
    fun `replaceQueryParam url-encodes special characters`() {
        val path = HttpRewriter(RuleRegistry()).setQueryParam("/a", "q", "a b&c")
        assertEquals("/a?q=a%20b%26c", path)
    }

    @Test
    fun `mapRemote rewrites host port and host header`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "map", name = "map", priority = 10,
                match = RuleMatch(hostRegex = "example\\.com"),
                actions = listOf(RuleAction.MapRemote("staging.example.com", 8443)),
            ),
        )
        val exchange = MutableExchange(request())
        val result = HttpRewriter(registry).applyTo(exchange)
        assertEquals(listOf("map"), result.appliedRuleIds)
        assertEquals("staging.example.com", exchange.request.host)
        assertEquals(8443, exchange.request.port)
        assertEquals("staging.example.com", exchange.request.header("host"))
    }

    @Test
    fun `mapRemote keepHostHeader preserves the original host header`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "map", name = "map", priority = 10,
                match = RuleMatch(hostRegex = "example\\.com"),
                actions = listOf(RuleAction.MapRemote("staging.example.com", keepHostHeader = true)),
            ),
        )
        val exchange = MutableExchange(request())
        HttpRewriter(registry).applyTo(exchange)
        assertEquals("staging.example.com", exchange.request.host)
        assertEquals("example.com", exchange.request.header("host"))
    }

    @Test
    fun `hit counters accumulate per rule`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "hit-me", name = "hit", priority = 10,
                match = RuleMatch(hostRegex = "example\\.com"),
                actions = listOf(RuleAction.SetStatus(200)),
            ),
        )
        val rewriter = HttpRewriter(registry)
        rewriter.applyTo(MutableExchange(request()))
        rewriter.applyTo(MutableExchange(request()))
        rewriter.applyTo(MutableExchange(MutableHttpRequest("GET", "elsewhere.com", "/other")))
        assertEquals(2, registry.hitCount("hit-me"))
        assertEquals(0, registry.hitCount("nope"))
    }

    @Test
    fun `abort propagates its timeout in the result`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "kill", name = "kill", priority = 10,
                match = RuleMatch(hostRegex = "example\\.com"),
                actions = listOf(RuleAction.Abort(1234)),
            ),
        )
        val result = HttpRewriter(registry).applyTo(MutableExchange(request()))
        assertTrue(result.dropped)
        assertTrue(result.shortCircuited)
        assertEquals(1234L, result.abortTimeoutMs)
    }
}
