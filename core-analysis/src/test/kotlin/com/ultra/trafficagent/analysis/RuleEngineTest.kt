package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RuleEngineTest {

    private fun request(
        host: String = "api.example.com",
        path: String = "/v1/data",
        method: String = "GET",
        status: Int? = 200,
        bytesUp: Long = 500,
        bytesDown: Long = 5_000,
        durationMs: Long? = 120,
        protocol: Protocol = Protocol.HTTP1,
        mime: String? = "application/json",
        uid: Int? = 10085,
        ja3: String? = null,
        error: String? = null,
    ) = CapturedRequest(
        id = 1L,
        timestampMs = 0L,
        host = host,
        path = path,
        method = method,
        status = status,
        requestHeaders = emptyMap(),
        responseHeaders = emptyMap(),
        requestBody = "",
        responseBody = "",
        bytesUp = bytesUp,
        bytesDown = bytesDown,
        protocol = protocol,
        appUid = uid,
        ja3 = ja3,
        responseMime = mime,
        durationMs = durationMs,
        error = error,
    )

    @Test
    fun `empty rule set allows everything`() {
        val d = RuleSet.EMPTY.evaluate(request())
        assertEquals(RuleAction.ALLOW, d.action)
        assertNull(d.matchedRule)
        assertFalse(d.redact)
        assertTrue(d.tags.isEmpty())
    }

    @Test
    fun `block rule with host regex`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "block-ads",
                    action = RuleAction.BLOCK,
                    condition = fieldCond(RuleField.HOST, RuleOp.MATCHES, "doubleclick\\.net$"),
                ),
            ),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(request(host = "ad.doubleclick.net")).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(request(host = "example.com")).action)
    }

    @Test
    fun `priority ordering highest wins`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "low",
                    priority = 1,
                    action = RuleAction.BLOCK,
                    condition = fieldCond(RuleField.HOST, RuleOp.CONTAINS, "example"),
                ),
                Rule(
                    name = "high",
                    priority = 100,
                    action = RuleAction.ALLOW,
                    condition = fieldCond(RuleField.HOST, RuleOp.CONTAINS, "example"),
                ),
            ),
        )
        val d = rs.evaluate(request())
        assertEquals(RuleAction.ALLOW, d.action)
        assertEquals("high", d.matchedRule?.name)
    }

    @Test
    fun `disabled rules are skipped`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "off",
                    enabled = false,
                    action = RuleAction.BLOCK,
                    condition = RuleCondition.Always,
                ),
            ),
        )
        assertEquals(RuleAction.ALLOW, rs.evaluate(request()).action)
    }

    @Test
    fun `throttle rule carries rate`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "slow",
                    action = RuleAction.THROTTLE,
                    condition = fieldCond(RuleField.DURATION, RuleOp.GT, 100L),
                    throttleRateKibPerS = 256,
                ),
            ),
        )
        val d = rs.evaluate(request(durationMs = 500))
        assertEquals(RuleAction.THROTTLE, d.action)
        assertEquals(256, d.throttleRateKibPerS)
        // Below threshold: allowed.
        assertEquals(RuleAction.ALLOW, rs.evaluate(request(durationMs = 50)).action)
    }

    @Test
    fun `mock rule carries status and body`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "health",
                    action = RuleAction.MOCK,
                    condition = fieldCond(RuleField.PATH, RuleOp.EQ, "/healthz"),
                    mockStatus = 200,
                    mockBody = "ok",
                ),
            ),
        )
        val d = rs.evaluate(request(path = "/healthz"))
        assertEquals(RuleAction.MOCK, d.action)
        assertEquals(200, d.mockStatus)
        assertEquals("ok", d.mockBody)
    }

    @Test
    fun `tags accumulate across rules`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "media-tag",
                    action = RuleAction.TAG,
                    condition = fieldCond(RuleField.MIME, RuleOp.STARTS_WITH, "video/"),
                    tagName = "media",
                ),
                Rule(
                    name = "big-tag",
                    action = RuleAction.TAG,
                    condition = fieldCond(RuleField.TOTAL, RuleOp.GT, 1_000L),
                    tagName = "big",
                ),
            ),
        )
        val d = rs.evaluate(request(bytesDown = 9_000, mime = "video/mp4"))
        assertEquals(RuleAction.ALLOW, d.action)
        assertEquals(setOf("media", "big"), d.tags.toSet())
    }

    @Test
    fun `redact combines with terminal actions`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "hide-secrets",
                    action = RuleAction.REDACT,
                    condition = fieldCond(RuleField.HOST, RuleOp.CONTAINS, "bank"),
                ),
                Rule(
                    name = "cap",
                    action = RuleAction.THROTTLE,
                    condition = fieldCond(RuleField.TOTAL, RuleOp.GT, 100L),
                    throttleRateKibPerS = 64,
                ),
            ),
        )
        val d = rs.evaluate(request(host = "bank.example.com"))
        assertEquals(RuleAction.THROTTLE, d.action)
        assertTrue(d.redact)
    }

    @Test
    fun `numeric operators on status and bytes`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "err",
                    action = RuleAction.BLOCK,
                    condition = fieldCond(RuleField.STATUS, RuleOp.GTE, 500L),
                ),
                Rule(
                    name = "tiny",
                    action = RuleAction.MOCK,
                    condition = fieldCond(RuleField.TOTAL, RuleOp.LT, 100L),
                    mockStatus = 204,
                ),
            ),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(request(status = 502)).action)
        assertEquals(RuleAction.MOCK, rs.evaluate(request(status = 200, bytesUp = 10, bytesDown = 10)).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(request(status = 200, bytesUp = 1000)).action)
    }

    @Test
    fun `status in list`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "retryable",
                    action = RuleAction.TAG,
                    condition = fieldCond(RuleField.STATUS, RuleOp.IN, 500L, 502L, 503L),
                    tagName = "retry",
                ),
            ),
        )
        assertEquals(listOf("retry"), rs.evaluate(request(status = 502)).tags)
        assertTrue(rs.evaluate(request(status = 404)).tags.isEmpty())
    }

    @Test
    fun `protocol and uid fields`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "h2",
                    action = RuleAction.TAG,
                    condition = fieldCond(RuleField.PROTOCOL, RuleOp.EQ, "http2"),
                    tagName = "h2",
                ),
                Rule(
                    name = "app",
                    action = RuleAction.BLOCK,
                    condition = fieldCond(RuleField.UID, RuleOp.EQ, 10_085L),
                ),
            ),
        )
        // uid 20000: only the protocol tag fires.
        assertEquals(listOf("h2"), rs.evaluate(request(protocol = Protocol.HTTP2, uid = 20_000)).tags)
        // uid 10085: the block rule terminates before the tag rule (both
        // priority 0, "app" sorts before "h2").
        assertEquals(RuleAction.BLOCK, rs.evaluate(request(uid = 10_085)).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(request(uid = 20_000, protocol = Protocol.HTTP1)).action)
    }

    @Test
    fun `category field ties into domain classifier`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "no-ads",
                    action = RuleAction.BLOCK,
                    condition = fieldCond(RuleField.CATEGORY, RuleOp.EQ, "ads"),
                ),
            ),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(request(host = "ad.doubleclick.net")).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(request(host = "example.com")).action)
    }

    @Test
    fun `missing field satisfies only neq`() {
        val rs = RuleSet(
            listOf(
                Rule(
                    name = "no-ja3-block",
                    action = RuleAction.BLOCK,
                    condition = fieldCond(RuleField.JA3, RuleOp.EQ, "abcd"),
                ),
                Rule(
                    name = "no-ja3-tag",
                    action = RuleAction.TAG,
                    condition = fieldCond(RuleField.JA3, RuleOp.NEQ, "abcd"),
                    tagName = "plain",
                ),
            ),
        )
        val d = rs.evaluate(request(ja3 = null))
        // EQ on a missing field is false; NEQ is true.
        assertEquals(RuleAction.ALLOW, d.action)
        assertEquals(listOf("plain"), d.tags)
    }

    @Test
    fun `boolean condition tree`() {
        val cond = RuleCondition.Or(
            RuleCondition.And(
                fieldCond(RuleField.HOST, RuleOp.CONTAINS, "api"),
                fieldCond(RuleField.METHOD, RuleOp.EQ, "POST"),
            ),
            RuleCondition.Not(fieldCond(RuleField.STATUS, RuleOp.LTE, 299L)),
        )
        val rs = RuleSet(listOf(Rule(name = "complex", action = RuleAction.BLOCK, condition = cond)))

        // api + POST -> first branch
        assertEquals(RuleAction.BLOCK, rs.evaluate(request(method = "POST")).action)
        // api + GET, status 200 -> false or not(false) -> allow
        assertEquals(RuleAction.ALLOW, rs.evaluate(request(method = "GET", status = 200)).action)
        // other host, status 500 -> second branch (not <=299)
        assertEquals(RuleAction.BLOCK, rs.evaluate(request(host = "other.com", status = 500)).action)
    }

    @Test
    fun `rule validation rejects bad params`() {
        assertThrows(IllegalArgumentException::class.java) {
            Rule("t1", action = RuleAction.THROTTLE, condition = RuleCondition.Always)
        }
        assertThrows(IllegalArgumentException::class.java) {
            Rule("t2", action = RuleAction.MOCK, condition = RuleCondition.Always, mockStatus = 42)
        }
        assertThrows(IllegalArgumentException::class.java) {
            Rule("t3", action = RuleAction.TAG, condition = RuleCondition.Always)
        }
        assertThrows(IllegalArgumentException::class.java) {
            Rule("", action = RuleAction.BLOCK, condition = RuleCondition.Always)
        }
    }
}

