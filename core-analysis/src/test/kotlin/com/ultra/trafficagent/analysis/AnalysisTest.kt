package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class EventBusTest {

    @Test
    fun `delivers events to topic subscribers`() {
        val bus = EventBus()
        val received = mutableListOf<String>()
        bus.subscribe(Topics.CAPTURED) { received += it as String }
        bus.publish(Topics.CAPTURED, "req-1")
        bus.publish(Topics.CAPTURED, "req-2")
        assertEquals(listOf("req-1", "req-2"), received)
        assertEquals(2, bus.publishedCount)
        assertEquals(0, bus.deadEventCount)
    }

    @Test
    fun `isolation between topics`() {
        val bus = EventBus()
        val a = mutableListOf<String>()
        bus.subscribe("topic.a") { a += it as String }
        bus.publish("topic.b", "x")
        assertTrue(a.isEmpty())
        assertEquals(1, bus.deadEventCount)
    }

    @Test
    fun `unsubscribe stops delivery`() {
        val bus = EventBus()
        var calls = 0
        val sub = bus.subscribe("t") { calls++ }
        bus.publish("t", 1)
        sub.cancel()
        bus.publish("t", 2)
        bus.publish("t", 3)
        assertEquals(1, calls)
        assertEquals(0, bus.subscriberCount("t"))
    }

    @Test
    fun `double cancel is safe`() {
        val bus = EventBus()
        val sub = bus.subscribe("t") { }
        sub.cancel()
        sub.cancel()
        assertEquals(0, bus.subscriberCount("t"))
    }

    @Test
    fun `same lambda subscribed twice receives twice`() {
        val bus = EventBus()
        var calls = 0
        val handler: (Any) -> Unit = { calls++ }
        bus.subscribe("t", handler)
        bus.subscribe("t", handler)
        bus.publish("t", "e")
        assertEquals(2, calls)
        assertEquals(2, bus.subscriberCount("t"))
    }

    @Test
    fun `empty topic rejected`() {
        val bus = EventBus()
        org.junit.jupiter.api.assertThrows<IllegalArgumentException> {
            bus.subscribe("") { }
        }
    }

    @Test
    fun `concurrent publish and subscribe stays consistent`() {
        val bus = EventBus()
        val writers = (1..4).map { id ->
            Thread {
                repeat(200) { bus.publish("c.topic", "$id-$it") }
            }
        }
        writers.forEach { it.start() }
        var handled = 0
        val sub = bus.subscribe("c.topic") { handled++ }
        writers.forEach { it.join() }
        sub.cancel()
        assertEquals(800, bus.publishedCount)
        assertTrue(handled <= 800) // unsubscribed mid-flight may miss some
    }
}

class TrafficStatsTest {

    private fun req(
        id: Long, host: String, up: Long, down: Long,
        proto: Protocol = Protocol.HTTP1, ts: Long = 1000, uid: Int? = 10,
    ) = CapturedRequest(
        id = id, timestampMs = ts, host = host, path = "/p", method = "GET",
        status = 200, requestHeaders = emptyMap(), responseHeaders = emptyMap(),
        requestBody = "", responseBody = "", bytesUp = up, bytesDown = down,
        protocol = proto, appUid = uid,
    )

    @Test
    fun `aggregates per host and sorts by total bytes`() {
        val stats = TrafficStats()
        stats.record(req(1, "a.com", 100, 900))
        stats.record(req(2, "a.com", 50, 50))
        stats.record(req(3, "b.io", 10, 10))
        val top = stats.topHosts(2)
        assertEquals(listOf("a.com", "b.io"), top.map { it.host })
        assertEquals(2, top[0].requests)
        assertEquals(1100L, top[0].totalBytes)
    }

    @Test
    fun `totals and protocol mix`() {
        val stats = TrafficStats()
        stats.record(req(1, "a.com", 100, 900))
        stats.record(req(2, "b.io", 1, 1, proto = Protocol.TLS))
        assertEquals(2, stats.totalRequests())
        assertEquals(101L, stats.totalBytesUp())
        assertEquals(901L, stats.totalBytesDown())
        assertEquals(mapOf(Protocol.HTTP1 to 1, Protocol.TLS to 1), stats.protocolCounts())
    }

