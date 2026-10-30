package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.transform.Phase
import com.ultra.trafficagent.transform.RuleAction
import com.ultra.trafficagent.transform.RuleMatch
import com.ultra.trafficagent.transform.RuleRegistry
import com.ultra.trafficagent.transform.RewriteRule
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.nio.charset.StandardCharsets

/** Mutation killers for mapper + interceptor + pool edge branches. */
class MutationKillerMitmTest {

    private fun exchange(
        status: Int? = 200,
        respBody: ByteArray? = "ok".toByteArray(),
        respDecoded: ByteArray? = null,
        reqBody: ByteArray? = "in".toByteArray(),
        contentType: String? = "text/plain",
    ) = ProxyExchange(
        id = 1,
        timestampMs = 123,
        scheme = "https",
        host = "h.com",
        port = 443,
        method = "POST",
        path = "/p",
        requestHeaders = listOfNotNull(
            "Content-Type" to "text/plain",
            reqBody?.let { "Content-Length" to it.size.toString() },
        ),
        requestBody = reqBody,
        status = status,
        responseHeaders = listOfNotNull(contentType?.let { "Content-Type" to it }),
        responseBody = respBody,
        responseDecodedBody = respDecoded,
        requestBytes = 10,
        responseBytes = 20,
        durationMs = 5,
        tls = true,
        appliedRuleIds = emptyList(),
        error = null,
        truncated = false,
    )

    @Test
    fun `mapper keeps raw bytes and mime for binary bodies`() {
        val png = byteArrayOf(0x89.toByte(), 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 1, 2, 3)
        val mapped = ProxyExchangeMapper.toCapturedRequest(
            exchange(respBody = png, respDecoded = null, contentType = "image/png"),
            id = 9,
        )
        assertArrayEquals(png, mapped.responseBodyBytes)
        assertArrayEquals("in".toByteArray(), mapped.requestBodyBytes)
        assertEquals("image/png", mapped.responseMime)
        assertTrue(mapped.responseBody.contains("binary body"))
        assertNull(mapped.error)
    }

    @Test
    fun `mapper prefers decoded body and empty bodies vanish`() {
        val mapped = ProxyExchangeMapper.toCapturedRequest(
            exchange(respBody = "raw".toByteArray(), respDecoded = "decoded".toByteArray()),
            id = 2,
        )
        assertEquals("decoded", mapped.responseBody)
        assertArrayEquals("decoded".toByteArray(), mapped.responseBodyBytes)
        assertEquals(7L, mapped.responseDecompressedBytes)

        val empty = ProxyExchangeMapper.toCapturedRequest(
            exchange(respBody = null, reqBody = ByteArray(0)),
            id = 3,
        )
        assertNull(empty.responseBodyBytes)
        assertNull(empty.requestBodyBytes)
        assertEquals("", empty.responseBody)
    }

    @Test
    fun `mapper sniffs text mime when header missing`() {
        val mapped = ProxyExchangeMapper.toCapturedRequest(
            exchange(respBody = """{"a":1}""".toByteArray(), contentType = null),
            id = 4,
        )
        assertEquals("application/json", mapped.responseMime)
    }

    @Test
    fun `mapper carries error duration and status-less exchanges`() {
        val mapped = ProxyExchangeMapper.toCapturedRequest(
            exchange(status = null, respBody = null).copy(error = "boom"),
            id = 5,
        )
        assertEquals("boom", mapped.error)
        assertNull(mapped.status)
        assertEquals(5L, mapped.durationMs)
    }

    @Test
    fun `bodyText round trips latin1 as binary placeholder`() {
        val binary = byteArrayOf(0xFF.toByte(), 0xFE.toByte(), 0x00, 0x01)
        assertTrue(ProxyExchangeMapper.bodyText(binary).contains("binary body"))
        assertEquals("hello", ProxyExchangeMapper.bodyText("hello".toByteArray()))
        assertEquals("", ProxyExchangeMapper.bodyText(null))
    }

