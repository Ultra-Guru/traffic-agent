package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TimeSeriesStatsTest {

    private fun req(ts: Long, up: Long = 100, down: Long = 900, status: Int? = 200,
                    proto: Protocol = Protocol.HTTP1, error: String? = null) =
        CapturedRequest(
            id = 1, timestampMs = ts, host = "h", path = "/p", method = "GET", status = status,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
            responseBody = "", bytesUp = up, bytesDown = down, protocol = proto,
            appUid = null, error = error,
        )

    @Test
    fun `buckets align to second boundaries`() {
        val t = TimeSeriesStats(bucketMs = 1_000)
        t.record(req(1_200))
        t.record(req(1_800))
        t.record(req(2_500))
        val s = t.series()
        assertEquals(2, s.size)
        assertEquals(1_000L, s[0].startMs)
        assertEquals(2_000L, s[1].startMs)
        assertEquals(2, s[0].requests)
        assertEquals(1, s[1].requests)
    }

    @Test
    fun `gap buckets are filled`() {
        val t = TimeSeriesStats(bucketMs = 1_000)
        t.record(req(0))
        t.record(req(5_000))
        val s = t.series()
        assertEquals(6, s.size)
        assertEquals(1, s[0].requests)
        assertEquals(0, s[3].requests)  // gap
        assertEquals(1, s[5].requests)
    }

    @Test
    fun `protocol split counters`() {
        val t = TimeSeriesStats()
        t.record(req(0, proto = Protocol.HTTP1))
        t.record(req(10, proto = Protocol.HTTP2))
        t.record(req(20, proto = Protocol.TLS))
        t.record(req(30, proto = Protocol.QUIC))
        t.record(req(40, proto = Protocol.DNS))
        val b = t.series().first()
        assertEquals(2, b.httpCount)
        assertEquals(1, b.tlsCount)
        assertEquals(1, b.quicCount)
        assertEquals(1, b.otherCount)
    }

    @Test
    fun `bytes accumulate per direction`() {
        val t = TimeSeriesStats()
        t.record(req(0, up = 10, down = 20))
        t.record(req(500, up = 1, down = 2))
        val b = t.series().first()
        assertEquals(11L, b.bytesUp)
        assertEquals(22L, b.bytesDown)
        assertEquals(33L, b.totalBytes)
    }

    @Test
    fun `errors counted per bucket`() {
        val t = TimeSeriesStats()
        t.record(req(0, status = 502))
        t.record(req(100, status = 200))
        t.record(req(200, status = 200, error = "decode failed"))
        val b = t.series().first()
        assertEquals(2, b.errorCount)
    }

    @Test
    fun `peak bytes per second`() {
        val t = TimeSeriesStats(bucketMs = 500)
        t.record(req(0, up = 300, down = 700))    // 1000 bytes / 0.5s = 2000 B/s
        t.record(req(1000, up = 10, down = 10))   // 20 / 0.5 = 40 B/s
        assertEquals(2000.0, t.peakBytesPerSecond(), 1e-9)
    }

    @Test
    fun `csv rendering`() {
        val t = TimeSeriesStats(bucketMs = 1_000)
        t.record(req(0, up = 1, down = 2))
        t.record(req(1_500, up = 3, down = 4, status = 500))
        val csv = t.toCsv()
        val lines = csv.trim().lines()
        assertEquals("time_ms,requests,bytes_up,bytes_down,errors", lines[0])
        assertEquals("0,1,1,2,0", lines[1])
        assertEquals("1000,1,3,4,1", lines[2])
    }

    @Test
    fun `empty series and reset`() {
        val t = TimeSeriesStats()
        assertTrue(t.series().isEmpty())
        assertEquals(0, t.requestCount)
        t.record(req(0))
        assertEquals(1, t.requestCount)
        t.reset()
        assertEquals(0, t.requestCount)
        assertTrue(t.series().isEmpty())
    }
}

class SessionScoreTest {

    private fun req(status: Int? = 200, dur: Long? = 100, proto: Protocol = Protocol.HTTP1,
                    error: String? = null) = CapturedRequest(
        id = 1, timestampMs = 0, host = "h", path = "/", method = "GET", status = status,
        requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
        responseBody = "", bytesUp = 1, bytesDown = 1, protocol = proto, appUid = null,
        durationMs = dur, error = error,
    )

    @Test
    fun `perfect session scores 100`() {
        val reqs = (1..10).map { req(proto = Protocol.TLS) }
        assertEquals(100, SessionScore.compute(reqs, nxdomainRate = 0.0))
    }

    @Test
    fun `empty session is neutral 100`() {
        assertEquals(100, SessionScore.compute(emptyList()))
    }

    @Test
    fun `all errors floor the score`() {
        val reqs = (1..10).map { req(status = 500) }
        // 45*(0) + 25*(1) + 20*0 + 10*1 = 35
        assertEquals(35, SessionScore.compute(reqs))
    }

    @Test
    fun `slow exchanges reduce score by weight`() {
        val fast = (1..8).map { req(proto = Protocol.TLS) }
        val slow = (1..2).map { req(proto = Protocol.TLS, dur = 5_000) }
        // errorRate=0 (45) + slowShare=0.2 -> 25*0.8=20 + secure=1 -> 20 + 10 = 95
        assertEquals(95, SessionScore.compute(fast + slow))
    }

    @Test
    fun `insecure traffic loses security points`() {
        val reqs = (1..10).map { req(proto = Protocol.HTTP1) }
        // 45 + 25 + 20*0 + 10 = 80
        assertEquals(80, SessionScore.compute(reqs))
    }

    @Test
    fun `nxdomain drains up to ten points`() {
        val reqs = (1..10).map { req(proto = Protocol.TLS) }
        assertEquals(90, SessionScore.compute(reqs, nxdomainRate = 1.0))
        assertEquals(95, SessionScore.compute(reqs, nxdomainRate = 0.5))
    }

    @Test
    fun `capture errors count like 5xx`() {
        val ok = (1..9).map { req(proto = Protocol.TLS) }
        val broken = listOf(req(proto = Protocol.TLS, error = "truncated"))
        // errorRate = 0.1 -> 45*0.9 = 40.5 -> int 40 + 25 + 20 + 10 = 95
        assertEquals(95, SessionScore.compute(ok + broken))
    }

    @Test
    fun `grade bands`() {
        assertEquals("A+", SessionScore.grade(100))
        assertEquals("A", SessionScore.grade(95))
        assertEquals("A-", SessionScore.grade(90))
        assertEquals("B+", SessionScore.grade(87))
        assertEquals("B", SessionScore.grade(84))
        assertEquals("B-", SessionScore.grade(80))
        assertEquals("C", SessionScore.grade(75))
        assertEquals("D", SessionScore.grade(65))
        assertEquals("F", SessionScore.grade(10))
    }

    @Test
    fun `components path matches request path`() {
        val reqs = (1..4).map { req(status = 500, proto = Protocol.HTTP1, dur = 9_000) }
        val viaComponents = SessionScore.compute(
            SessionScore.Components(
                errorRate = 1.0, slowShare = 1.0, secureShare = 0.0,
                nxdomainRate = 0.0, exchangeCount = 4,
            ),
        )
        assertEquals(viaComponents, SessionScore.compute(reqs))
    }
}
