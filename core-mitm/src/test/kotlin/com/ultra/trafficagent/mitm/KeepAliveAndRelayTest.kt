package com.ultra.trafficagent.mitm

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket
import java.nio.charset.StandardCharsets
import java.util.concurrent.CountDownLatch
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

/**
 * End-to-end keep-alive pooling and websocket relaying through the plain
 * AUTO-mode proxy: a scripted TCP origin (not the JDK httpserver) counts
 * accepted connections so assertions can prove socket reuse.
 */
class KeepAliveAndRelayTest {

    private class Captures : CaptureListener {
        val items = CopyOnWriteArrayList<ProxyExchange>()
        override fun onExchange(exchange: ProxyExchange) {
            items.add(exchange)
        }

        fun await(count: Int, timeoutMs: Long = 10_000): List<ProxyExchange> {
            val deadline = System.currentTimeMillis() + timeoutMs
            while (items.size < count && System.currentTimeMillis() < deadline) {
                Thread.sleep(20)
            }
            return items.toList()
        }
    }

    /** Scripted keep-alive origin: answers every request on the same socket. */
    private class ScriptedOrigin {
        val server = ServerSocket(0, 50, InetAddress.getLoopbackAddress())
        val accepts = AtomicInteger(0)
        private val thread = Thread {
            while (!server.isClosed) {
                val client = try {
                    server.accept()
                } catch (_: Exception) {
                    break
                }
                accepts.incrementAndGet()
                Thread {
                    client.use { socket ->
                        socket.soTimeout = 10_000
                        try {
                            val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
                            while (true) {
                                var line = reader.readLine() ?: break
                                if (line.isEmpty()) continue
                                // Drain the head.
                                var contentLength = 0
                                while (true) {
                                    val h = reader.readLine() ?: return@Thread
                                    if (h.isEmpty()) break
                                    if (h.startsWith("Content-Length:", true)) {
                                        contentLength = h.substringAfter(':').trim().toInt()
                                    }
                                }
                                repeat(contentLength) { reader.read() }
                                val body = "ok"
                                socket.getOutputStream().write(
                                    ("HTTP/1.1 200 OK\r\nContent-Length: ${body.length}\r\n" +
                                        "Connection: keep-alive\r\n\r\n$body")
                                        .toByteArray(StandardCharsets.ISO_8859_1),
                                )
                                socket.getOutputStream().flush()
                            }
                        } catch (_: Exception) {
                        }
                    }
                }.apply { isDaemon = true }.start()
            }
        }

        init {
            thread.isDaemon = true
            thread.start()
        }

        val port: Int get() = server.localPort

        fun close() {
            server.close()
        }
    }

    /** Origin that upgrades to a websocket and echoes every byte back. */
    private class WebsocketEchoOrigin {
        val server = ServerSocket(0, 50, InetAddress.getLoopbackAddress())
        private val thread = Thread {
            val client = try {
                server.accept()
            } catch (_: Exception) {
                return@Thread
            }
            client.use { socket ->
                socket.soTimeout = 10_000
                try {
                    val head = HttpIo.readHead(socket.getInputStream()) ?: return@use
                    val body = "upgraded"
                    socket.getOutputStream().write(
                        ("HTTP/1.1 101 Switching Protocols\r\n" +
                            "Upgrade: websocket\r\n" +
                            "Connection: Upgrade\r\n" +
                            "Content-Length: 0\r\n\r\n")
                            .toByteArray(StandardCharsets.ISO_8859_1),
                    )
                    socket.getOutputStream().flush()
                    // Echo tunnel bytes until the client stops writing.
                    val buf = ByteArray(4096)
                    val input = socket.getInputStream()
                    while (true) {
                        val n = try {
                            input.read(buf)
                        } catch (_: Exception) {
                            -1
                        }
                        if (n < 0) break
                        socket.getOutputStream().write(buf, 0, n)
                        socket.getOutputStream().flush()
                    }
                } catch (_: Exception) {
                }
            }
        }

        init {
            thread.isDaemon = true
            thread.start()
        }

        val port: Int get() = server.localPort

        fun close() {
            server.close()
        }
    }

