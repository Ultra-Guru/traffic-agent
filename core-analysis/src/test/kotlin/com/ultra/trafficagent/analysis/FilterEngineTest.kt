package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class FilterEngineTest {

    private fun capture(
        id: Long,
        host: String = "api.weibo.cn",
        path: String = "/2/statuses/home.json",
        method: String = "GET",
        status: Int? = 200,
        body: String = "{}",
        protocol: Protocol = Protocol.HTTP2,
        bytesUp: Long = 500,
        bytesDown: Long = 20_000,
        durationMs: Long? = 120,
        uid: Int? = 10085,
        error: String? = null,
        mime: String? = "application/json",
    ) = CapturedRequest(
        id = id, timestampMs = 1_700_000_000_000 + id, host = host, path = path, method = method,
        status = status, requestHeaders = mapOf("accept" to "application/json"),
        responseHeaders = mapOf("content-type" to "application/json; charset=utf-8"),
        requestBody = "", responseBody = body, bytesUp = bytesUp, bytesDown = bytesDown,
        protocol = protocol, appUid = uid, responseMime = mime, durationMs = durationMs, error = error,
    )

    @Test
    fun `parses every dsl token`() {
        val f = CaptureFilter.parse(
            "host:weibo path:/statuses method:GET,POST status:4xx,500 mime:image/ " +
                "size>1024 size<99999 time>50 time<2000 proto:http2,tls secure:true uid:10085 error:true",
        )
        assertEquals("weibo", f.hostKeyword)
        assertEquals("/statuses", f.pathKeyword)
        assertEquals(setOf("GET", "POST"), f.methods)
        assertEquals(setOf(4), f.statusClasses)
        assertEquals(setOf(500), f.exactStatus)
        assertEquals(listOf("image/"), f.mimePrefixes)
        assertEquals(1024L, f.minBytes)
        assertEquals(99999L, f.maxBytes)
        assertEquals(50L, f.minDurationMs)
        assertEquals(2000L, f.maxDurationMs)
        assertEquals(setOf(Protocol.HTTP2, Protocol.TLS), f.protocols)
        assertTrue(f.secureOnly)
        assertEquals(setOf(10085), f.appUids)
        assertTrue(f.errorOnly)
    }

    @Test
    fun `bare word becomes host keyword`() {
        val f = CaptureFilter.parse("weibo")
        assertEquals("weibo", f.hostKeyword)
    }

    @Test
    fun `malformed tokens are rejected with the token`() {
        assertThrows(IllegalArgumentException::class.java) { CaptureFilter.parse("size>abc") }
        assertThrows(IllegalArgumentException::class.java) { CaptureFilter.parse("status:9z") }
        assertThrows(IllegalArgumentException::class.java) { CaptureFilter.parse("proto:sctp") }
        assertThrows(IllegalArgumentException::class.java) { CaptureFilter.parse("uid:xx") }
    }

    @Test
    fun `matches matrix`() {
        val target = capture(1)
        assertTrue(CaptureFilter.parse("host:weibo").matches(target))
        assertTrue(CaptureFilter.parse("weibo").matches(target))
        assertTrue(!CaptureFilter.parse("host:zhihu").matches(target))
        assertTrue(CaptureFilter.parse("method:get").matches(target)) // case-insensitive
        assertTrue(!CaptureFilter.parse("method:post").matches(target))
        assertTrue(CaptureFilter.parse("status:2xx").matches(target))
        assertTrue(!CaptureFilter.parse("status:4xx").matches(target))
        assertTrue(CaptureFilter.parse("status:200").matches(target))
        assertTrue(CaptureFilter.parse("mime:application/json").matches(target))
        assertTrue(CaptureFilter.parse("mime:application").matches(target)) // prefix match
        assertTrue(!CaptureFilter.parse("mime:image/").matches(target))
        assertTrue(CaptureFilter.parse("size>1000").matches(target)) // total = 20500
        assertTrue(!CaptureFilter.parse("size>30000").matches(target))
        assertTrue(CaptureFilter.parse("time>100").matches(target))
        assertTrue(!CaptureFilter.parse("time>300").matches(target))
        assertTrue(CaptureFilter.parse("proto:http2").matches(target))
        assertTrue(!CaptureFilter.parse("proto:dns").matches(target))
        assertTrue(CaptureFilter.parse("uid:10085").matches(target))
    }

    @Test
    fun `error only matches failures and 5xx`() {
        val ok = capture(1)
        val failed = capture(2, error = "connect timeout")
        val serverError = capture(3, status = 502)
        val f = CaptureFilter.parse("error:true")
        assertTrue(!f.matches(ok))
        assertTrue(f.matches(failed))
        assertTrue(f.matches(serverError))
    }

    @Test
    fun `filter over a list`() {
        val requests = listOf(
            capture(1, host = "a.com"),
            capture(2, host = "b.com"),
            capture(3, host = "a.io"),
        )
        assertEquals(2, CaptureFilter.parse("a").filter(requests).size)
        assertEquals(1, CaptureFilter.parse("host:b.com").filter(requests).size)
    }

    @Test
    fun `null duration counts as zero`() {
        val c = capture(1, durationMs = null)
        assertTrue(CaptureFilter.parse("time<1").matches(c))
        assertTrue(!CaptureFilter.parse("time>1").matches(c))
    }
}