class RuleDslParserTest {

    private fun req(
        host: String = "api.example.com",
        path: String = "/v1/x",
        status: Int? = 200,
        method: String = "GET",
        durationMs: Long? = 100,
        bytesDown: Long = 1_000,
        mime: String? = null,
    ): CapturedRequest = CapturedRequest(
        id = 1, timestampMs = 0, host = host, path = path, method = method, status = status,
        requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
        responseBody = "", bytesUp = 100, bytesDown = bytesDown, protocol = Protocol.HTTP1,
        appUid = null, responseMime = mime, durationMs = durationMs,
    )

    @Test
    fun `parses a simple block rule`() {
        val rs = RuleDslParser.parse(
            """
            rule block-ads
              when host contains "doubleclick"
              then block
            """.trimIndent(),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(req(host = "ad.doubleclick.net")).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(req(host = "example.com")).action)
    }

    @Test
    fun `parses priority and disabled modifiers`() {
        val rs = RuleDslParser.parse(
            """
            rule a priority 10 when true then block
            rule b priority 100 disabled when true then allow
            """.trimIndent(),
        )
        // b disabled -> a (block) wins.
        assertEquals(RuleAction.BLOCK, rs.evaluate(req()).action)
    }

    @Test
    fun `parses or and and expressions`() {
        val rs = RuleDslParser.parse(
            """
            rule combo
              when (host = "a.com" or host = "b.com") and status = 500
              then block
            """.trimIndent(),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(req(host = "a.com", status = 500)).action)
        assertEquals(RuleAction.BLOCK, rs.evaluate(req(host = "b.com", status = 500)).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(req(host = "a.com", status = 200)).action)
        assertEquals(RuleAction.ALLOW, rs.evaluate(req(host = "c.com", status = 500)).action)
    }

