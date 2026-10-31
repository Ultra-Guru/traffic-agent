package com.ultra.trafficagent.exports

import com.ultra.trafficagent.analysis.DnsInsight
import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.ByteArrayInputStream
import java.util.zip.ZipInputStream

class ReportExporterTest {

    private fun req(ts: Long, host: String = "api.example.com", status: Int? = 200, up: Long = 100,
                    down: Long = 5_000, dur: Long? = 50, proto: Protocol = Protocol.HTTP1,
                    error: String? = null, path: String = "/api/v1") = CapturedRequest(
        id = 1, timestampMs = ts, host = host, path = path, method = "GET", status = status,
        requestHeaders = mapOf("accept" to "*/*"), responseHeaders = emptyMap(),
        requestBody = "", responseBody = "", bytesUp = up, bytesDown = down,
        protocol = proto, appUid = null, durationMs = dur, error = error,
    )

    @Test
    fun `summary section lists counts and score`() {
        val md = ReportExporter.export(listOf(req(0), req(1_000, host = "b.com")))
        assertTrue(md.contains("# Traffic Agent session report"))
        assertTrue(md.contains("## Summary"))
        assertTrue(md.contains("| Exchanges | 2 |"))
        assertTrue(md.contains("| Session score |"))
        assertTrue(md.contains("9.8 KiB"))  // 2 x 5000 down bytes
    }

    @Test
    fun `top hosts section sorted by traffic`() {
        val md = ReportExporter.export(
            listOf(
                req(0, host = "small.com", down = 100),
                req(1, host = "big.com", down = 100_000),
            ),
        )
        val topIdx = md.indexOf("big.com")
        val smallIdx = md.indexOf("small.com")
        assertTrue(topIdx in 0 until smallIdx)
        assertTrue(md.contains("## Top hosts"))
    }

    @Test
    fun `error and slow sections appear when relevant`() {
        val md = ReportExporter.export(
            listOf(
                req(0, host = "err.com", status = 502),
                req(1, host = "slow.com", dur = 9_000),
                req(2, host = "ok.com"),
            ),
        )
        assertTrue(md.contains("## Errors (1)"))
        assertTrue(md.contains("502"))
        assertTrue(md.contains("## Slow requests (> 1s)"))
        assertTrue(md.contains("slow.com"))
        assertTrue(md.contains("9000 ms"))
    }

    @Test
    fun `dns section renders when insight provided`() {
        val insight = DnsInsight()
        insight.observe(DnsInsight.Observation(0, "a.com", 0))
        insight.observe(DnsInsight.Observation(1, "b.com", 3))
        val md = ReportExporter.export(listOf(req(0)), dnsInsight = insight)
        assertTrue(md.contains("## DNS"))
        assertTrue(md.contains("NXDOMAIN: 1 (50.0%)"))
        assertTrue(md.contains("a.com"))
    }

    @Test
    fun `sparkline renders for multi-second sessions`() {
        val reqs = (0 until 10).map { req(it * 1_000L, host = "h$it.com") }
        val md = ReportExporter.export(reqs)
        assertTrue(md.contains("## Timeline"))
        val blocks = "▁▂▃▄▅▆▇█"
        assertTrue(blocks.any { ch -> md.contains(ch) })
    }

    @Test
    fun `request table capped at 500 rows`() {
        val reqs = (0 until 600).map { req(it.toLong()) }
        val md = ReportExporter.export(reqs)
        assertTrue(md.contains("100 more"))
        // No row 501+.
        assertTrue(!md.contains("| 501 |"))
    }

    @Test
    fun `pipe characters escaped in cells`() {
        val md = ReportExporter.export(listOf(req(0, host = "we|ird.com")))
        assertTrue(md.contains("we\\|ird.com"))
        assertTrue(!md.contains("we|ird.com"))
    }