class CaptureRepositoryTest {

    private fun capture(id: Long, host: String = "h.io", bytesDown: Long = 10) =
        CapturedRequest(
            id = id, timestampMs = id, host = host, path = "/p", method = "GET", status = 200,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(),
            requestBody = "", responseBody = "x", bytesUp = 1, bytesDown = bytesDown,
            protocol = Protocol.HTTP1, appUid = null,
        )

    @Test
    fun `ring buffer evicts oldest beyond capacity`() {
        val repo = CaptureRepository(capacity = 3)
        repeat(5) { repo.add(capture(it.toLong())) }
        assertEquals(3, repo.size)
        assertEquals(listOf(4L, 3L, 2L), repo.snapshot().map { it.id })
        assertEquals(null, repo.get(0))
        assertEquals(capture(2).host, repo.get(2)?.host)
    }

    @Test
    fun `apply uses the filter engine`() {
        val repo = CaptureRepository(capacity = 10)
        repo.add(capture(1, host = "a.com"))
        repo.add(capture(2, host = "b.com"))
        assertEquals(1, repo.apply(CaptureFilter.parse("host:a.com")).size)
    }

    @Test
    fun `stats aggregate everything buffered`() {
        val repo = CaptureRepository(capacity = 100)
        repeat(3) { repo.add(capture(it.toLong(), bytesDown = 100)) }
        val summary = repo.stats()
        assertEquals(3, summary.requests)
        assertEquals(303L, summary.bytesUp + summary.bytesDown)
    }

    @Test
    fun `on added callback fires and survives listener exceptions`() {
        val repo = CaptureRepository(capacity = 2)
        var seen = 0
        repo.onAdded = { if (it.id == 1L) throw IllegalStateException("boom") else seen++ }
        repo.add(capture(1))
        repo.add(capture(2))
        assertEquals(1, seen)
        assertEquals(2, repo.size)
    }

    @Test
    fun `status classes counted`() {
        val repo = CaptureRepository(capacity = 10)
        repo.add(capture(1))
        repo.add(capture(2).copy(status = 404))
        repo.add(capture(3).copy(status = 502))
        val counts = TrafficStats().apply {
            repo.snapshot().forEach { record(it) }
        }.statusClassCounts()
        assertEquals(1, counts[2])
        assertEquals(1, counts[4])
        assertEquals(1, counts[5])
    }
}

/** Full token-matrix coverage: every DSL branch gets an exercising pair. */
class FilterEngineTokenMatrixTest {

    private fun capture(
        id: Long,
        host: String = "matrix.example.com",
        path: String = "/deep/path/file.bin?k=v",
        method: String = "GET",
        status: Int? = 200,
        body: String = "needle-in-haystack",
        protocol: Protocol = Protocol.HTTP2,
        bytesUp: Long = 100,
        bytesDown: Long = 1_000,
        durationMs: Long? = 250,
        uid: Int? = 20000,
        error: String? = null,
        mime: String? = null,
    ) = CapturedRequest(
        id = id, timestampMs = id, host = host, path = path, method = method, status = status,
        requestHeaders = mapOf("Accept" to "text/html"),
        responseHeaders = mapOf("Content-Type" to "application/x-protobuf"),
        requestBody = "req-needle", responseBody = body, bytesUp = bytesUp, bytesDown = bytesDown,
        protocol = protocol, appUid = uid, responseMime = mime, durationMs = durationMs, error = error,
    )

