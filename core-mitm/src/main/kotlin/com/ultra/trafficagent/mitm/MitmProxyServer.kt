package com.ultra.trafficagent.mitm

import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.ByteArrayOutputStream
import java.io.EOFException
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket
import java.util.Locale
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.zip.GZIPInputStream
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocket

/** Tuning knobs for [MitmProxyServer]. */
data class MitmConfig(
    /** Bodies beyond this many bytes are clipped in the captured exchange. */
    val captureMaxBodyBytes: Long = 1 shl 20,
    val connectTimeoutMs: Int = 8_000,
    val soTimeoutMs: Int = 30_000,
    val workers: Int = 8,
    /** Trust every origin certificate (capture tooling; App toggles it). */
    val trustOriginAll: Boolean = false,
    val interceptors: List<ExchangeInterceptor> = emptyList(),
) {
    init {
        require(captureMaxBodyBytes >= 0) { "captureMaxBodyBytes must not be negative" }
        require(connectTimeoutMs > 0) { "connectTimeoutMs must be positive" }
        require(workers > 0) { "workers must be positive" }
    }
}

/**
 * Android hook: the app layer injects `VpnService.protect(socket)` here so
 * origin sockets bypass the VPN tunnel (prevents routing loops). The JVM
 * default is a no-op.
 */
fun interface SocketProtector {
    fun protect(socket: Socket)

    companion object {
        val NONE: SocketProtector = SocketProtector { }
    }
}

/**
 * HTTPS MITM proxy (HttpCanary-style capture core, pure JDK).
 *
 * Supports CONNECT tunnelling with TLS termination (leaf certificates are
 * issued on the fly from [CaCertificateAuthority] with SNI awareness) plus
 * plain absolute-form HTTP proxying. Every finished request/response pair is
 * handed to [listener]; interceptors can rewrite or short-circuit exchanges.
 */