    @Test
    fun `parses not expression`() {
        val rs = RuleDslParser.parse(
            """
            rule notads
              when not category = ads
              then tag name=clean
            """.trimIndent(),
        )
        assertEquals(listOf("clean"), rs.evaluate(req(host = "example.com")).tags)
        assertTrue(rs.evaluate(req(host = "ad.doubleclick.net")).tags.isEmpty())
    }

    @Test
    fun `parses throttle with rate param`() {
        val rs = RuleDslParser.parse(
            """
            rule slow
              when duration > 50
              then throttle rate=128
            """.trimIndent(),
        )
        val d = rs.evaluate(req(durationMs = 200))
        assertEquals(RuleAction.THROTTLE, d.action)
        assertEquals(128, d.throttleRateKibPerS)
    }

    @Test
    fun `parses mock with status and body params`() {
        val rs = RuleDslParser.parse(
            """
            rule health
              when path = "/healthz"
              then mock status=503 body="down\nfor\nmaintenance"
            """.trimIndent(),
        )
        val d = rs.evaluate(req(path = "/healthz"))
        assertEquals(RuleAction.MOCK, d.action)
        assertEquals(503, d.mockStatus)
        assertEquals("down\nfor\nmaintenance", d.mockBody)
    }

    @Test
    fun `parses in-list values`() {
        val rs = RuleDslParser.parse(
            """
            rule retryable
              when status in 500,502,503
              then tag name=retry
            """.trimIndent(),
        )
        assertEquals(listOf("retry"), rs.evaluate(req(status = 503)).tags)
        assertTrue(rs.evaluate(req(status = 404)).tags.isEmpty())
    }