    @Test
    fun `every positive token matches its target`() {
        val c = capture(1)
        assertTrue(CaptureFilter.parse("host:matrix.example.com").matches(c))
        assertTrue(CaptureFilter.parse("path:/deep/path").matches(c))
        assertTrue(CaptureFilter.parse("body:needle-in-haystack").matches(c))
        assertTrue(CaptureFilter.parse("method:get").matches(c))
        assertTrue(CaptureFilter.parse("status:2xx").matches(c))
        assertTrue(CaptureFilter.parse("status:200").matches(c))
        assertTrue(CaptureFilter.parse("mime:application/x-").matches(c))
        assertTrue(CaptureFilter.parse("size>1000").matches(c))   // total = 1100
        assertTrue(CaptureFilter.parse("size<2000").matches(c))
        assertTrue(CaptureFilter.parse("time>100").matches(c))   // duration 250
        assertTrue(CaptureFilter.parse("time<1000").matches(c))
        assertTrue(CaptureFilter.parse("proto:http2").matches(c))
        assertTrue(CaptureFilter.parse("proto:HTTP2").matches(c))
        assertTrue(CaptureFilter.parse("uid:20000").matches(c))
    }

    @Test
    fun `every negative token rejects its target`() {
        val c = capture(1)
        assertFalse(CaptureFilter.parse("host:other").matches(c))
        assertFalse(CaptureFilter.parse("path:/shallow").matches(c))
        assertFalse(CaptureFilter.parse("body:missing").matches(c))
        assertFalse(CaptureFilter.parse("method:post").matches(c))
        assertFalse(CaptureFilter.parse("status:3xx").matches(c))
        assertFalse(CaptureFilter.parse("status:404").matches(c))
        assertFalse(CaptureFilter.parse("mime:text/").matches(c))
        assertFalse(CaptureFilter.parse("size>5000").matches(c))
        assertFalse(CaptureFilter.parse("size<50").matches(c))
        assertFalse(CaptureFilter.parse("time>999").matches(c))
        assertFalse(CaptureFilter.parse("time<10").matches(c))
        assertFalse(CaptureFilter.parse("proto:quic").matches(c))
        assertFalse(CaptureFilter.parse("uid:1").matches(c))
        assertFalse(CaptureFilter.parse("secure:true").matches(c))
    }

    @Test
    fun `secure true matches tls captures`() {
        val tls = capture(1, protocol = Protocol.TLS)
        assertTrue(CaptureFilter.parse("secure:true").matches(tls))
        assertFalse(CaptureFilter.parse("secure:false").matches(tls))
        assertFalse(CaptureFilter.parse("secure:true").matches(capture(2)))
        assertTrue(CaptureFilter.parse("secure:false").matches(capture(2)))
    }

    @Test
    fun `error true matches transport errors and 5xx`() {
        assertTrue(CaptureFilter.parse("error:true").matches(capture(1, error = "boom")))
        assertTrue(CaptureFilter.parse("error:true").matches(capture(2, status = 503)))
        assertFalse(CaptureFilter.parse("error:true").matches(capture(3, status = 400)))
        assertFalse(CaptureFilter.parse("error:true").matches(capture(4, status = 200, error = null)))
        // optional token with non-true value is ignored rather than failing
        assertTrue(CaptureFilter.parse("error:false").matches(capture(5)))
    }

    @Test
    fun `combined query intersects every clause`() {
        val c = capture(1)
        assertTrue(CaptureFilter.parse("host:example status:2xx method:get size>500 time>100 proto:http2").matches(c))
        assertFalse(CaptureFilter.parse("host:example status:5xx").matches(c))
        assertFalse(CaptureFilter.parse("host:example status:2xx size>99999").matches(c))
    }

    @Test
    fun `mime falls back to response headers when mime field is null`() {
        val c = capture(1, mime = null)
        assertTrue(CaptureFilter.parse("mime:application/x-protobuf").matches(c))
        assertFalse(CaptureFilter.parse("mime:text/").matches(c))
    }
}
