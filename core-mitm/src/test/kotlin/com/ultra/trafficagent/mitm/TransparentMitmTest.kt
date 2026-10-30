package com.ultra.trafficagent.mitm

import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.BufferedWriter
import java.io.OutputStreamWriter
import java.net.InetSocketAddress
import java.net.Socket
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.security.KeyStore
import java.security.SecureRandom
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocket
import javax.net.ssl.TrustManagerFactory

/**
 * Transparent-mode interception: the VPN forwarding stack redirects client
 * TCP flows to the local proxy, so clients arrive WITHOUT a CONNECT
 * preamble — either a raw TLS handshake (0x16) or a relative-form HTTP
 * request. These tests reproduce exactly that wiring.
 */
class TransparentMitmTest {

    private fun startPlainOrigin(): com.sun.net.httpserver.HttpServer {
        val server = com.sun.net.httpserver.HttpServer.create(InetSocketAddress(0), 0)
        server.createContext("/hello") { exchange ->
            val body = """{"hello":"transparent"}""".toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/json")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.executor = null
        server.start()
        return server
    }

    private fun startTlsOrigin(ca: CaCertificateAuthority): com.sun.net.httpserver.HttpsServer {
        val https = com.sun.net.httpserver.HttpsServer.create(InetSocketAddress(0), 0)
        https.createContext("/hello") { exchange ->
            val body = """{"hello":"tls-transparent"}""".toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/json")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        val leaf = ca.issueServerCertificate("localhost")
        val ks = KeyStore.getInstance("PKCS12").apply {
            load(null, null)
            setKeyEntry("leaf", leaf.keyPair.private, null, arrayOf(leaf.cert))
        }
        val kmf = javax.net.ssl.KeyManagerFactory.getInstance("SunX509").apply { init(ks, null) }
        val ssl = SSLContext.getInstance("TLS").apply { init(kmf.keyManagers, null, null) }
        https.httpsConfigurator = com.sun.net.httpserver.HttpsConfigurator(ssl)
        https.executor = java.util.concurrent.Executors.newCachedThreadPool()
        https.start()
        return https
    }

    /** SSLContext that trusts only the given CA (the "user installed the cert" stance). */
    private fun trusting(ca: CaCertificateAuthority): SSLContext {
        val ks = KeyStore.getInstance("PKCS12").apply {
            load(null, null)
            setCertificateEntry("ca", ca.caCertificate())
        }
        val tmf = TrustManagerFactory.getInstance("X509").apply { init(ks) }
        return SSLContext.getInstance("TLS").apply {
            init(null, tmf.trustManagers, SecureRandom())
        }
    }

    private class Captures : CaptureListener {
        val items = java.util.concurrent.CopyOnWriteArrayList<ProxyExchange>()
        override fun onExchange(exchange: ProxyExchange) {
            items.add(exchange)
        }

        fun await(count: Int = 1, timeoutMs: Long = 10_000): List<ProxyExchange> {
            val deadline = System.nanoTime() + timeoutMs * 1_000_000
            while (items.size < count) {
                if (System.nanoTime() > deadline) return items.toList()
                Thread.sleep(20)
            }
            return items.toList()
        }
    }

    /** Reads one full HTTP/1.x response: head block + exactly Content-Length bytes. */
    private fun readHttpResponse(input: java.io.InputStream): Pair<String, ByteArray> {
        val head = StringBuilder()
        while (true) {
            val c = input.read()
            if (c < 0) break
            head.append(c.toChar())
            if (head.length >= 4 && head.endsWith("\r\n\r\n")) break
        }
        val text = head.toString()
        val length = Regex("Content-Length:\\s*(\\d+)", RegexOption.IGNORE_CASE)
            .find(text)?.groupValues?.get(1)?.toIntOrNull() ?: 0
        val body = if (length > 0) input.readNBytes(length) else ByteArray(0)
        return text to body
    }

    @Test
    fun `transparent plain http flow is captured`() {
        val origin = startPlainOrigin()
        val ca = CaCertificateAuthority()
        val captures = Captures()
        val proxy = MitmProxyServer(0, ca, listener = captures)
        proxy.start()
        try {
            // The client believes it talks to localhost:<originPort> — bytes
            // land on the proxy (VPN redirection).
            Socket("127.0.0.1", proxy.boundPort()).use { sock ->
                sock.soTimeout = 10_000
                val out = BufferedWriter(OutputStreamWriter(sock.getOutputStream(), StandardCharsets.ISO_8859_1))
                out.write("GET /hello HTTP/1.1\r\n")
                out.write("Host: localhost:${origin.address.port}\r\n")
                out.write("Connection: close\r\n\r\n")
                out.flush()
                val (head, body) = readHttpResponse(sock.getInputStream())
                assertTrue(head.startsWith("HTTP/1.1 200"), "unexpected head: ${head.take(40)}")
                assertTrue(body.size > 0)
            }

            val captured = captures.await(1)
            assertEquals(1, captured.size)
            val ex = captured[0]
            assertEquals("localhost", ex.host)
            assertEquals(origin.address.port, ex.port)
            assertEquals("GET", ex.method)
            assertEquals("/hello", ex.path)
            assertEquals(200, ex.status)
            assertFalse(ex.tls)
            assertEquals("""{"hello":"transparent"}""", String(ex.responseBody ?: ByteArray(0)))
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    @Test
    fun `transparent tls flow is decrypted and captured`() {
        val ca = CaCertificateAuthority()
        val origin = startTlsOrigin(ca)
        val captures = Captures()
        val proxy = MitmProxyServer(
            0, ca,
            config = MitmConfig(trustOriginAll = true),  // origin is certified by our own test CA
            listener = captures,
            mode = ServeMode.TRANSPARENT_TLS,
        )
        proxy.start()
        try {
            val clientContext = trusting(ca)
            // Redirected client: raw socket to the proxy, TLS handshake with
            // SNI "localhost", Host header naming the *origin* port.
            val raw = Socket("127.0.0.1", proxy.boundPort())
            raw.soTimeout = 15_000
            val tls = clientContext.socketFactory
                .createSocket(raw, "localhost", origin.address.port, true) as SSLSocket
            tls.use {
                tls.startHandshake()
                val out = tls.getOutputStream()
                out.write(
                    ("GET /hello HTTP/1.1\r\nHost: localhost:${origin.address.port}\r\n" +
                        "Connection: close\r\n\r\n").toByteArray(StandardCharsets.ISO_8859_1),
                )
                out.flush()
                val (head, body) = readHttpResponse(tls.getInputStream())
                assertTrue(head.startsWith("HTTP/1.1 200"), "unexpected head: ${head.take(40)}")
                assertEquals("""{"hello":"tls-transparent"}""", String(body))
            }

            val captured = captures.await(1)
            assertEquals(1, captured.size)
            val ex = captured[0]
            assertEquals("localhost", ex.host)
            assertEquals("GET", ex.method)
            assertEquals("/hello", ex.path)
            assertEquals(200, ex.status)
            assertTrue(ex.tls)
            assertEquals("https", ex.scheme)
            assertEquals("""{"hello":"tls-transparent"}""", String(ex.responseBody ?: ByteArray(0)))
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    @Test
    fun `ca survives pkcs12 roundtrip and keeps issuing leaves`() {
        val dir = Files.createTempDirectory("ta-ca-test")
        val file = dir.resolve("ca.p12").toFile()
        val password = "test-password".toCharArray()

        val original = CaCertificateAuthority()
        original.saveKeyStore(file, password)

        assertTrue(file.exists() && file.length() > 0)
        val restored = CaCertificateAuthority.fromKeyStore(file, password)

        assertEquals(original.caCertificatePem(), restored.caCertificatePem())
        assertArrayEquals(original.caCertificate().encoded, restored.caCertificate().encoded)

        // Leaves issued by the restored CA must chain to the same original
        // certificate (same signing key), i.e. trust established before the
        // restart still validates.
        val leaf = restored.issueServerCertificate("persisted.example.com")
        leaf.cert.verify(original.caCertificate().publicKey)
    }
}
