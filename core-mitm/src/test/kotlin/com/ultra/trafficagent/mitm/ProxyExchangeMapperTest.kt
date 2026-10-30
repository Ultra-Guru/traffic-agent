package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.capture.Protocol
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class ProxyExchangeMapperTest {

    private fun exchange(
        tls: Boolean = true,
        body: ByteArray? = "hello".toByteArray(),
        decoded: ByteArray? = null,
        mime: String? = "application/json",
    ) = ProxyExchange(
        id = 1,
        timestampMs = 1700000000123,
        scheme = if (tls) "https" else "http",
        host = "api.example.com",
        port = 443,
        method = "GET",
        path = "/v1/items?page=2",
        requestHeaders = listOf("Host" to "api.example.com", "Accept" to "application/json"),
        requestBody = null,
        status = 200,
        responseHeaders = buildList {
            if (mime != null) add("Content-Type" to "$mime; charset=utf-8")
            add("X-Trace" to "t1")
        },
        responseBody = body,
        responseDecodedBody = decoded,
        requestBytes = 123,
        responseBytes = 4567,
        durationMs = 89,
        tls = tls,
    )

    @Test
    fun `maps tls exchange fields`() {
        val req = ProxyExchangeMapper.toCapturedRequest(exchange(), id = 42)
        assertEquals(42, req.id)
        assertEquals("api.example.com", req.host)
        assertEquals("/v1/items?page=2", req.path)
        assertEquals("GET", req.method)
        assertEquals(200, req.status)
        assertEquals("api.example.com", req.requestHeaders["Host"])
        assertEquals("t1", req.responseHeaders["X-Trace"])
        assertEquals("hello", req.responseBody)
        assertEquals(123, req.bytesUp)
        assertEquals(4567, req.bytesDown)
        assertEquals(Protocol.TLS, req.protocol)
        assertTrue(req.isSecure)
        assertEquals(89, req.durationMs)
        assertEquals("application/json", req.responseMime)
        assertEquals(null, req.responseDecompressedBytes)  // no decoded variant present
    }

    @Test
    fun `plain http maps to HTTP1 and is not secure`() {
        val req = ProxyExchangeMapper.toCapturedRequest(exchange(tls = false), id = 1)
        assertEquals(Protocol.HTTP1, req.protocol)
        assertTrue(!req.isSecure)
    }

    @Test
    fun `decoded body wins over raw`() {
        val req = ProxyExchangeMapper.toCapturedRequest(
            exchange(body = byteArrayOf(0x1F.toByte(), 0x8B.toByte()), decoded = "expanded".toByteArray()),
            id = 2,
        )
        assertEquals("expanded", req.responseBody)
        assertEquals("expanded".length.toLong(), req.responseDecompressedBytes)
    }

    @Test
    fun `binary body becomes a readable placeholder`() {
        val binary = byteArrayOf(0x00, 0x01, 0x02, 0xFF.toByte(), 0xFE.toByte())
        val req = ProxyExchangeMapper.toCapturedRequest(exchange(body = binary, mime = null), id = 3)
        assertEquals("«binary body: 5 bytes»", req.responseBody)
    }

    @Test
    fun `json sniffing when content type is absent`() {
        val req = ProxyExchangeMapper.toCapturedRequest(
            exchange(body = """{"a":1}""".toByteArray(), mime = null),
            id = 4,
        )
        assertEquals("application/json", req.responseMime)
    }

    @Test
    fun `error and uid pass through`() {
        val broken = exchange().copy(error = "connection reset")
        val req = ProxyExchangeMapper.toCapturedRequest(broken, id = 5, appUid = 10042)
        assertEquals("connection reset", req.error)
        assertEquals(10042, req.appUid)
    }
}