    private fun getViaProxy(proxyPort: Int, target: String): String {
        Socket("127.0.0.1", proxyPort).use { socket ->
            socket.soTimeout = 10_000
            val out = socket.getOutputStream()
            out.write(
                ("GET http://$target/ HTTP/1.1\r\nHost: $target\r\nAccept: */*\r\n\r\n")
                    .toByteArray(StandardCharsets.ISO_8859_1),
            )
            out.flush()
            val head = HttpIo.readHead(socket.getInputStream())
                ?: throw IllegalStateException("no response head")
            val headers = MutableHeaders(head.headers)
            val len = headers.get("content-length")?.toInt() ?: 0
            val body = ByteArray(len)
            var off = 0
            while (off < len) {
                val n = socket.getInputStream().read(body, off, len - off)
                if (n < 0) break
                off += n
            }
            assertEquals(200, head.status)
            return String(body, StandardCharsets.ISO_8859_1)
        }
    }

    @Test
    fun `two requests reuse one origin connection`() {
        val origin = ScriptedOrigin()
        val captures = Captures()
        val proxy = MitmProxyServer(
            port = 0,
            ca = CaCertificateAuthority(),
            config = MitmConfig(trustOriginAll = true, originKeepAlive = true),
            listener = captures,
            mode = ServeMode.AUTO,
        )
        proxy.start()
        try {
            val target = "127.0.0.1:${origin.port}"
            assertEquals("ok", getViaProxy(proxy.boundPort(), target))
            assertEquals("ok", getViaProxy(proxy.boundPort(), target))
            assertEquals(2, captures.await(2).size)
            // Both exchanges went over ONE accepted origin socket.
            assertEquals(1, origin.accepts.get())
        } finally {
            proxy.stop()
            origin.close()
        }
    }

    @Test
    fun `keep-alive can be disabled per config`() {
        val origin = ScriptedOrigin()
        val proxy = MitmProxyServer(
            port = 0,
            ca = CaCertificateAuthority(),
            config = MitmConfig(trustOriginAll = true, originKeepAlive = false),
            mode = ServeMode.AUTO,
        )
        proxy.start()
        try {
            val target = "127.0.0.1:${origin.port}"
            assertEquals("ok", getViaProxy(proxy.boundPort(), target))
            assertEquals("ok", getViaProxy(proxy.boundPort(), target))
            assertEquals(2, origin.accepts.get())
        } finally {
            proxy.stop()
            origin.close()
        }
    }

    @Test
    fun `websocket upgrade relays frames in both directions`() {
        val origin = WebsocketEchoOrigin()
        val captures = Captures()
        val proxy = MitmProxyServer(
            port = 0,
            ca = CaCertificateAuthority(),
            config = MitmConfig(trustOriginAll = true, wsIdleTimeoutMs = 5_000),
            listener = captures,
            mode = ServeMode.AUTO,
        )
        proxy.start()
        try {
            Socket("127.0.0.1", proxy.boundPort()).use { socket ->
                socket.soTimeout = 10_000
                val out = socket.getOutputStream()
                // Upgrade request through the proxy.
                out.write(
                    ("GET http://127.0.0.1:${origin.port}/chat HTTP/1.1\r\n" +
                        "Host: 127.0.0.1:${origin.port}\r\n" +
                        "Upgrade: websocket\r\nConnection: Upgrade\r\n" +
                        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n" +
                        "Sec-WebSocket-Version: 13\r\n\r\n")
                        .toByteArray(StandardCharsets.ISO_8859_1),
                )
                out.flush()

                val head = HttpIo.readHead(socket.getInputStream())
                    ?: throw IllegalStateException("no upgrade response")
                assertEquals(101, head.status)
                val upgradeHeaders = MutableHeaders(head.headers)
                assertEquals("websocket", upgradeHeaders.get("upgrade")?.lowercase())
                // The Upgrade/Connection headers survived hop-by-hop filtering.
                assertTrue(upgradeHeaders.get("connection")?.contains("upgrade", true) == true)
                // No Content-Length on a 101 (it would kill the tunnel).
                assertEquals(null, upgradeHeaders.get("content-length"))

                // Frames after the upgrade must be relayed to the echo origin
                // and the echo must come back.
                val frame = byteArrayOf(
                    0x81.toByte(), 0x03.toByte(),
                    'h'.code.toByte(), 'i'.code.toByte(), '!'.code.toByte(),
                )
                out.write(frame)
                out.flush()
                val echoed = ByteArray(frame.size)
                val input = socket.getInputStream()
                var off = 0
                while (off < echoed.size) {
                    val n = input.read(echoed, off, echoed.size - off)
                    if (n < 0) break
                    off += n
                }
                assertTrue(echoed.contentEquals(frame))

                // The 101 handshake landed in the capture list.
                val exchanges = captures.await(1)
                assertEquals(1, exchanges.size)
                assertEquals(101, exchanges[0].status ?: 0)
            }
        } finally {
            proxy.stop()
            origin.close()
        }
    }
}
