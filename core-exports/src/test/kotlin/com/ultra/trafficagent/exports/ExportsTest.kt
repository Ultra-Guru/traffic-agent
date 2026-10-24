package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.time.Instant

class JsonWriterTest {

    @Test
    fun `escapes quotes backslash and control chars`() {
        assertEquals("\"hi\"", JsonWriter.str("hi"))
        assertEquals("\"a\\\"b\"", JsonWriter.str("a\"b"))
        assertEquals("\"a\\\\b\"", JsonWriter.str("a\\b"))
        assertEquals("\"line1\\nline2\"", JsonWriter.str("line1\nline2"))
        assertEquals("\"tab\\there\"", JsonWriter.str("tab\there"))
        assertEquals("\"ctrl\\u0001x\"", JsonWriter.str("ctrlx"))
        assertEquals("\"null\"", JsonWriter.str("null"))
        assertEquals("null", JsonWriter.str(null))
    }

    @Test
    fun `builds objects and arrays`() {
        assertEquals("""{"a":1,"b":"x"}""", JsonWriter.obj("a" to "1", "b" to JsonWriter.str("x")))
        assertEquals("""[1,2]""", JsonWriter.arr(listOf("1", "2")))
        assertEquals("[]", JsonWriter.arr(emptyList()))
        assertEquals("5", JsonWriter.num(5))
        assertEquals("true", JsonWriter.bool(true))
    }
}

class HarExporterTest {

    private fun req(id: Long = 1, ts: Long = 1700000000123L) = CapturedRequest(
        id = id, timestampMs = ts, host = "api.example.com", path = "/v1/x?q=1",
        method = "POST", status = 201,
        requestHeaders = mapOf("Content-Type" to "application/json"),
        responseHeaders = mapOf("Content-Type" to "application/json"),
        requestBody = """{"a":1}""", responseBody = """{"ok":true}""",
        bytesUp = 120, bytesDown = 340, protocol = Protocol.HTTP1, appUid = null,
    )

    @Test
    fun `har skeleton and metadata`() {
        val har = HarExporter.export(listOf(req()))
        assertTrue(har.contains("\"version\": \"1.2\"")) // handwritten template keeps spaces
        assertTrue(har.contains("\"name\":\"traffic-agent\"")) // json-writer part is compact
        assertTrue(har.contains("\"entries\""))
    }

    @Test
    fun `timestamps are ISO-8601 parseable`() {
        val entry = HarExporter.entry(req())
        val m = Regex("\"startedDateTime\":\\s*\"([^\"]+)\"").find(entry)!!
        Instant.parse(m.groupValues[1]) // must not throw
    }

    @Test
    fun `entry carries request response and bodies`() {
        val entry = HarExporter.entry(req())
        assertTrue(entry.contains("\"method\":\"POST\""))
        assertTrue(entry.contains("\"url\":\"https://api.example.com/v1/x?q=1\""))
        assertTrue(entry.contains("\"status\":201"))
        assertTrue(entry.contains("\"bodySize\":120"))
        assertTrue(entry.contains("{\\\"ok\\\":true}"))
    }

    @Test
    fun `multiple entries joined`() {
        val har = HarExporter.export(listOf(req(1), req(2, 1700000000999L)))
        assertTrue(har.count { it == '\n' } >= 10)
        assertTrue(har.contains("2023-11-14"))
    }

    @Test
    fun `pending responses export with status zero`() {
        val pending = req().copy(status = null)
        val entry = HarExporter.entry(pending)
        assertTrue(entry.contains("\"status\":0"))
        assertTrue(entry.contains("pending"))
    }
}

class CurlExporterTest {

    private fun req(
        method: String = "GET", body: String = "",
        headers: Map<String, String> = mapOf("Accept" to "application/json"),
    ) = CapturedRequest(
        id = 1, timestampMs = 0, host = "h.io", path = "/p", method = method, status = 200,
        requestHeaders = headers, responseHeaders = emptyMap(),
        requestBody = body, responseBody = "", bytesUp = 0, bytesDown = 0,
        protocol = Protocol.HTTP1, appUid = null,
    )

    @Test
    fun `get without body`() {
        val curl = CurlExporter.toCurl(req())
        assertEquals("curl -X GET 'https://h.io/p' -H 'Accept: application/json' --compressed", curl)
    }

    @Test
    fun `post includes data-raw`() {
        val curl = CurlExporter.toCurl(req(method = "POST", body = """{"a":1}"""))
        assertTrue(curl.startsWith("curl -X POST"))
        assertTrue(curl.contains("--data-raw '{\"a\":1}'"))
    }

    @Test
    fun `single quotes in values are escaped`() {
        assertEquals("'it'\\''s'", CurlExporter.shellQuote("it's"))
        val curl = CurlExporter.toCurl(req(headers = mapOf("X-Note" to "it's fine")))
        assertTrue(curl.contains("-H 'X-Note: it'\\''s fine'"))
    }

    @Test
    fun `body can be excluded`() {
        val curl = CurlExporter.toCurl(req(method = "POST", body = "data"), includeBody = false)
        assertTrue(!curl.contains("--data-raw"))
    }
}

class TableExportersTest {

    private fun req(id: Long, host: String = "a.io", path: String = "/x", status: Int? = 200) =
        CapturedRequest(
            id = id, timestampMs = 1000 + id, host = host, path = path, method = "GET",
            status = status, requestHeaders = emptyMap(), responseHeaders = emptyMap(),
            requestBody = "", responseBody = "", bytesUp = 10, bytesDown = 20,
            protocol = Protocol.TLS, appUid = null,
        )

    @Test
    fun `markdown has header table and summary`() {
        val md = MarkdownExporter.export(listOf(req(1), req(2)))
        assertTrue(md.startsWith("# Traffic Agent report"))
        assertTrue(md.contains("- Requests: 2"))
        assertTrue(md.contains("- Total traffic: 60 bytes"))
        assertTrue(md.contains("| 1 | GET | a.io | /x | 200 | 10 | 20 |"))
        assertTrue(md.contains("| # | Method | Host | Path | Status | Up | Down |"))
    }

    @Test
    fun `markdown escapes pipes in cells`() {
        val md = MarkdownExporter.export(listOf(req(1, path = "/a|b")))
        assertTrue(md.contains("/a\\|b"))
    }

    @Test
    fun `csv quotes special fields`() {
        assertEquals("plain", CsvExporter.field("plain"))
        assertEquals("\"a,b\"", CsvExporter.field("a,b"))
        assertEquals("\"say \"\"hi\"\"\"", CsvExporter.field("say \"hi\""))
        assertEquals("\"line1\nline2\"", CsvExporter.field("line1\nline2"))
    }

    @Test
    fun `csv rows follow header`() {
        val csv = CsvExporter.export(listOf(req(1, path = "/with,comma")))
        val lines = csv.trim().lines()
        assertEquals(
            "id,timestamp_ms,method,host,path,status,bytes_up,bytes_down,protocol",
            lines[0],
        )
        assertTrue(lines[1].contains("\"/with,comma\""))
        assertTrue(lines[1].endsWith(",TLS"))
    }
}