    @Test
    fun `parses method in list with bare idents`() {
        val rs = RuleDslParser.parse(
            """
            rule writes
              when method in POST,PUT,PATCH
              then tag name=write
            """.trimIndent(),
        )
        assertEquals(listOf("write"), rs.evaluate(req(method = "PUT")).tags)
        assertTrue(rs.evaluate(req(method = "GET")).tags.isEmpty())
    }

    @Test
    fun `comments are ignored`() {
        val rs = RuleDslParser.parse(
            """
            # policy: block trackers
            rule trackers
              when category = tracker # tracker domains
              then block
            # end of file
            """.trimIndent(),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(req(host = "sdk.appsflyer.com")).action)
    }

    @Test
    fun `string escapes roundtrip`() {
        val rs = RuleDslParser.parse(
            """
            rule esc
              when path = "/a\"b"
              then block
            """.trimIndent(),
        )
        assertEquals(RuleAction.BLOCK, rs.evaluate(req(path = "/a\"b")).action)
    }

    @Test
    fun `regex matches operator`() {
        val rs = RuleDslParser.parse(
            """
            rule cn-sites
              when host matches ".*\\.cn$"
              then tag name=cn
            """.trimIndent(),
        )
        assertEquals(listOf("cn"), rs.evaluate(req(host = "www.example.cn")).tags)
        assertTrue(rs.evaluate(req(host = "example.com")).tags.isEmpty())
    }

    @Test
    fun `malformed rules throw with context`() {
        assertThrows(IllegalArgumentException::class.java) {
            RuleDslParser.parse("rule x when host then block")
        }
        assertThrows(IllegalArgumentException::class.java) {
            RuleDslParser.parse("rule x when (host = \"a\" then block")
        }
        assertThrows(IllegalArgumentException::class.java) {
            RuleDslParser.parse("nonsense")
        }
        assertThrows(IllegalArgumentException::class.java) {
            RuleDslParser.parse("rule x when true then throttle rate=abc")
        }
        assertThrows(IllegalArgumentException::class.java) {
            RuleDslParser.parse("rule x when true then mock status=42")
        }
    }

    @Test
    fun `multiple rules evaluate in priority order`() {
        val rs = RuleDslParser.parse(
            """
            rule catch-all priority 20 when true then tag name=seen
            rule block-slow priority 10
              when duration > 50 and host contains "api"
              then block
            """.trimIndent(),
        )
        val d = rs.evaluate(req(host = "api.example.com", durationMs = 500))
        assertEquals(RuleAction.BLOCK, d.action)
        // The higher-priority tag rule fired before the terminal block.
        assertEquals(listOf("seen"), d.tags)
    }

    @Test
    fun `starts_with and ends_with operators`() {
        val rs = RuleDslParser.parse(
            """
            rule media
              when mime starts_with "video/"
              then tag name=media
            rule api-path
              when path ends_with ".json"
              then tag name=json
            """.trimIndent(),
        )
        assertEquals(listOf("media"), rs.evaluate(req(mime = "video/mp4")).tags)
        assertEquals(listOf("json"), rs.evaluate(req(path = "/v1/list.json")).tags)
    }
}
