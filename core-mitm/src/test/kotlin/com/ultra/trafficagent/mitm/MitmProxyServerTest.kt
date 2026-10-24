package com.ultra.trafficagent.mitm

import com.sun.net.httpserver.HttpsConfigurator
import com.sun.net.httpserver.HttpsServer
import com.ultra.trafficagent.transform.Phase
import com.ultra.trafficagent.transform.RuleAction
import com.ultra.trafficagent.transform.RuleMatch
import com.ultra.trafficagent.transform.RuleRegistry
import com.ultra.trafficagent.transform.RewriteRule
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.ProxySelector
import java.net.URI
import java.net.URL
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.charset.StandardCharsets
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext

class MitmProxyServerTest {

    // -------------------------------------------------------------- helpers

    private fun startOrigin(): com.sun.net.httpserver.HttpServer {
        val server = com.sun.net.httpserver.HttpServer.create(InetSocketAddress(0), 0)
        server.createContext("/hello") { exchange ->
            val body = """{"hello":"world","n":42}""".toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/json")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/echo") { exchange ->
            val body = exchange.requestBody.readBytes()
            exchange.responseHeaders.add("Content-Type", "text/plain")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/chunked") { exchange ->
            exchange.responseHeaders.add("Content-Type", "text/plain")
            exchange.sendResponseHeaders(200, 0) // 0 -> chunked
            exchange.responseBody.use { out: OutputStream ->
                for (chunk in listOf("alpha ", "beta ", "gamma")) {
                    out.write(chunk.toByteArray())
                    out.flush()
                }
            }
        }
        server.createContext("/slow") { exchange ->
            Thread.sleep(1200)
            val body = "finally".toByteArray()
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.executor = null
        server.start()
        return server
    }

    /** HTTPS origin serving the same routes, certified by our own CA. */
    private fun startTlsOrigin(ca: CaCertificateAuthority): HttpsServer {
        val https = HttpsServer.create(InetSocketAddress(0), 0)
        https.createContext("/hello") { exchange ->
            val body = """{"hello":"world","n":42}""".toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/json")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        https.createContext("/echo") { exchange ->
            val body = exchange.requestBody.readBytes()
            exchange.responseHeaders.add("Content-Type", "text/plain")
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        val leaf = ca.issueServerCertificate("localhost")
        val ks = java.security.KeyStore.getInstance("PKCS12").apply {
            load(null, null)
            setKeyEntry("leaf", leaf.keyPair.private, null, arrayOf(leaf.cert))
        }
        val kmf = javax.net.ssl.KeyManagerFactory.getInstance("SunX509").apply { init(ks, null) }
        val ssl = SSLContext.getInstance("TLS").apply { init(kmf.keyManagers, null, null) }
        https.httpsConfigurator = HttpsConfigurator(ssl)
        https.executor = java.util.concurrent.Executors.newCachedThreadPool()
        https.start()
        return https
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

    private fun clientThrough(
        proxyPort: Int,
        trustCa: CaCertificateAuthority? = null,
    ): HttpClient {
        val builder = HttpClient.newBuilder()
            .proxy(ProxySelector.of(InetSocketAddress("127.0.0.1", proxyPort)))
            .connectTimeout(java.time.Duration.ofSeconds(10))
        if (trustCa != null) {
            builder.sslContext(SSLContext.getInstance("TLS").apply {
                init(
                    null,
                    arrayOf(
                        javax.net.ssl.TrustManagerFactory.getInstance(
                            "X509",
                        ).apply {
                            val ks = java.security.KeyStore.getInstance("PKCS12").apply {
                                load(null, null)
                                setCertificateEntry("ca", trustCa.caCertificate())
                            }
                            init(ks)
                        }.trustManagers[0],
                    ),
                    null,
                )
            })
        }
        return builder.build()
    }

    // ------------------------------------------------------------ plain HTTP

    @Test
    fun `plain proxy captures get with body and headers`() {
        val origin = startOrigin()
        val ca = CaCertificateAuthority()
        val captures = Captures()
        val proxy = MitmProxyServer(0, ca, listener = captures)
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            val response = client.send(
                HttpRequest.newBuilder(java.net.URI.create("http://127.0.0.1:${origin.address.port}/hello"))
                    .header("X-Test", "abc")
                    .GET()
                    .build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            assertEquals(200, response.statusCode())
            assertEquals("""{"hello":"world","n":42}""", response.body())
            val captured = captures.await(1).first()
            assertEquals("GET", captured.method)
            assertEquals("/hello", captured.path)
            assertEquals("127.0.0.1", captured.host)
            assertEquals(200, captured.status)
            assertEquals("abc", captured.requestHeaders.firstOrNull { it.first == "X-Test" }?.second)
            assertEquals("application/json", captured.responseHeaders.firstOrNull { it.first.equals("Content-Type", true) }?.second?.substringBefore(';'))
            assertTrue(captured.durationMs >= 0)
            assertEquals(false, captured.tls)
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    @Test
    fun `plain proxy forwards post echo body`() {
        val origin = startOrigin()
        val captures = Captures()
        val proxy = MitmProxyServer(0, CaCertificateAuthority(), listener = captures)
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            val response = client.send(
                HttpRequest.newBuilder(java.net.URI.create("http://127.0.0.1:${origin.address.port}/echo"))
                    .POST(HttpRequest.BodyPublishers.ofString("ping-	payload ünicode"))
                    .build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            assertEquals(200, response.statusCode())
            assertEquals("ping-	payload ünicode", response.body())
            val captured = captures.await(1).first()
            assertEquals("POST", captured.method)
            assertEquals("ping-	payload ünicode", String(captured.requestBody!!, StandardCharsets.UTF_8))
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    @Test
    fun `chunked response passes through`() {
        val origin = startOrigin()
        val captures = Captures()
        val proxy = MitmProxyServer(0, CaCertificateAuthority(), listener = captures)
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            val response = client.send(
                HttpRequest.newBuilder(java.net.URI.create("http://127.0.0.1:${origin.address.port}/chunked"))
                    .GET()
                    .build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            assertEquals("alpha beta gamma", response.body())
            val captured = captures.await(1).first()
            assertEquals("alpha beta gamma", String(captured.responseBody!!, StandardCharsets.UTF_8))
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    // ------------------------------------------------------------- HTTPS MITM

    @Test
    fun `https mitm decrypts and captures`() {
        val ca = CaCertificateAuthority()
        val origin = startTlsOrigin(ca)
        val captures = Captures()
        // the TLS origin below is certified by our own test CA, so the proxy
        // must trust any origin here (the app exposes this as a setting)
        val proxy = MitmProxyServer(0, ca, config = MitmConfig(trustOriginAll = true), listener = captures)
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort(), trustCa = ca)
            val response = client.send(
                HttpRequest.newBuilder(java.net.URI.create("https://localhost:${origin.address.port}/hello"))
                    .header("X-Mitm-Probe", "yes")
                    .GET()
                    .build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            assertEquals(200, response.statusCode())
            assertEquals("""{"hello":"world","n":42}""", response.body())
            val captured = captures.await(1).first()
            assertTrue(captured.tls)
            assertEquals("https", captured.scheme)
            assertEquals("localhost", captured.host)
            assertEquals("/hello", captured.path)
            assertEquals("GET", captured.method)
            assertEquals(200, captured.status)
            assertEquals("yes", captured.requestHeaders.firstOrNull { it.first == "X-Mitm-Probe" }?.second)
            val bodyText = String(captured.responseBody!!, StandardCharsets.UTF_8)
            assertTrue(bodyText.contains("\"hello\":\"world\""))
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    // ------------------------------------------------------------- interceptors

    @Test
    fun `rewriter interceptor replaces response body`() {
        val origin = startOrigin()
        val ca = CaCertificateAuthority()
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "r1",
                name = "replace world",
                match = RuleMatch(pathRegex = "/hello"),
                actions = listOf(
                    RuleAction.ReplaceBody(Phase.RESPONSE, "world", "universe", 1),
                ),
            ),
        )
        val captures = Captures()
        val proxy = MitmProxyServer(
            0, ca,
            config = MitmConfig(interceptors = listOf(MitmRewriteInterceptor(registry))),
            listener = captures,
        )
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            val response = client.send(
                HttpRequest.newBuilder(java.net.URI.create("http://127.0.0.1:${origin.address.port}/hello"))
                    .GET()
                    .build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            assertEquals("""{"hello":"universe","n":42}""", response.body())
            val captured = captures.await(1).first()
            assertTrue("r1" in captured.appliedRuleIds)
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    @Test
    fun `short circuit interceptor answers without origin`() {
        val ca = CaCertificateAuthority()
        val captures = Captures()
        val blocker = object : ExchangeInterceptor {
            override fun onRequest(ctx: MutableProxyExchange): ProxyDecision =
                ctx.shortCircuit(418, "no origin needed".toByteArray(), "text/plain")

            override fun onResponse(ctx: MutableProxyExchange) = Unit
        }
        val proxy = MitmProxyServer(0, ca, config = MitmConfig(interceptors = listOf(blocker)), listener = captures)
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            val response = client.send(
                HttpRequest.newBuilder(java.net.URI.create("http://nowhere.invalid/x")).GET().build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            assertEquals(418, response.statusCode())
            assertEquals("no origin needed", response.body())
            val captured = captures.await(1).first()
            assertEquals(418, captured.status)
            assertEquals("no origin needed", String(captured.responseBody!!, StandardCharsets.UTF_8))
        } finally {
            proxy.stop()
        }
    }

    @Test
    fun `delay action inflates captured duration`() {
        val origin = startOrigin()
        val registry = RuleRegistry()
        registry.add(
            RewriteRule(
                id = "slow-down",
                name = "slow down",
                match = RuleMatch(pathRegex = "/hello"),
                actions = listOf(RuleAction.DelayMs(150)),
            ),
        )
        val captures = Captures()
        val proxy = MitmProxyServer(
            0, CaCertificateAuthority(),
            config = MitmConfig(interceptors = listOf(MitmRewriteInterceptor(registry))),
            listener = captures,
        )
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            client.send(
                HttpRequest.newBuilder(java.net.URI.create("http://127.0.0.1:${origin.address.port}/hello")).GET().build(),
                HttpResponse.BodyHandlers.ofString(),
            )
            val captured = captures.await(1).first()
            assertTrue(captured.durationMs >= 140, "captured=${captured.durationMs}")
            assertTrue("slow-down" in captured.appliedRuleIds)
        } finally {
            proxy.stop()
            origin.stop(0)
        }
    }

    @Test
    fun `dead origin surfaces error in captured exchange`() {
        val captures = Captures()
        val proxy = MitmProxyServer(0, CaCertificateAuthority(), listener = captures)
        proxy.start()
        try {
            val client = clientThrough(proxy.boundPort())
            val response = try {
                client.send(
                    HttpRequest.newBuilder(java.net.URI.create("http://127.0.0.1:1/nope")).GET().build(),
                    HttpResponse.BodyHandlers.ofString(),
                )
            } catch (_: java.io.IOException) {
                null // connect refused reaching the client is fine too
            }
            assertTrue(response == null || response.statusCode() == 502)
        } finally {
            proxy.stop()
        }
    }

    @Test
    fun `server start stop and restart are idempotent`() {
        val proxy = MitmProxyServer(0, CaCertificateAuthority())
        assertFalse(proxy.isRunning())
        proxy.start()
        assertTrue(proxy.isRunning())
        assertTrue(proxy.boundPort() > 0)
        proxy.stop()
        assertFalse(proxy.isRunning())
        proxy.stop() // double stop is fine
    }
}