    @Test
    fun `byte formatting tiers`() {
        assertEquals("512 B", ReportExporter.formatBytes(512))
        assertEquals("1.5 KiB", ReportExporter.formatBytes(1_536))
        assertEquals("2.0 MiB", ReportExporter.formatBytes(2 * 1_048_576))
    }
}

class SessionPackagerTest {

    private fun req(ts: Long, host: String = "api.example.com") = CapturedRequest(
        id = 1, timestampMs = ts, host = host, path = "/x", method = "GET", status = 200,
        requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
        responseBody = "", bytesUp = 10, bytesDown = 20, protocol = Protocol.HTTP1, appUid = null,
    )

    private fun unzipEntries(zipBytes: ByteArray): Map<String, ByteArray> {
        val out = mutableMapOf<String, ByteArray>()
        ZipInputStream(ByteArrayInputStream(zipBytes)).use { zis ->
            var entry = zis.nextEntry
            while (entry != null) {
                val buf = java.io.ByteArrayOutputStream()
                zis.copyTo(buf)
                out[entry.name] = buf.toByteArray()
                entry = zis.nextEntry
            }
        }
        return out
    }

    @Test
    fun `standard package contains manifest and artifacts`() {
        val zip = SessionPackager.packageStandard(
            listOf(req(0), req(1_000, host = "b.com")),
            title = "test session",
            nowMs = 1_700_000_000_000,
        )
        val entries = unzipEntries(zip)
        assertTrue(entries.containsKey("manifest.json"))
        assertTrue(entries.containsKey("session.md"))
        assertTrue(entries.containsKey("session.csv"))
        assertTrue(entries.containsKey("session.har"))
        assertTrue(entries.containsKey("session.jsonl"))
        assertTrue(entries.containsKey("session.curl"))
        assertTrue(entries.containsKey("session.timeline"))
        val manifest = String(entries["manifest.json"]!!)
        assertTrue(manifest.contains("\"exchangeCount\": 2"))
        assertTrue(manifest.contains("\"session.md\""))
        assertTrue(manifest.contains("\"formatVersion\": 1"))
    }

    @Test
    fun `duplicate artifact names are deduplicated`() {
        val zip = SessionPackager.packageSession(
            listOf(
                SessionPackager.Artifact("data.txt", "text/plain", "first"),
                SessionPackager.Artifact("data.txt", "text/plain", "second"),
            ),
            createdAtMs = 0,
            exchangeCount = 0,
        )
        val entries = unzipEntries(zip)
        assertTrue(entries.containsKey("data.txt"))
        assertTrue(entries.containsKey("data-1.txt"))
        assertEquals("first", String(entries["data.txt"]!!))
        assertEquals("second", String(entries["data-1.txt"]!!))
    }

    @Test
    fun `empty package rejected`() {
        assertThrows(IllegalArgumentException::class.java) {
            SessionPackager.packageSession(emptyList(), 0, 0)
        }
    }

    @Test
    fun `binary artifacts roundtrip`() {
        val pcapHeader = byteArrayOf(0xd4.toByte(), 0xc3.toByte(), 0xb2.toByte(), 0xa1.toByte())
        val zip = SessionPackager.packageSession(
            listOf(SessionPackager.Artifact("cap.pcap", "application/vnd.tcpdump.pcap", pcapHeader)),
            createdAtMs = 42,
            exchangeCount = 1,
        )
        val entries = unzipEntries(zip)
        assertTrue(entries["cap.pcap"]!!.contentEquals(pcapHeader))
    }

    @Test
    fun `manifest lists artifact sizes`() {
        val zip = SessionPackager.packageSession(
            listOf(SessionPackager.Artifact("a.txt", "text/plain", "hello")),
            createdAtMs = 1,
            exchangeCount = 5,
        )
        val manifest = String(unzipEntries(zip)["manifest.json"]!!)
        assertTrue(manifest.contains("\"bytes\": 5"))
        assertTrue(manifest.contains("\"mime\": \"text/plain\""))
    }
}

class FlowTimelineExporterTest {