class MitmProxyServer(
    private val port: Int,
    private val ca: CaCertificateAuthority,
    private val config: MitmConfig = MitmConfig(),
    private val listener: CaptureListener? = null,
    private val socketProtector: SocketProtector = SocketProtector.NONE,
) {
    init {
        require(port in 0..65535) { "port must be 0..65535" }
    }

    private val running = AtomicBoolean(false)
    private val captured = AtomicLong(0)
    private var serverSocket: ServerSocket? = null
    private var acceptThread: Thread? = null
    private var pool = Executors.newFixedThreadPool(config.workers) { r ->
        Thread(r, "mitm-worker").apply { isDaemon = true }
    }
    private val serverContext: SSLContext = TlsContexts.serverContext(ca)
    private val originContext: SSLContext = TlsContexts.originContext(config.trustOriginAll)

    /** Starts accepting connections; port 0 binds an ephemeral port. */
    fun start() {
        if (!running.compareAndSet(false, true)) return
        val ss = ServerSocket()
        ss.reuseAddress = true
        ss.bind(InetSocketAddress(port))
        serverSocket = ss
        pool = Executors.newFixedThreadPool(config.workers) { r ->
            Thread(r, "mitm-worker").apply { isDaemon = true }
        }
        acceptThread = Thread({ acceptLoop(ss) }, "mitm-accept").apply {
            isDaemon = true
            start()
        }
    }

    fun stop() {
        if (!running.compareAndSet(true, false)) return
        try {
            serverSocket?.close()
        } catch (_: IOException) {
        }
        acceptThread?.interrupt()
        pool.shutdownNow()
    }

    fun isRunning(): Boolean = running.get()

    /** The port actually bound (useful with port = 0). */
    fun boundPort(): Int = serverSocket?.localPort ?: -1

    fun capturedCount(): Long = captured.get()

    // ------------------------------------------------------------------ accept

    private fun acceptLoop(ss: ServerSocket) {
        while (running.get()) {
            val client = try {
                ss.accept()
            } catch (_: IOException) {
                break
            }
            try {
                client.soTimeout = config.soTimeoutMs
                client.tcpNoDelay = true
            } catch (_: IOException) {
            }
            val worker = Runnable { runConnection(client) }
            try {
                pool.execute(worker)
            } catch (_: RuntimeException) {
                try {
                    client.close()
                } catch (_: IOException) {
                }
            }
        }
    }

    // -------------------------------------------------------------- connection

    private fun runConnection(client: Socket) {
        try {
            val input = BufferedInputStream(client.getInputStream(), 16 * 1024)
            val output = BufferedOutputStream(client.getOutputStream(), 16 * 1024)
            val firstLine = HttpIo.readLine(input) ?: return
            if (firstLine.startsWith("CONNECT ", ignoreCase = true)) {
                handleTunnel(client, input, output, firstLine)
            } else {
                handlePlainProxying(input, output, firstLine)
            }
        } catch (_: IOException) {
            // client vanished mid-conversation: nothing to salvage
        } finally {
            try {
                client.close()
            } catch (_: IOException) {
            }
        }
    }

    /** CONNECT host:port — terminate TLS locally, keep HTTP/1.1 inside. */
    private fun handleTunnel(client: Socket, input: InputStream, output: OutputStream, requestLine: String) {
        val target = requestLine.removePrefix("CONNECT").trim().substringBefore(' ')
        val host = target.substringBeforeLast(':')
        val port = target.substringAfterLast(':').toIntOrNull() ?: 443
        output.write("HTTP/1.1 200 Connection Established\r\n\r\n".toByteArray(Charsets.ISO_8859_1))
        output.flush()

        val tlsClient = serverContext.socketFactory.createSocket(
            client, host, client.port, true,
        ) as SSLSocket
        // Layered sockets default to client mode; we are the server.
        tlsClient.useClientMode = false
        tlsClient.use {
            tlsClient.startHandshake()
            val tlsInput = tlsClient.inputStream
            val tlsOutput = tlsClient.outputStream
            serveRequests(
                clientInput = tlsInput,
                clientOutput = tlsOutput,
                scheme = "https",
                defaultHost = host,
                defaultPort = port,
                tls = true,
                firstLine = HttpIo.readLine(tlsInput) ?: return,
            )
        }
    }

    /** Absolute-form proxying (`GET http://host/path`) on a plain socket. */
    private fun handlePlainProxying(input: InputStream, output: OutputStream, firstLine: String) {
        // Relative form without Host is unusable for a proxy.
        serveRequests(
            clientInput = input,
            clientOutput = output,
            scheme = "http",
            defaultHost = "",
            defaultPort = 80,
            tls = false,
            firstLine = firstLine,
        )
    }

    private fun serveRequests(
        clientInput: InputStream,
        clientOutput: OutputStream,
        scheme: String,
        defaultHost: String,
        defaultPort: Int,
        tls: Boolean,
        firstLine: String,
    ) {
        var line: String? = firstLine
        while (line != null) {
            val head = HttpIo.readHead(clientInput, line) ?: break
            if (!serveOne(clientInput, clientOutput, scheme, defaultHost, defaultPort, tls, head)) break
            try {
                line = HttpIo.readLine(clientInput)
            } catch (_: IOException) {
                break
            }
        }
    }

    /**
     * Serves one request/response cycle. Returns false when the client
     * connection should be dropped.
     */
    private fun serveOne(
        clientInput: InputStream,
        clientOutput: OutputStream,
        scheme: String,
        defaultHost: String,
        defaultPort: Int,
        tls: Boolean,
        head: HttpIo.Head,
    ): Boolean {
        val started = System.nanoTime()
        val headers = MutableHeaders(head.headers)
        val host = headers.get("host")?.substringBefore(':') ?: defaultHost.ifEmpty { return false }
        var effectivePort = headers.get("host")?.substringAfterLast(':')?.toIntOrNull() ?: defaultPort
        var path = head.target
        var upstreamScheme = scheme
        var upstreamHost = host
        var upstreamPort = effectivePort
        // absolute-form target overrides the Host header
        val absolute = Regex("^https?://([^/]+)(/.*)?$").find(head.target)
        if (absolute != null) {
            upstreamHost = absolute.groupValues[1].substringBeforeLast(':')
            upstreamPort = absolute.groupValues[1].substringAfterLast(':').toIntOrNull() ?: 443
            upstreamScheme = if (head.target.startsWith("https", true)) "https" else "http"
            path = absolute.groupValues[2].ifEmpty { "/" }
            effectivePort = upstreamPort
        }
        if (upstreamHost.isEmpty()) return false

        val ctx = MutableProxyExchange(
            scheme = upstreamScheme,
            host = upstreamHost,
            port = upstreamPort,
            method = head.method,
            path = path,
            requestHeaders = MutableHeaders(head.headers),
            requestBody = readRequestBody(clientInput, headers),
        )

        val exchangeId = captured.incrementAndGet()
        var decision: ProxyDecision = ProxyDecision.Forward
        var interceptorError: String? = null
        for (interceptor in config.interceptors) {
            try {
                val d = interceptor.onRequest(ctx)
                if (d is ProxyDecision.ShortCircuit) {
                    decision = d
                    break
                }
            } catch (e: Exception) {
                interceptorError = "interceptor: ${e.message}"
            }
        }

        var status: Int? = null
        var responseHeaders = MutableHeaders()
        var responseBody: ByteArray? = null
        var requestBytes: Long = head.raw.size.toLong() + (ctx.requestBody?.size ?: 0)
        var responseBytes = 0L
        var error: String? = interceptorError

        if (decision is ProxyDecision.ShortCircuit) {
            status = decision.status
            responseHeaders.add("Content-Type", decision.contentType)
            responseHeaders.add("Content-Length", decision.body.size.toString())
            responseHeaders.add("X-Mitm", "short-circuit")
            responseBody = decision.body
            responseBytes = decision.body.size.toLong()
            HttpIo.writeResponse(clientOutput, status, "MITM", responseHeaders, responseBody)
        } else {
            // ---- forward to origin: fresh connection per request ----
            try {
                val origin = openOrigin(ctx.host, ctx.port, upstreamScheme)
                origin.use { socket ->
                val originOut = socket.getOutputStream()
                val originIn = socket.getInputStream()
                HttpIo.writeRequest(
                    originOut, ctx.method, ctx.path, ctx.host,
                    ctx.requestHeaders, ctx.requestBody,
                )
                val respHead = HttpIo.readHead(originIn) ?: throw EOFException("origin closed")
                val respHeaders = MutableHeaders(respHead.headers)
                status = respHead.status
                val bodiless = ctx.method.equals("HEAD", true) ||
                    status in 204..205 || status == 304 || status in 100..199
                val raw = if (bodiless) ByteArray(0) else readResponseBody(originIn, respHeaders)
                responseHeaders = respHeaders
                responseBody = raw
                responseBytes = respHead.raw.size + raw.size.toLong()
                if (config.interceptors.isNotEmpty()) {
                    ctx.status = status
                    ctx.responseHeaders.replaceWith(respHeaders)
                    ctx.responseBody = raw
                    for (interceptor in config.interceptors) {
                        try {
                            interceptor.onResponse(ctx)
                        } catch (e: Exception) {
                            if (error == null) error = "interceptor: ${e.message}"
                        }
                    }
                    status = ctx.status
                    responseHeaders = ctx.responseHeaders
                    responseBody = ctx.responseBody ?: raw
                }
                HttpIo.writeResponse(clientOutput, status, reasonFor(status), responseHeaders, responseBody)
                }
            } catch (e: IOException) {
                error = e.message ?: e.javaClass.simpleName
                try {
                    clientOutput.write(
                        "HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                            .toByteArray(Charsets.ISO_8859_1),
                    )
                    clientOutput.flush()
                } catch (_: IOException) {
                }
                emit(
                    exchangeId, started, ctx, null, status, responseHeaders, responseBody,
                    requestBytes, responseBytes, tls, error,
                )
                return false
            }
        }

        emit(
            exchangeId, started, ctx, decision, status, responseHeaders, responseBody,
            requestBytes, responseBytes, tls, error,
        )
        return true
    }

    private fun emit(
        exchangeId: Long,
        started: Long,
        ctx: MutableProxyExchange,
        decision: ProxyDecision?,
        status: Int?,
        responseHeaders: MutableHeaders,
        responseBody: ByteArray?,
        requestBytes: Long,
        responseBytes: Long,
        tls: Boolean,
        error: String?,
    ) {
        val durationMs = (System.nanoTime() - started) / 1_000_000
        val exchange = ProxyExchange(
            id = exchangeId,
            timestampMs = System.currentTimeMillis(),
            scheme = ctx.scheme,
            host = ctx.host,
            port = ctx.port,
            method = ctx.method,
            path = ctx.path,
            requestHeaders = ctx.requestHeaders.toList(),
            requestBody = clip(ctx.requestBody),
            status = status,
            responseHeaders = responseHeaders.toList(),
            responseBody = clip(responseBody),
            responseDecodedBody = decodeBody(responseBody, responseHeaders.get("content-encoding")),
            requestBytes = requestBytes,
            responseBytes = responseBytes,
            durationMs = durationMs,
            tls = tls,
            appliedRuleIds = ctx.appliedRuleIds.toList(),
            error = error,
            truncated = (responseBody?.size ?: 0) > config.captureMaxBodyBytes ||
                (ctx.requestBody?.size ?: 0) > config.captureMaxBodyBytes,
        )
        if (listener != null) {
            try {
                listener.onExchange(exchange)
            } catch (_: RuntimeException) {
            }
        }
    }

    /** Opens a plain or TLS connection to the origin (protected via [socketProtector]). */
    private fun openOrigin(host: String, port: Int, scheme: String): Socket {
        val plain = Socket()
        socketProtector.protect(plain)
        plain.tcpNoDelay = true
        plain.connect(InetSocketAddress(host, port), config.connectTimeoutMs)
        plain.soTimeout = config.soTimeoutMs
        if (scheme == "https") {
            val tls = originContext.socketFactory.createSocket(plain, host, port, true) as SSLSocket
            tls.startHandshake()
            return tls
        }
        return plain
    }

    private fun clip(body: ByteArray?): ByteArray? {
        if (body == null) return null
        val limit = config.captureMaxBodyBytes
        if (body.size <= limit) return body
        return body.copyOfRange(0, limit.toInt())
    }

    private fun readRequestBody(input: InputStream, headers: MutableHeaders): ByteArray? {
        if (headers.get("transfer-encoding")?.contains("chunked", true) == true) {
            return HttpIo.readChunked(input)
        }
        val len = headers.get("content-length")?.trim()?.toIntOrNull() ?: return null
        if (len <= 0) return null
        return HttpIo.readFully(input, len)
    }

    private fun readResponseBody(input: InputStream, headers: MutableHeaders): ByteArray {
        if (headers.get("transfer-encoding")?.contains("chunked", true) == true) {
            return HttpIo.readChunked(input)
        }
        val len = headers.get("content-length")?.trim()?.toIntOrNull()
        if (len != null && len >= 0) return HttpIo.readFully(input, len)
        // EOF-delimited body (origin used Connection: close)
        return HttpIo.readUntilEof(input)
    }

    private fun decodeBody(body: ByteArray?, encoding: String?): ByteArray? {
        if (body == null || body.isEmpty()) return null
        val enc = encoding?.lowercase(Locale.ROOT) ?: return null
        return try {
            when {
                enc.contains("gzip") -> GZIPInputStream(body.inputStream()).use { it.readBytes() }
                enc.contains("deflate") -> java.util.zip.InflaterInputStream(
                    body.inputStream(),
                    java.util.zip.Inflater(true),
                ).use { it.readBytes() }

                else -> null
            }
        } catch (_: java.util.zip.DataFormatException) {
            null
        } catch (_: IOException) {
            null
        }
    }

    private fun reasonFor(status: Int?): String = when (status) {
        200 -> "OK"
        301 -> "Moved Permanently"
        302 -> "Found"
        304 -> "Not Modified"
        400 -> "Bad Request"
        403 -> "Forbidden"
        404 -> "Not Found"
        418 -> "I'm a teapot"
        500 -> "Internal Server Error"
        502 -> "Bad Gateway"
        503 -> "Service Unavailable"
        else -> "Status"
    }
}

