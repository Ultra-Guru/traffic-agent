package com.ultra.trafficagent.capture

import com.sun.net.httpserver.HttpServer
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.net.InetSocketAddress
import java.net.URI
import java.nio.charset.StandardCharsets
import java.util.concurrent.Executors

class ReplayEngineTest {

    private fun origin(): HttpServer {
        val server = HttpServer.create(InetSocketAddress(0), 0)
        server.createContext("/json") { exchange ->
            val body = """{"replayed":true}""".toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/json")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/echo") { exchange ->
            val body = exchange.requestBody.readBytes()
            assertEquals("x-replay-token", exchange.requestHeaders.getFirst("X-Probe"))
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/missing") { exchange ->
            // -1: no response body (0 would require closing an empty stream)
            exchange.sendResponseHeaders(404, -1)
        }
        server.executor = Executors.newCachedThreadPool()
        server.start()
        return server
    }

    private fun captured(host: String, port: Int, path: String, method: String = "GET", body: String = "") =
        CapturedRequest(
            id = 1,
            timestampMs = 0,
            host = host,
            path = path,
            method = method,
            status = 200,
            requestHeaders = mapOf("X-Probe" to "x-replay-token"),
            responseHeaders = emptyMap(),
            requestBody = body,
            responseBody = "",
            bytesUp = 10,
            bytesDown = 10,
            protocol = Protocol.HTTP1,
            appUid = null,
        )

    @Test
    fun `replays a get and returns the response`() {
        val server = origin()
        try {
            val engine = ReplayEngine()
            val result = engine.replay(
                captured("127.0.0.1", 0, "/json").copy(
                    path = "/json",
                    // ReplayEngine builds the URL from the capture; force the origin port
                    requestHeaders = mapOf("X-Probe" to "x-replay-token"),
                ),
                ReplayOverrides(url = "http://127.0.0.1:${server.address.port}/json"),
            )
            assertNull(result.error)
            assertEquals(200, result.status)
            assertEquals("""{"replayed":true}""", String(result.body!!, StandardCharsets.UTF_8))
            assertTrue(result.durationMs >= 0)
            assertNotNull(result.requestUrl)
        } finally {
            server.stop(0)
        }
    }

    @Test
    fun `replays a post with body and custom headers`() {
        val server = origin()
        try {
            val engine = ReplayEngine()
            val result = engine.replay(
                captured("127.0.0.1", 0, "/echo", method = "POST", body = "replayed-payload"),
                ReplayOverrides(url = "http://127.0.0.1:${server.address.port}/echo"),
            )
            assertNull(result.error)
            assertEquals(200, result.status)
            assertEquals("replayed-payload", String(result.body!!, StandardCharsets.UTF_8))
        } finally {
            server.stop(0)
        }
    }

    @Test
    fun `404 surfaces the status`() {
        val server = origin()
        try {
            val result = ReplayEngine().replay(
                captured("127.0.0.1", 0, "/missing"),
                ReplayOverrides(url = "http://127.0.0.1:${server.address.port}/missing"),
            )
            assertEquals(404, result.status)
            assertNull(result.error)
        } finally {
            server.stop(0)
        }
    }

    @Test
    fun `unreachable origin returns error not throw`() {
        val result = ReplayEngine(ReplayConfig(connectTimeoutMs = 500)).replay(
            captured("127.0.0.1", 0, "/x"),
            ReplayOverrides(url = "http://127.0.0.1:1/x"),
        )
        assertNull(result.status)
        assertNotNull(result.error)
    }
}
