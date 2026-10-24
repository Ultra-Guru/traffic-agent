package com.ultra.trafficagent.capture

import java.net.ConnectException
import java.net.HttpURLConnection
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.time.Duration
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLException
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

/**
 * Tunables for [ReplayEngine]; mirrors the request-replay screen of
 * HttpCanary/Reqable.
 */
data class ReplayConfig(
    val followRedirects: Boolean = false,
    val connectTimeoutMs: Long = 8000,
    val ioTimeoutMs: Long = 15000,
    val trustAll: Boolean = false,
    val extraHeaders: Map<String, String> = emptyMap(),
)

/**
 * Per-replay overrides applied on top of a captured exchange: replace the
 * method, retarget the URL, merge headers, or swap the body.
 */
data class ReplayOverrides(
    val method: String? = null,
    val url: String? = null,
    val headers: Map<String, String> = emptyMap(),
    val body: ByteArray? = null,
)

/** Outcome of one replay attempt. [status] is null on transport errors. */
data class ReplayResult(
    val status: Int?,
    val headers: List<Pair<String, String>>,
    val body: ByteArray?,
    val durationMs: Long,
    val requestUrl: String,
    val error: String?,
)

/**
 * Replays a captured exchange against its (possibly overridden) origin using
 * the JDK HttpClient — HttpCanary's most-used debugging feature.
 *
 * On Android the same semantics can be layered on OkHttp; this JVM
 * implementation keeps the core testable without extra dependencies.
 */
class ReplayEngine(private val config: ReplayConfig = ReplayConfig()) {

    private val client: HttpClient = buildClient()

    /**
     * Replays [capture] with [overrides] applied. Transport failures
     * (connect refused, timeouts, TLS errors) are reported through
     * [ReplayResult.error] with a null status instead of throwing.
     */
    fun replay(capture: CapturedRequest, overrides: ReplayOverrides = ReplayOverrides()): ReplayResult {
        val method = (overrides.method ?: capture.method).uppercase()
        val url = overrides.url ?: replayUrl(capture)
        val headers = mergedHeaders(capture, overrides)
        val body: ByteArray? = if (method == "GET" || method == "HEAD") {
            null
        } else {
            overrides.body ?: capture.requestBody.toByteArray()
        }

        val start = System.nanoTime()
        try {
            val builder = HttpRequest.newBuilder(URI(url))
                .timeout(Duration.ofMillis(config.ioTimeoutMs))
                .method(
                    method,
                    if (body != null) HttpRequest.BodyPublishers.ofByteArray(body) else HttpRequest.BodyPublishers.noBody(),
                )
            for ((name, value) in headers) builder.header(name, value)
            val response = client.send(builder.build(), HttpResponse.BodyHandlers.ofByteArray())
            val durationMs = elapsedMs(start)
            return ReplayResult(
                status = response.statusCode(),
                headers = response.headers().map().flatMap { (name, values) ->
                    values.map { name to it }
                },
                body = response.body(),
                durationMs = durationMs,
                requestUrl = url,
                error = null,
            )
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
            return failure(url, start, e)
        } catch (e: Exception) {
            // ConnectException (incl. HttpConnectTimeoutException) and
            // SSLException are the expected transport failures; anything
            // else (bad URI, restricted header, ...) is reported the same way.
            return failure(url, start, e)
        }
    }

    /**
     * URL the capture replays to when no override is given: secure or
     * not-yet-answered exchanges go to https, plain HTTP captures with a
     * recorded response go to http. [CapturedRequest.path] may carry a query.
     */
    internal fun replayUrl(capture: CapturedRequest): String {
        val scheme = if (capture.isSecure || capture.responseHeaders.isEmpty()) "https" else "http"
        return "$scheme://${capture.host}${capture.path}"
    }

    private fun failure(url: String, start: Long, e: Exception): ReplayResult =
        ReplayResult(
            status = null,
            headers = emptyList(),
            body = null,
            durationMs = elapsedMs(start),
            requestUrl = url,
            error = e.message ?: e.javaClass.simpleName,
        )

    private fun elapsedMs(start: Long): Long = (System.nanoTime() - start) / 1_000_000L

    private fun mergedHeaders(capture: CapturedRequest, overrides: ReplayOverrides): Map<String, String> {
        val merged = LinkedHashMap<String, String>()
        for ((name, value) in capture.requestHeaders) {
            if (!isHopByHop(name)) merged[name] = value
        }
        for ((name, value) in config.extraHeaders) {
            if (!isHopByHop(name)) merged[name] = value
        }
        for ((name, value) in overrides.headers) {
            if (!isHopByHop(name)) merged[name] = value
        }
        return merged
    }

    private fun buildClient(): HttpClient {
        val builder = HttpClient.newBuilder()
            .connectTimeout(Duration.ofMillis(config.connectTimeoutMs))
            .followRedirects(if (config.followRedirects) HttpClient.Redirect.ALWAYS else HttpClient.Redirect.NEVER)
        if (config.trustAll) {
            builder.sslContext(trustAllContext())
            // java.net.http has no hostnameVerifier setter: endpoint
            // identification is disabled through the SSL parameters instead.
            val params = javax.net.ssl.SSLParameters()
            params.endpointIdentificationAlgorithm = ""
            builder.sslParameters(params)
        }
        return builder.build()
    }

    private fun isHopByHop(name: String): Boolean = name.lowercase() in HOP_BY_HOP_HEADERS

    private companion object {
        /**
         * Hop-by-hop headers never replayed verbatim; "host" and
         * "content-length" are dropped because HttpClient derives them from
         * the target URI and the (possibly overridden) body.
         */
        val HOP_BY_HOP_HEADERS = setOf(
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailer",
            "transfer-encoding",
            "upgrade",
            "host",
            "content-length",
        )

        fun trustAllContext(): SSLContext {
            val trustAll = object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) = Unit

                override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) = Unit

                override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
            }
            val context = SSLContext.getInstance("TLS")
            context.init(null, arrayOf<TrustManager>(trustAll), SecureRandom())
            return context
        }
    }
}
