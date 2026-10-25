package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/** Direct JSONL round-trip coverage for the persistence codec (基建三「存」). */
class SessionCodecTest {

    private fun session(
        id: Long = 1L,
        body: String = "",
        status: Int? = 200,
    ) = CapturedRequest(
        id = id,
        timestampMs = 1_699_000_000_000L,
        host = "api.example.com",
        path = "/v1/things?page=2",
        method = "GET",
        status = status,
        requestHeaders = mapOf("Accept" to "application/json"),
        responseHeaders = mapOf("Content-Type" to "text/html; charset=utf-8"),
        requestBody = "",
        responseBody = body,
        bytesUp = 128L,
        bytesDown = 4096L,
        protocol = Protocol.HTTP1,
        appUid = 10042,
    )

    @Test
    fun `round trips a full session`() {
        val original = session(body = "<html>\n\"quoted\" & 'more'</html>")
        val decoded = SessionCodec.decode(SessionCodec.encode(original))
        assertEquals(original, decoded)
    }

    @Test
    fun `round trips null status and uid`() {
        val original = session(status = null).copy(appUid = null)
        val decoded = SessionCodec.decode(SessionCodec.encode(original))
        assertNull(decoded!!.status)
        assertNull(decoded.appUid)
    }

    @Test
    fun `round trips every protocol enum value`() {
        for (p in Protocol.entries) {
            val encoded = SessionCodec.encode(session().copy(protocol = p))
            assertEquals(p, SessionCodec.decode(encoded)!!.protocol, "protocol $p")
        }
    }

    @Test
    fun `decode rejects blank and non object lines`() {
        assertNull(SessionCodec.decode(""))
        assertNull(SessionCodec.decode("   "))
        assertNull(SessionCodec.decode("not json at all"))
        assertNull(SessionCodec.decode("[1,2,3]"))
    }

    @Test
    fun `decode rejects malformed json structures`() {
        assertNull(SessionCodec.decode("{\"id\":1"))                    // truncated object
        assertNull(SessionCodec.decode("{\"id\":\"x\"}"))                // id not a number
        assertNull(SessionCodec.decode("{id:1}"))                        // unquoted key
        assertNull(SessionCodec.decode("{\"id\":1,\"a\":}"))             // missing value
        assertNull(SessionCodec.decode("{\"id\":1,\"a\":\"unterminated}")) // unterminated string
    }

    @Test
    fun `decode survives unknown extra fields`() {
        // The codec subset has no array support, so future fields must be
        // scalars, strings or nested objects — exactly what we design for.
        val encoded = SessionCodec.encode(session())
            .removeSuffix("}") + ",\"futureField\":{\"nested\":{\"x\":1}},\"futureNum\":7}"
        assertEquals(session(), SessionCodec.decode(encoded))
    }

    @Test
    fun `decode parses unicode and control escapes`() {
        val encoded = SessionCodec.encode(session(body = "café — 东京 \u0007bell"))
        assertEquals("café — 东京 \u0007bell", SessionCodec.decode(encoded)!!.responseBody)
    }

    @Test
    fun `escape quotes backslash and control characters`() {
        assertEquals("null", SessionCodec.escape(null))
        val escaped = SessionCodec.escape("a\"b\\c\nd\re\tf\bg")
        assertTrue(escaped.contains("\\\""))
        assertTrue(escaped.contains("\\\\"))
        assertTrue(escaped.contains("\\n"))
        assertTrue(escaped.contains("\\r"))
        assertTrue(escaped.contains("\\t"))
        assertTrue(escaped.contains("\\b"))
        assertEquals("\"a\\\"b\\\\c\\nd\\re\\tf\\bg\"", escaped)
    }

    @Test
    fun `encode emits compact single line json`() {
        val encoded = SessionCodec.encode(session())
        assertTrue(encoded.startsWith("{") && encoded.endsWith("}"))
        assertEquals(1, encoded.lines().size)
        assertTrue(encoded.contains("\"host\":\"api.example.com\""))
        assertTrue(encoded.contains("\"protocol\":\"HTTP1\""))
        assertTrue(encoded.contains("\"uid\":10042"))
        assertTrue(encoded.contains("\"status\":200"))
    }

    @Test
    fun `encode maps and decode restores empty maps`() {
        val empty = session().copy(requestHeaders = emptyMap(), responseHeaders = emptyMap())
        val decoded = SessionCodec.decode(SessionCodec.encode(empty))
        assertTrue(decoded!!.requestHeaders.isEmpty())
        assertTrue(decoded.responseHeaders.isEmpty())
    }

    @Test
    fun `decode handles large numeric fields`() {
        val big = session().copy(
            id = Long.MAX_VALUE,
            timestampMs = 253_402_300_799_000L,
            bytesUp = 9_007_199_254_740_992L,
            bytesDown = 1_000_000_000_000L,
        )
        assertEquals(big, SessionCodec.decode(SessionCodec.encode(big)))
    }

    @Test
    fun `decode defaults missing optional fields instead of failing`() {
        val decoded = SessionCodec.decode("{\"id\":5}")
        assertEquals(5L, decoded!!.id)
        assertEquals("", decoded.host)
        assertEquals(0L, decoded.bytesUp)
        assertEquals(Protocol.UNKNOWN, decoded.protocol)
        assertNull(decoded.status)
    }

    @Test
    fun `escape emits unicode form for control chars below 0x20`() {
        // 0x1f is escaped as \\u001f; a space (0x20) stays literal.
        assertEquals("\"\\u001f\"", SessionCodec.escape("\u001f"))
        assertEquals("\" \"", SessionCodec.escape(" "))
        assertEquals("\"\\u0001\"", SessionCodec.escape("\u0001"))
    }

    @Test
    fun `round trips a body holding a raw control byte`() {
        val original = session(body = "a\u001fb")
        assertEquals(original, SessionCodec.decode(SessionCodec.encode(original)))
    }

    @Test
    fun `decode rejects object-open without object-close`() {
        assertNull(SessionCodec.decode("{"))
        assertNull(SessionCodec.decode("{invalid"))
    }

    @Test
    fun `encode renders null status and uid as json null`() {
        val encoded = SessionCodec.encode(session(status = null).copy(appUid = null))
        assertTrue(encoded.contains("\"status\":null"))
        assertTrue(encoded.contains("\"uid\":null"))
    }
}