/** Byte-level HTTP/1.1 framing helpers shared by the proxy paths. */
internal object HttpIo {
    const val MAX_LINE = 64 * 1024

    class Head(
        val method: String,
        val target: String,
        val version: String,
        val status: Int?,
        val headers: List<Pair<String, String>>,
        val raw: ByteArray,
    )

    /** Reads a CRLF (or LF) terminated line; null on EOF. */
    fun readLine(input: InputStream): String? {
        val out = ByteArrayOutputStream()
        var sawCr = false
        while (true) {
            val b = try {
                input.read()
            } catch (_: IOException) {
                return null
            }
            if (b < 0) {
                return if (out.size() == 0) null else out.toString(Charsets.ISO_8859_1)
            }
            if (b == '\n'.code) break
            if (sawCr) {
                // stray CR not followed by LF: keep both bytes
                out.write('\r'.code)
                sawCr = false
            }
            if (b == '\r'.code) {
                sawCr = true
            } else {
                out.write(b)
            }
            if (out.size() > MAX_LINE) throw IOException("line too long")
        }
        return out.toString(Charsets.ISO_8859_1)
    }

    /** Reads a full head, consuming the first line itself. */
    fun readHead(input: InputStream): Head? {
        val first = readLine(input) ?: return null
        return readHead(input, first)
    }