    @Test
    fun `timeline shows request and response arrows`() {
        val req = CapturedRequest(
            id = 1, timestampMs = 3_723_000_123, host = "api.example.com", path = "/v1/data",
            method = "GET", status = 200, requestHeaders = emptyMap(), responseHeaders = emptyMap(),
            requestBody = "", responseBody = "", bytesUp = 412, bytesDown = 5_120,
            protocol = Protocol.HTTP1, appUid = null, durationMs = 78,
        )
        val out = FlowTimelineExporter.export(listOf(req))
        assertTrue(out.contains("-> api.example.com"))
        assertTrue(out.contains("GET /v1/data"))
        assertTrue(out.contains("<- api.example.com"))
        assertTrue(out.contains("200 OK"))
        assertTrue(out.contains("5.0 KiB"))
        assertTrue(out.contains("78 ms"))
    }

    @Test
    fun `pending requests have no response line`() {
        val req = CapturedRequest(
            id = 1, timestampMs = 0, host = "h", path = "/", method = "POST", status = null,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
            responseBody = "", bytesUp = 1, bytesDown = 0, protocol = Protocol.TLS, appUid = null,
        )
        val out = FlowTimelineExporter.export(listOf(req))
        assertTrue(out.count { it == '\n' } == 1)
        assertTrue(!out.contains("<-"))
    }

    @Test
    fun `long paths are truncated`() {
        val longPath = "/" + "a".repeat(200)
        val req = CapturedRequest(
            id = 1, timestampMs = 0, host = "h", path = longPath, method = "GET", status = 200,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
            responseBody = "", bytesUp = 1, bytesDown = 1, protocol = Protocol.HTTP1, appUid = null,
        )
        val out = FlowTimelineExporter.export(listOf(req))
        assertTrue(out.lines().any { it.length <= 130 })
    }
}

class JsonlExporterTest {

    @Test
    fun `one object per line with core fields`() {
        val req = CapturedRequest(
            id = 7, timestampMs = 1_000, host = "h.com", path = "/p", method = "GET", status = 404,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
            responseBody = "", bytesUp = 1, bytesDown = 2, protocol = Protocol.HTTP2,
            appUid = null, durationMs = 15, error = null,
        )
        val out = JsonlExporter.export(listOf(req))
        val lines = out.trim().lines()
        assertEquals(1, lines.size)
        val obj = lines[0]
        assertTrue(obj.startsWith("{") && obj.endsWith("}"))
        assertTrue(obj.contains("\"id\": 7"))
        assertTrue(obj.contains("\"status\": 404"))
        assertTrue(obj.contains("\"proto\": \"HTTP2\""))
        assertTrue(obj.contains("\"durationMs\": 15"))
    }

    @Test
    fun `null status serialized as json null`() {
        val req = CapturedRequest(
            id = 1, timestampMs = 0, host = "h", path = "/", method = "GET", status = null,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
            responseBody = "", bytesUp = 0, bytesDown = 0, protocol = Protocol.TLS, appUid = null,
        )
        val out = JsonlExporter.export(listOf(req))
        assertTrue(out.contains("\"status\": null"))
        assertTrue(!out.contains("\"durationMs\""))
        assertTrue(!out.contains("\"error\""))
    }

    @Test
    fun `strings are escaped`() {
        val req = CapturedRequest(
            id = 1, timestampMs = 0, host = "h", path = "/a\"b\\c", method = "GET", status = 200,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(), requestBody = "",
            responseBody = "", bytesUp = 0, bytesDown = 0, protocol = Protocol.HTTP1, appUid = null,
            error = "trunc\"ated",
        )
        val out = JsonlExporter.export(listOf(req))
        assertTrue(out.contains("/a\\\"b\\\\c"))
        assertTrue(out.contains("trunc\\\"ated"))
        // Parseable as JSON via the platform parser.
        val line = out.trim()
        assertNotNull(line)
    }
}
