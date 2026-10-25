package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.net.Socket
import java.nio.charset.StandardCharsets

/**
 * One HTTP/1.x request/response relayed through the MITM position
 * (基建二「解」), producing a fully captured exchange.
 *
 * The relay terminates one client connection, forwards each request it
 * receives to the real origin (a fresh protected upstream socket, re-framed
 * with Connection: close so responses are delimited even without
 * Content-Length), then decodes the response body (Content-Length / chunked /
 * EOF) and re-frames it for the client.
 */
class HttpRelay(
    val clientIn: InputStream,
    val clientOut: OutputStream,
    val originalDstIp: String,
    val originalDstPort: Int,
    val openUpstream: (host: String, port: Int) -> Socket,
    val wrapUpstreamTls: (plain: Socket, host: String, port: Int) -> Socket,
    val now: () -> Long = System::currentTimeMillis,
) {

    companion object {
        private const val MAX_HEAD_BYTES = 32 * 1024
        private const val MAX_BODY_BYTES = 8 * 1024 * 1024
        private fun statusProtocol(isTls: Boolean) = if (isTls) Protocol.TLS else Protocol.HTTP1
    }

    /** Result of one request/response exchange. */
    data class RelayResult(val captured: CapturedRequest, val clientWantsMore: Boolean)

    /**
     * Performs a single exchange. Returns null when the client closed cleanly
     * before sending a request.
     */
    fun exchange(id: Long): RelayResult? {
        val request = readRequest() ?: return null

        val hostHeader = request.headers.entries.firstOrNull {
            it.key.equals("Host", ignoreCase = true)
        }?.value?.substringBefore(':')?.trim()
        val host = hostHeader?.takeIf { it.isNotEmpty() } ?: originalDstIp
        val upstreamPort = if (originalDstPort == 443) 443 else originalDstPort
        val isTls = originalDstPort == 443

        var upstream = openUpstream(host, upstreamPort)
        try {
            if (isTls) {
                upstream = wrapUpstreamTls(upstream, host, upstreamPort)
            }
            val upOut = BufferedOutputStream(upstream.getOutputStream())
            upOut.write(request.encoded().toByteArray(StandardCharsets.ISO_8859_1))
            upOut.flush()

            val upIn = BufferedInputStream(upstream.getInputStream())
            val response = readResponse(upIn)

            val clientKeepAlive = request.keepAlive
            val encoded = response.encodedForClient(keepAlive = clientKeepAlive)
            clientOut.write(encoded)
            clientOut.flush()

            val captured = CapturedRequest(
                id = id,
                timestampMs = now(),
                host = host,
                path = request.target,
                method = request.method,
                status = response.statusCode,
                requestHeaders = request.headers,
                responseHeaders = response.headers,
                requestBody = request.body.toString(StandardCharsets.UTF_8),
                responseBody = response.body.toString(StandardCharsets.UTF_8),
                bytesUp = request.encodedLength().toLong(),
                bytesDown = response.totalLength.toLong(),
                protocol = statusProtocol(isTls),
                appUid = null,
            )
            return RelayResult(captured, clientKeepAlive)
        } finally {
            try {
                upstream.close()
            } catch (_: IOException) {
            }
        }
    }

    // ---------------- request ----------------

    class Http1Request(
        val method: String,
        val target: String,
        val version: String,
        val headers: Map<String, String>,
        val body: ByteArrayOutputStream,
        val keepAlive: Boolean,
    ) {
        fun encoded(): String = buildString {
            append(method).append(' ').append(target).append(' ').append(version).append("\r\n")
            for ((k, v) in headers) append(k).append(": ").append(v).append("\r\n")
            append("Connection: close\r\n\r\n")
            append(body.toString(StandardCharsets.ISO_8859_1))
        }

        fun encodedLength(): Int = encoded().toByteArray(StandardCharsets.ISO_8859_1).size
    }

    private fun readRequest(): Http1Request? {
        val head = readHead(clientIn) ?: return null
        val lines = head.split("\r\n")
        val first = lines.firstOrNull() ?: return null
        val parts = first.split(' ')
        if (parts.size < 3) throw IOException("malformed request line: $first")
        val headers = LinkedHashMap<String, String>()
        for (i in 1 until lines.size) {
            val line = lines[i]
            val idx = line.indexOf(':')
            if (idx <= 0) continue
            headers[line.substring(0, idx).trim()] = line.substring(idx + 1).trim()
        }
        val version = parts[2]
        val connHeader = headers.entries.firstOrNull { it.key.equals("Connection", ignoreCase = true) }?.value
        val keepAlive = when {
            connHeader != null -> connHeader.contains("keep-alive", ignoreCase = true)
            else -> version >= "HTTP/1.1"
        }
        val body = readBody(clientIn, headers, allowEof = false) ?: ByteArrayOutputStream()
        return Http1Request(parts[0], parts[1], version, headers, body, keepAlive)
    }

    // ---------------- response ----------------

    class Http1Response(
        val version: String,
        val statusCode: Int,
        val reason: String,
        val headers: Map<String, String>,
        val body: ByteArrayOutputStream,
        val chunked: Boolean,
        val endedByEof: Boolean,
        val headLength: Int,
    ) {
        val totalLength: Int get() = headLength + body.size()

        /** Re-frames the response for the client: decoded bodies get a Content-Length. */
        fun encodedForClient(keepAlive: Boolean): ByteArray {
            val out = ByteArrayOutputStream(totalLength + 128)
            val w = out.writer(StandardCharsets.ISO_8859_1)
            w.write("$version $statusCode")
            if (reason.isNotEmpty()) w.write(" $reason")
            w.write("\r\n")
            for ((k, v) in headers) {
                if (k.equals("Connection", ignoreCase = true)) continue
                if (k.equals("Transfer-Encoding", ignoreCase = true)) continue
                if (k.equals("Content-Length", ignoreCase = true)) continue
                w.write("$k: $v\r\n")
            }
            w.write("Content-Length: ${body.size()}\r\n")
            w.write(if (keepAlive) "Connection: keep-alive" else "Connection: close")
            w.write("\r\n\r\n")
            w.flush()
            out.write(body.toByteArray())
            return out.toByteArray()
        }
    }

    private fun readResponse(input: InputStream): Http1Response {
        val head = readHead(input) ?: throw IOException("empty response")
        val lines = head.split("\r\n")
        val first = lines.firstOrNull() ?: throw IOException("empty response")
        val parts = first.split(' ', limit = 3)
        if (parts.size < 2 || !parts[0].startsWith("HTTP/")) throw IOException("malformed status line: $first")
        val status = parts[1].toIntOrNull() ?: throw IOException("bad status code: $first")
        val reason = if (parts.size == 3) parts[2] else ""
        val headers = LinkedHashMap<String, String>()
        for (i in 1 until lines.size) {
            val line = lines[i]
            val idx = line.indexOf(':')
            if (idx <= 0) continue
            headers[line.substring(0, idx).trim()] = line.substring(idx + 1).trim()
        }
        val body = readBody(input, headers, allowEof = true)
        val chunked = headers.entries.any {
            it.key.equals("Transfer-Encoding", ignoreCase = true) &&
                it.value.contains("chunked", ignoreCase = true)
        }
        val endedByEof = !chunked && headers.entries.none { it.key.equals("Content-Length", ignoreCase = true) }
        return Http1Response(
            version = parts[0], statusCode = status, reason = reason, headers = headers,
            body = body ?: ByteArrayOutputStream(), chunked = chunked, endedByEof = endedByEof,
            headLength = head.toByteArray(StandardCharsets.ISO_8859_1).size + 4,
        )
    }

    // ---------------- framing helpers ----------------

    /** Reads up to (and including) the blank line; null on clean EOF. */
    private fun readHead(input: InputStream): String? {
        val sb = StringBuilder()
        var got = false
        while (true) {
            val line = readLine(input) ?: break
            if (line.isEmpty()) {
                got = true
                break
            }
            sb.append(line).append("\r\n")
            if (sb.length > MAX_HEAD_BYTES) throw IOException("head too large")
        }
        if (!got) {
            return if (sb.isEmpty()) null else throw IOException("truncated head")
        }
        return sb.toString()
    }

    private fun readLine(input: InputStream): String? {
        val sb = StringBuilder()
        while (true) {
            val c = input.read()
            if (c < 0) return if (sb.isEmpty()) null else sb.toString()
            if (c == '\n'.code) {
                if (sb.isNotEmpty() && sb.last() == '\r') sb.setLength(sb.length - 1)
                return sb.toString()
            }
            sb.append(c.toChar())
            if (sb.length > MAX_HEAD_BYTES) throw IOException("line too long")
        }
    }

    /** Decodes a body per Content-Length / chunked / EOF semantics. */
    private fun readBody(input: InputStream, headers: Map<String, String>, allowEof: Boolean): ByteArrayOutputStream? {
        val chunkedHeader = headers.entries.firstOrNull {
            it.key.equals("Transfer-Encoding", ignoreCase = true)
        }?.value?.contains("chunked", ignoreCase = true) == true
        if (chunkedHeader) return readChunked(input)

        val clHeader = headers.entries.firstOrNull { it.key.equals("Content-Length", ignoreCase = true) }?.value
        if (clHeader != null) {
            val len = clHeader.trim().toIntOrNull() ?: throw IOException("bad content-length: $clHeader")
            if (len < 0 || len > MAX_BODY_BYTES) throw IOException("body too large: $len")
            val out = ByteArrayOutputStream(len)
            var remaining = len
            val buf = ByteArray(8192)
            while (remaining > 0) {
                val n = input.read(buf, 0, minOf(buf.size, remaining))
                if (n < 0) throw IOException("truncated body")
                out.write(buf, 0, n)
                remaining -= n
            }
            return out
        }
        if (allowEof) {
            val out = ByteArrayOutputStream()
            val buf = ByteArray(8192)
            while (true) {
                val n = input.read(buf)
                if (n < 0) break
                out.write(buf, 0, n)
                if (out.size() > MAX_BODY_BYTES) throw IOException("body too large")
            }
            return out
        }
        return null
    }

    private fun readChunked(input: InputStream): ByteArrayOutputStream {
        val out = ByteArrayOutputStream()
        while (true) {
            val sizeLine = readLine(input) ?: throw IOException("truncated chunk header")
            val sizeText = sizeLine.substringBefore(';').trim()
            val size = sizeText.toIntOrNull(16) ?: throw IOException("bad chunk size: $sizeText")
            if (size == 0) {
                // trailers until the final blank line (usually immediate)
                while (true) {
                    val t = readLine(input) ?: throw IOException("truncated trailers")
                    if (t.isEmpty()) break
                }
                return out
            }
            if (size > MAX_BODY_BYTES) throw IOException("chunk too large")
            var remaining = size
            val buf = ByteArray(8192)
            while (remaining > 0) {
                val n = input.read(buf, 0, minOf(buf.size, remaining))
                if (n < 0) throw IOException("truncated chunk")
                out.write(buf, 0, n)
                remaining -= n
            }
            val crlf = readLine(input) ?: throw IOException("missing chunk terminator")
            if (crlf.isNotEmpty()) throw IOException("bad chunk terminator")
        }
    }
}

private fun ByteArrayOutputStream.writer(cs: java.nio.charset.Charset): java.io.Writer =
    object : java.io.Writer() {
        override fun write(cbuf: CharArray, off: Int, len: Int) {
            this@writer.write(String(cbuf, off, len).toByteArray(cs))
        }

        override fun flush() {}

        override fun close() {}
    }