    /** Reads the head starting from an already-consumed first line. */
    fun readHead(input: InputStream, firstLine: String): Head? {
        val raw = ByteArrayOutputStream()
        raw.write(firstLine.toByteArray(Charsets.ISO_8859_1))
        raw.write("\r\n".toByteArray(Charsets.ISO_8859_1))
        val headerList = ArrayList<Pair<String, String>>(16)
        while (true) {
            val line = readLine(input) ?: return null
            raw.write(line.toByteArray(Charsets.ISO_8859_1))
            raw.write("\r\n".toByteArray(Charsets.ISO_8859_1))
            if (line.isEmpty()) break
            if (line.startsWith(" ") || line.startsWith("\t")) continue // obs-fold: skip continuation
            val colon = line.indexOf(':')
            if (colon <= 0) continue
            headerList.add(line.substring(0, colon).trim() to line.substring(colon + 1).trim())
        }
        val parts = firstLine.split(' ')
        val isResponse = parts.first().startsWith("HTTP/", ignoreCase = true)
        return if (isResponse && parts.size >= 2) {
            Head(
                method = "",
                target = "",
                version = parts[0],
                status = parts[1].toIntOrNull(),
                headers = headerList,
                raw = raw.toByteArray(),
            )
        } else if (parts.size >= 3) {
            Head(
                method = parts[0],
                target = parts[1],
                version = parts[2],
                status = null,
                headers = headerList,
                raw = raw.toByteArray(),
            )
        } else {
            null
        }
    }

