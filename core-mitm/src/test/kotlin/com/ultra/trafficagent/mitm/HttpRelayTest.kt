package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.capture.Protocol
import com.sun.net.httpserver.HttpServer
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.net.InetSocketAddress
import java.net.Socket
import java.nio.charset.StandardCharsets
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

/**
 * Exercises HttpRelay against a real loopback origin (基建二「解」): the
 * client side and the TLS wrapper are injected doubles, so every test
 * controls exactly what the client sent and whether TLS was requested.
 */
class HttpRelayTest {

    private lateinit var origin: HttpServer
    private var originPort: Int = 0
    private val tlsWrapped = AtomicBoolean(false)
    private val tlsHost = AtomicReference<String?>(null)

    private val fixedNow = 1_700_000_000_000L

    @BeforeEach
    fun startOrigin() {
        origin = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        origin.createContext("/hello") { exchange ->
            val body = """{"hello":"world","n":42}""".toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/json")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        origin.createContext("/echo") { exchange ->
            val body = exchange.requestBody.readBytes()
            exchange.responseHeaders.add("Content-Type", "text/plain")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        origin.createContext("/chunked") { exchange ->
            exchange.responseHeaders.add("Content-Type", "text/plain")
            exchange.sendResponseHeaders(200, 0) // 0 -> chunked
            exchange.responseBody.use { out ->
                for (chunk in listOf("alpha ", "beta ", "gamma")) {
                    out.write(chunk.toByteArray())
                    out.flush()
                }
            }
        }
        origin.executor = null
        origin.start()
        originPort = origin.address.port
    }

    @AfterEach
    fun stopOrigin() {
        origin.stop(0)
    }

    private fun relay(clientBytes: ByteArray, originalPort: Int = originPort): Pair<HttpRelay, ByteArrayOutputStream> {
        val clientOut = ByteArrayOutputStream()
        val relay = HttpRelay(
            clientIn = ByteArrayInputStream(clientBytes),
            clientOut = clientOut,
            originalDstIp = "10.0.0.1",
            originalDstPort = originalPort,
            openUpstream = { _, _ -> Socket("127.0.0.1", originPort) },
            wrapUpstreamTls = { plain, host, _ ->
                tlsWrapped.set(true)
                tlsHost.set(host)
                plain
            },
            now = { fixedNow },
        )
        return relay to clientOut
    }

    private fun get(target: String, extraHeaders: List<String> = emptyList(), version: String = "HTTP/1.1"): ByteArray =
        buildString {
            append("GET $target $version\r\n")
            append("Host: localhost\r\n")
            for (h in extraHeaders) append(h).append("\r\n")
            append("\r\n")
        }.toByteArray(StandardCharsets.ISO_8859_1)

    @Test
    fun `relays plain request and captures the exchange`() {
        val (relay, clientOut) = relay(get("/hello"))
        val result = relay.exchange(7L)
        assertNotNull(result)
        val captured = result!!.captured
        assertEquals(7L, captured.id)
        assertEquals(fixedNow, captured.timestampMs)
        assertEquals("localhost", captured.host)
        assertEquals("/hello", captured.path)
        assertEquals("GET", captured.method)
        assertEquals(200, captured.status)
        assertTrue(captured.responseBody.contains("\"hello\":\"world\""))
        assertEquals(Protocol.HTTP1, captured.protocol)
        assertTrue(result.clientWantsMore) // HTTP/1.1 without Connection header
        assertTrue(captured.bytesUp > 0)
        assertTrue(captured.bytesDown > 0)
        val toClient = clientOut.toString(StandardCharsets.ISO_8859_1.name())
        assertTrue(toClient.startsWith("HTTP/1.1 200"), "client saw: ${toClient.take(40)}")
        assertTrue(toClient.contains("Content-Length:"))
        assertTrue(toClient.contains("Connection: keep-alive"))
    }

    @Test
    fun `tls port forces tls protocol and wrapper invocation`() {
        val (relay, _) = relay(get("/hello"), originalPort = 443)
        val result = relay.exchange(1L)
        assertNotNull(result)
        assertEquals(Protocol.TLS, result!!.captured.protocol)
        assertTrue(tlsWrapped.get(), "wrapUpstreamTls must be used for 443 flows")
        assertEquals("localhost", tlsHost.get())
    }

    @Test
    fun `missing host header falls back to original destination ip`() {
        val request = "GET /hello HTTP/1.1\r\n\r\n".toByteArray(StandardCharsets.ISO_8859_1)
        val (relay, _) = relay(request)
        val result = relay.exchange(2L)
        assertNotNull(result)
        assertEquals("10.0.0.1", result!!.captured.host)
    }

    @Test
    fun `client close before request yields null`() {
        val (relay, _) = relay(ByteArray(0))
        assertNull(relay.exchange(3L))
    }

    @Test
    fun `connection close header disables keep alive for the client`() {
        val (relay, clientOut) = relay(get("/hello", extraHeaders = listOf("Connection: close")))
        val result = relay.exchange(4L)
        assertNotNull(result)
        assertFalse(result!!.clientWantsMore)
        val toClient = clientOut.toString(StandardCharsets.ISO_8859_1.name())
        assertTrue(toClient.contains("Connection: close"))
        assertFalse(toClient.contains("Connection: keep-alive"))
    }

    @Test
    fun `http 1 0 without connection header defaults to close`() {
        val (relay, _) = relay(get("/hello", version = "HTTP/1.0"))
        val result = relay.exchange(5L)
        assertNotNull(result)
        assertFalse(result!!.clientWantsMore)
    }

    @Test
    fun `chunked response is decoded and reframed with content length`() {
        val (relay, clientOut) = relay(get("/chunked"))
        val result = relay.exchange(6L)
        assertNotNull(result)
        val captured = result!!.captured
        assertEquals("alpha beta gamma", captured.responseBody)
        val toClient = clientOut.toString(StandardCharsets.ISO_8859_1.name())
        assertTrue(toClient.contains("Content-Length: 16"), "reframed: ${toClient.substringAfterLast("\r\n\r\n")}")
        assertFalse(toClient.contains("Transfer-Encoding"))
    }

    @Test
    fun `post body round trips through the echo origin`() {
        val body = "k=v&x=1"
        val request = ("POST /echo HTTP/1.1\r\nHost: localhost\r\nContent-Type: " +
            "application/x-www-form-urlencoded\r\nContent-Length: ${body.length}\r\n\r\n$body")
            .toByteArray(StandardCharsets.ISO_8859_1)
        val (relay, _) = relay(request)
        val result = relay.exchange(8L)
        assertNotNull(result)
        val captured = result!!.captured
        assertEquals("POST", captured.method)
        assertEquals(body, captured.requestBody)
        assertEquals(body, captured.responseBody)
        assertEquals("application/x-www-form-urlencoded", captured.requestHeaders["Content-Type"])
    }

    // ---------------- mutation-killer tests: framing edge cases ----------------

    /** Loopback origin that answers with fully hand-crafted raw bytes. */
    private fun rawOrigin(vararg responses: ByteArray): Pair<Int, () -> Unit> {
        val server = java.net.ServerSocket(0, 1, java.net.InetAddress.getByName("127.0.0.1"))
        val port = server.localPort
        val done = AtomicBoolean(false)
        Thread {
            try {
                server.soTimeout = 10_000
                val socket = server.accept()
                // drain the request head + body before responding
                socket.getInputStream().read(ByteArray(8192))
                val out = socket.getOutputStream()
                for (r in responses) out.write(r)
                out.flush()
                socket.close()
            } catch (_: java.io.IOException) {
            } finally {
                done.set(true)
                server.close()
            }
        }.start()
        return port to { server.close() }
    }

    private fun relayToPort(port: Int, clientBytes: ByteArray): Pair<HttpRelay, ByteArrayOutputStream> {
        val clientOut = ByteArrayOutputStream()
        val relay = HttpRelay(
            clientIn = ByteArrayInputStream(clientBytes),
            clientOut = clientOut,
            originalDstIp = "10.0.0.1",
            originalDstPort = port,
            openUpstream = { _, _ -> Socket("127.0.0.1", port) },
            wrapUpstreamTls = { plain, _, _ -> plain },
            now = { fixedNow },
        )
        return relay to clientOut
    }

    @Test
    fun `malformed status line from upstream throws`() {
        val (port, close) = rawOrigin("GARBAGE\r\n\r\n".toByteArray())
        try {
            val (relay, _) = relayToPort(port, get("/hello"))
            assertThrows<java.io.IOException> { relay.exchange(10L) }
        } finally {
            close()
        }
    }

    @Test
    fun `truncated content length body throws`() {
        val (port, close) = rawOrigin(
            "HTTP/1.1 200 OK\r\nContent-Length: 100\r\n\r\nonly-ten!!".toByteArray(),
        )
        try {
            val (relay, _) = relayToPort(port, get("/hello"))
            assertThrows<java.io.IOException> { relay.exchange(11L) }
        } finally {
            close()
        }
    }

    @Test
    fun `chunked with extensions and empty chunks decodes`() {
        val chunked = ("HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n" +
            "5;ext=1\r\nhello\r\n" +
            "0\r\n\r\n").toByteArray()
        val (port, close) = rawOrigin(chunked)
        try {
            val (relay, _) = relayToPort(port, get("/hello"))
            val result = relay.exchange(12L)
            assertEquals("hello", result!!.captured.responseBody)
        } finally {
            close()
        }
    }

    @Test
    fun `response without reason phrase parses`() {
        val (port, close) = rawOrigin("HTTP/1.1 200\r\nContent-Length: 2\r\n\r\nhi".toByteArray())
        try {
            val (relay, clientOut) = relayToPort(port, get("/hello"))
            val result = relay.exchange(13L)
            assertEquals(200, result!!.captured.status)
            assertEquals("hi", result.captured.responseBody)
            val toClient = clientOut.toString(StandardCharsets.ISO_8859_1.name())
            assertTrue(toClient.startsWith("HTTP/1.1 200\r\n"), "no reason: ${toClient.take(20)}")
        } finally {
            close()
        }
    }

    @Test
    fun `empty host header falls back to original ip`() {
        val request = "GET /hello HTTP/1.1\r\nHost: \r\n\r\n".toByteArray(StandardCharsets.ISO_8859_1)
        val (relay, _) = relay(request)
        val result = relay.exchange(14L)
        assertEquals("10.0.0.1", result!!.captured.host)
    }

    @Test
    fun `host header with port strips the port`() {
        val request = "GET /hello HTTP/1.1\r\nHost: localhost:9999\r\n\r\n"
            .toByteArray(StandardCharsets.ISO_8859_1)
        val (relay, _) = relay(request)
        val result = relay.exchange(15L)
        assertEquals("localhost", result!!.captured.host)
    }

    @Test
    fun `upstream response headers surface in capture`() {
        origin.removeContext("/hello")
        origin.createContext("/hello") { exchange ->
            exchange.responseHeaders.add("X-Strange-Value", "present")
            exchange.responseHeaders.add("Content-Type", "text/plain")
            val body = "ok".toByteArray()
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        val (relay, _) = relay(get("/hello"))
        val result = relay.exchange(16L)
        val headers = result!!.captured.responseHeaders
        val strange = headers.entries.firstOrNull { it.key.equals("X-Strange-Value", ignoreCase = true) }?.value
        assertEquals("present", strange, "headers: $headers")
        assertTrue(headers.keys.any { it.equals("Content-Type", ignoreCase = true) })
    }

    @Test
    fun `malformed request line throws`() {
        val (relay, _) = relay("GARBAGE\r\n\r\n".toByteArray(StandardCharsets.ISO_8859_1))
        assertThrows<java.io.IOException> { relay.exchange(17L) }
    }

    @Test
    fun `oversized request head throws`() {
        val huge = StringBuilder("GET /hello HTTP/1.1\r\nHost: localhost\r\n")
        while (huge.length < 40_000) huge.append("X-Pad: 0123456789\r\n")
        huge.append("\r\n")
        val (relay, _) = relay(huge.toString().toByteArray(StandardCharsets.ISO_8859_1))
        assertThrows<java.io.IOException> { relay.exchange(18L) }
    }

    @Test
    fun `bytes down equals the full wire response length`() {
        // head = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n" (33 bytes) + blank CRLF (4) + body (2) = 39
        val (port, close) = rawOrigin("HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi".toByteArray())
        try {
            val (relay, _) = relayToPort(port, get("/hello"))
            val result = relay.exchange(19L)
            // head = status line(17) + "Content-Length: 2\r\n"(19) = 36; total = 36 + 4 + body(2) = 42

        assertEquals(42L, result!!.captured.bytesDown)
            assertEquals("hi", result.captured.responseBody)
        } finally {
            close()
        }
    }

    @Test
    fun `relay exposes its original destination fields`() {
        val (relay, _) = relay(get("/hello"))
        assertEquals("10.0.0.1", relay.originalDstIp)
        assertEquals(originPort, relay.originalDstPort)
    }
}