    @Test
    fun `interceptor clamps delays to max`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "slow", name = "slow", priority = 10,
                match = RuleMatch(hostRegex = "slow\\.com"),
                actions = listOf(RuleAction.DelayMs(10_000)),
            ),
        )
        val started = System.currentTimeMillis()
        val decision = MitmRewriteInterceptor(registry, maxDelayMs = 150).onRequest(
            MutableProxyExchange("https", "slow.com", 443, "GET", "/"),
        )
        val elapsed = System.currentTimeMillis() - started
        assertTrue(decision is ProxyDecision.Forward)
        assertTrue(elapsed in 100..2_000)
    }

    @Test
    fun `interceptor ignores exchange errors and rewrites response body`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "fix", name = "fix", priority = 10,
                match = RuleMatch(hostRegex = "api\\.com"),
                actions = listOf(
                    RuleAction.ReplaceBody(Phase.RESPONSE, "old", "new"),
                    RuleAction.RemoveHeader(Phase.RESPONSE, "X-Junk"),
                ),
            ),
        )
        val ctx = MutableProxyExchange("https", "api.com", 443, "GET", "/x")
        ctx.status = 200
        ctx.responseHeaders.add("Content-Type", "text/plain")
        ctx.responseHeaders.add("X-Junk", "yes")
        ctx.responseBody = "old value".toByteArray()
        MitmRewriteInterceptor(registry).onResponse(ctx)
        assertEquals("new value", ctx.responseBody!!.toString(StandardCharsets.UTF_8))
        assertNull(ctx.responseHeaders.get("X-Junk"))
        assertEquals(listOf("fix"), ctx.appliedRuleIds)
    }

    @Test
    fun `interceptor onRequest copies content length only when present`() {
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "hdr", name = "hdr", priority = 10,
                match = RuleMatch(hostRegex = "api\\.com"),
                actions = listOf(RuleAction.SetHeader(Phase.REQUEST, "X-Added", "1")),
            ),
        )
        val ctx = MutableProxyExchange("https", "api.com", 443, "POST", "/x")
        ctx.requestBody = "abc".toByteArray()
        val decision = MitmRewriteInterceptor(registry).onRequest(ctx)
        assertTrue(decision is ProxyDecision.Forward)
        // No content-length in the original headers -> none synthesized.
        assertNull(ctx.requestHeaders.get("Content-Length"))
        assertEquals("1", ctx.requestHeaders.get("X-Added"))
    }

    @Test
    fun `pool releases beyond capacity close the oldest`() {
        val pool = OriginConnectionPool(
            connect = { _, _, _ -> FakeSocket() },
            maxIdlePerKey = 1,
            clock = { 0L },
        )
        val first = pool.acquire("https", "a.com", 443)
        val second = pool.acquire("https", "a.com", 443)
        val third = pool.acquire("https", "a.com", 443)
        pool.release(first, "https://a.com:443", true)
        pool.release(second, "https://a.com:443", true)
        assertEquals(1, pool.idleCount())
        // third was never released: releasing again is a plain close.
        pool.release(third, "https://a.com:443", false)
        assertEquals(1, pool.idleCount())
    }

    @Test
    fun `pool ttl boundary is inclusive`() {
        var now = 0L
        val pool = OriginConnectionPool(
            connect = { _, _, _ -> FakeSocket() },
            idleTtlMs = 10_000,
            clock = { now },
        )
        val lease = pool.acquire("https", "a.com", 443)
        pool.release(lease, "https://a.com:443", true)
        now = 10_000  // exactly the TTL: still reusable
        assertTrue(pool.acquire("https", "a.com", 443).reused)
        now = 10_001  // one past: expired
        assertFalse(pool.acquire("https", "a.com", 443).reused)
    }

    @Test
    fun `keyOf is stable per scheme host port`() {
        assertEquals("https://a.com:443", OriginConnectionPool.keyOf("https", "a.com", 443))
        assertFalse(OriginConnectionPool.keyOf("http", "a.com", 443) == OriginConnectionPool.keyOf("https", "a.com", 443))
    }
}