    @Test
    fun `app shares are fractions of requests`() {
        val stats = TrafficStats()
        stats.record(req(1, "a.com", 1, 1, uid = 1))
        stats.record(req(2, "a.com", 1, 1, uid = 1))
        stats.record(req(3, "a.com", 1, 1, uid = 2))
        val shares = stats.appShares()
        assertEquals(2.0 / 3.0, shares[1]!!, 1e-9)
        assertEquals(1.0 / 3.0, shares[2]!!, 1e-9)
    }

    @Test
    fun `bandwidth uses observation span`() {
        val stats = TrafficStats()
        stats.record(req(1, "a.com", 100, 100, ts = 0))
        stats.record(req(2, "a.com", 100, 100, ts = 2000))
        // 400 bytes = 3200 bits over 2 seconds
        assertEquals(1600.0, stats.bandwidthBps(), 1e-6)
    }

    @Test
    fun `bandwidth falls back for single sample`() {
        val stats = TrafficStats()
        stats.record(req(1, "a.com", 125, 125, ts = 500))
        // 250 bytes = 2000 bits over 1000 ms fallback window
        assertEquals(2000.0, stats.bandwidthBps(fallbackWindowMs = 1000), 1e-6)
    }

    @Test
    fun `empty stats are zero`() {
        val stats = TrafficStats()
        assertEquals(0, stats.totalRequests())
        assertEquals(0.0, stats.bandwidthBps(), 0.0)
        assertNull(stats.firstTimestamp())
        assertTrue(stats.hostStats().isEmpty())
        assertTrue(stats.appShares().isEmpty())
    }

    @Test
    fun `reset clears everything`() {
        val stats = TrafficStats()
        stats.record(req(1, "a.com", 1, 1))
        stats.reset()
        assertEquals(0, stats.totalRequests())
        assertNull(stats.hostStat("a.com"))
    }
}

class TimelineIndexTest {

    private fun req(id: Long, ts: Long) = CapturedRequest(
        id = id, timestampMs = ts, host = "h", path = "/$id", method = "GET",
        status = 200, requestHeaders = emptyMap(), responseHeaders = emptyMap(),
        requestBody = "", responseBody = "", bytesUp = 0, bytesDown = 0,
        protocol = Protocol.HTTP1, appUid = null,
    )

    @Test
    fun `buckets by second`() {
        val index = TimelineIndex()
        index.add(req(1, 1700000000000))
        index.add(req(2, 1700000000999))
        index.add(req(3, 1700000001000))
        assertEquals(2, index.bucketCount())
        assertEquals(2, index.requestsInSecond(1700000000).size)
        assertEquals(1, index.requestsInSecond(1700000001).size)
        assertEquals(3, index.totalCount())
    }

    @Test
    fun `range query is inclusive`() {
        val index = TimelineIndex()
        index.add(req(1, 1000))
        index.add(req(2, 1500))
        index.add(req(3, 2500))
        val out = index.requestsIn(1000, 2000)
        assertEquals(listOf(1L, 2L), out.map { it.id })
        assertEquals(2, index.countIn(1000, 2000))
    }

    @Test
    fun `empty and inverted ranges`() {
        val index = TimelineIndex()
        index.add(req(1, 1000))
        assertTrue(index.requestsIn(2000, 1000).isEmpty())
        assertTrue(index.requestsIn(5000, 6000).isEmpty())
    }

    @Test
    fun `peak detection`() {
        val index = TimelineIndex()
        index.add(req(1, 1000))
        index.add(req(2, 1000))
        index.add(req(3, 1000))
        index.add(req(4, 2000))
        assertEquals(1L, index.peakSecond())
        assertEquals(3, index.peakCount())
    }

    @Test
    fun `empty index has no peak`() {
        val index = TimelineIndex()
        assertNull(index.peakSecond())
        assertEquals(0, index.peakCount())
    }
}

class DiffEngineTest {