    fun readFully(input: InputStream, length: Int): ByteArray {
        val out = ByteArray(length)
        var off = 0
        while (off < length) {
            val n = input.read(out, off, length - off)
            if (n < 0) throw EOFException("body truncated at $off/$length")
            off += n
        }
        return out
    }

    fun readChunked(input: InputStream): ByteArray {
        val out = ByteArrayOutputStream()
        while (true) {
            val sizeLine = readLine(input) ?: throw EOFException("chunked: missing size")
            val size = sizeLine.substringBefore(';').trim().toIntOrNull(16)
                ?: throw IOException("chunked: bad size line")
            if (size == 0) {
                // trailers until empty line
                while (true) {
                    val t = readLine(input) ?: break
                    if (t.isEmpty()) break
                }
                break
            }
            out.write(readFully(input, size))
            readLine(input) // trailing CRLF after each chunk
        }
        return out.toByteArray()
    }

    fun readUntilEof(input: InputStream): ByteArray {
        return input.readBytes()
    }

    private val hopByHop = setOf(
        "connection", "proxy-connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade",
    )

    fun writeRequest(
        output: OutputStream,
        method: String,
        path: String,
        host: String,
        headers: MutableHeaders,
        body: ByteArray?,
    ) {
        val sb = StringBuilder()
        sb.append(method).append(' ').append(path).append(" HTTP/1.1\r\n")
        sb.append("Host: ").append(host).append("\r\n")
        sb.append("Connection: close\r\n")
        for ((name, value) in headers.toList()) {
            if (name.equals("host", true) || name.lowercase() in hopByHop) continue
            sb.append(name).append(": ").append(value).append("\r\n")
        }
        if (body != null && headers.get("content-length") == null &&
            headers.get("transfer-encoding") == null
        ) {
            sb.append("Content-Length: ").append(body.size).append("\r\n")
        }
        sb.append("\r\n")
        output.write(sb.toString().toByteArray(Charsets.ISO_8859_1))
        if (body != null) output.write(body)
        output.flush()
    }

    fun writeResponse(
        output: OutputStream,
        status: Int?,
        reason: String,
        headers: MutableHeaders,
        body: ByteArray?,
    ) {
        val sb = StringBuilder()
        sb.append("HTTP/1.1 ").append(status ?: 502).append(' ').append(reason).append("\r\n")
        var hasDate = false
        for ((name, value) in headers.toList()) {
            if (name.lowercase() in hopByHop || name.equals("content-length", true)) continue
            if (name.equals("date", true)) hasDate = true
            sb.append(name).append(": ").append(value).append("\r\n")
        }
        if (!hasDate) sb.append("Date: ").append(java.time.format.DateTimeFormatter.RFC_1123_DATE_TIME
            .format(java.time.ZonedDateTime.now(java.time.ZoneOffset.UTC))).append("\r\n")
        sb.append("Content-Length: ").append(body?.size ?: 0).append("\r\n")
        sb.append("\r\n")
        output.write(sb.toString().toByteArray(Charsets.ISO_8859_1))
        if (body != null && body.isNotEmpty()) output.write(body)
        output.flush()
    }
}
