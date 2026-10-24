package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class NewExportersTest {

    private fun capture(id: Long) = CapturedRequest(
        id = id,
        timestampMs = 1_700_000_000_000 + id,
        host = "api.example.com",
        path = "/v2/users/list?active=true&limit=20",
        method = "POST",
        status = 200,
        requestHeaders = linkedMapOf(
            "Content-Type" to "application/json",
            "Authorization" to "Bearer tok\"en",
        ),
        responseHeaders = linkedMapOf("Content-Type" to "application/json"),
        requestBody = """{"q":"中文 query"}""",
        responseBody = """{"items":[]}""",
        bytesUp = 120,
        bytesDown = 340,
        protocol = Protocol.HTTP2,
        appUid = 10085,
    )

    // ---------------- Postman ----------------

    @Test
    fun `postman collection shape is valid v2_1`() {
        val json = PostmanExporter.toPostmanCollection(listOf(capture(1), capture(2)))
        assertTrue(json.startsWith("{\"info\":{"), json)
        assertTrue(json.contains("\"name\":\"POST api.example.com/v2/users/list?active=true&limit=20\""), json)
        assertTrue(
            json.contains("\"schema\":\"https://schema.getpostman.com/json/collection/v2.1.0/collection.json\""),
            json,
        )
        assertEquals(2, Regex("\"method\":\"POST\"").findAll(json).count())
        assertTrue(json.contains("\"host\":[\"api\",\"example\",\"com\"]"), json)
        assertTrue(json.contains("\"path\":[\"v2\",\"users\",\"list\"]"), json)
        assertTrue(json.contains("\"key\":\"active\""), json)
        assertTrue(json.contains("\"key\":\"limit\""), json)
        assertTrue(json.contains("\"raw\":\"{\\\"q\\\":\\\"中文 query\\\"}\""), json)
        assertTrue(json.contains("\"value\":\"Bearer tok\\\"en\""), json)
    }

    @Test
    fun `get request carries no body block`() {
        val get = capture(1).copy(method = "GET", requestBody = "", path = "/plain")
        val json = PostmanExporter.toPostmanCollection(listOf(get))
        assertTrue(!json.contains(""""body":"""))
    }

    // ---------------- RawHttp ----------------

    @Test
    fun `share text contains wire-format halves`() {
        val text = RawHttpExporter.toShareText(capture(1))
        assertTrue(text.startsWith("POST /v2/users/list?active=true&limit=20 HTTP/1.1\r\n"))
        assertTrue(text.contains("Host: api.example.com\r\n"))
        assertTrue(text.contains("Content-Type: application/json\r\n"))
        assertTrue(text.contains("""{"q":"中文 query"}"""))
        assertTrue(text.contains("=== RESPONSE ==="))
        assertTrue(text.contains("HTTP/1.1 200 OK\r\n"))
    }

    @Test
    fun `status reasons cover common codes`() {
        assertEquals(
            "Not Found",
            RawHttpExporter.toShareText(capture(1).copy(status = 404))
                .substringAfter("=== RESPONSE ===").let { it.substringAfter("HTTP/1.1 404 ") }.substringBefore("\r\n"),
        )
    }

    @Test
    fun `host header not duplicated in raw request`() {
        val c = capture(1).copy(
            requestHeaders = linkedMapOf("Host" to "old.example.com", "X-A" to "1"),
        )
        val raw = RawHttpExporter.toRawHttpRequest(c)
        assertEquals(1, Regex("Host:", RegexOption.IGNORE_CASE).findAll(raw).count())
        assertTrue(raw.contains("Host: api.example.com"))
    }
}