    private fun req(
        id: Long, method: String = "GET", host: String = "a.com", path: String = "/x",
        status: Int? = 200, reqHeaders: Map<String, String> = mapOf("Accept" to "json"),
        respHeaders: Map<String, String> = mapOf("Content-Type" to "application/json"),
        body: String = "", respBody: String = "data",
        proto: Protocol = Protocol.HTTP1,
    ) = CapturedRequest(
        id = id, timestampMs = 0, host = host, path = path, method = method,
        status = status, requestHeaders = reqHeaders, responseHeaders = respHeaders,
        requestBody = body, responseBody = respBody, bytesUp = 10, bytesDown = 20,
        protocol = proto, appUid = null,
    )

    @Test
    fun `identical captures report no differences`() {
        val a = listOf(req(1), req(2, path = "/y"))
        val b = listOf(req(3), req(4, path = "/y"))
        val report = DiffEngine().diff(a, b)
        assertTrue(report.isIdentical)
        assertEquals(0, report.changeScore)
    }

    @Test
    fun `detects added and removed requests`() {
        val base = listOf(req(1, path = "/keep"), req(2, path = "/gone"))
        val cand = listOf(req(3, path = "/keep"), req(4, path = "/new"))
        val report = DiffEngine().diff(base, cand)
        assertEquals(1, report.added.size)
        assertEquals("/new", report.added[0].path)
        assertEquals(1, report.removed.size)
        assertEquals("/gone", report.removed[0].path)
        assertEquals(2, report.changeScore)
        assertFalse(report.isIdentical)
    }

    @Test
    fun `detects status change`() {
        val report = DiffEngine().diff(listOf(req(1)), listOf(req(2, status = 304)))
        val diff = report.changed.single()
        val change = diff.changes.single()
        assertEquals("status", change.key)
        assertEquals("200", change.before)
        assertEquals("304", change.after)
    }

    @Test
    fun `detects header changes case-insensitively`() {
        val report = DiffEngine().diff(
            listOf(req(1, respHeaders = mapOf("Content-Type" to "application/json"))),
            listOf(req(2, respHeaders = mapOf("content-type" to "text/html"))),
        )
        val change = report.changed.single().changes.single()
        assertEquals("response.header[content-type]", change.key)
        assertEquals("application/json", change.before)
        assertEquals("text/html", change.after)
    }

    @Test
    fun `detects added and removed headers`() {
        val report = DiffEngine().diff(
            listOf(req(1, reqHeaders = mapOf("Accept" to "json", "X-Old" to "1"))),
            listOf(req(2, reqHeaders = mapOf("accept" to "json", "X-New" to "2"))),
        )
        val keys = report.changed.single().changes.map { it.key }.sorted()
        assertEquals(listOf("request.header[x-new]", "request.header[x-old]"), keys)
    }

    @Test
    fun `detects body length and protocol changes`() {
        val report = DiffEngine().diff(
            listOf(req(1, respBody = "short", proto = Protocol.HTTP1)),
            listOf(req(2, respBody = "much longer body", proto = Protocol.HTTP2)),
        )
        val keys = report.changed.single().changes.map { it.key }.sorted()
        assertEquals(listOf("protocol", "responseBody.length"), keys)
    }

    @Test
    fun `duplicate keys pair in order`() {
        val base = listOf(req(1, path = "/dup"), req(2, path = "/dup"))
        val cand = listOf(req(3, path = "/dup"), req(4, path = "/dup"), req(5, path = "/dup"))
        val report = DiffEngine().diff(base, cand)
        assertEquals(1, report.added.size)
        assertEquals(0, report.removed.size)
        assertEquals(0, report.changed.size)
    }

    @Test
    fun `empty baseline means everything added`() {
        val report = DiffEngine().diff(emptyList(), listOf(req(1)))
        assertEquals(1, report.added.size)
        assertEquals(0, report.removed.size)
        assertFalse(report.isIdentical)
    }

    @Test
    fun `report carries labels`() {
        val report = DiffEngine().diff(listOf(req(1)), emptyList(), "run-1", "run-2")
        assertEquals("run-1", report.baselineLabel)
        assertEquals("run-2", report.candidateLabel)
        assertEquals(1, report.removed.size)
    }
}
