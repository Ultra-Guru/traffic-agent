package com.ultra.trafficagent.mitm

import com.ultra.trafficagent.transform.HttpRewriter
import com.ultra.trafficagent.transform.MutableExchange
import com.ultra.trafficagent.transform.MutableHttpRequest
import com.ultra.trafficagent.transform.MutableHttpResponse
import com.ultra.trafficagent.transform.RuleRegistry
import java.nio.charset.StandardCharsets

/**
 * Bridges the proxy pipeline into the shared [RuleRegistry] rewrite engine:
 * HttpCanary-style request/response rewriting applied to decrypted MITM
 * traffic (SPEC v2.1 L1.5).
 *
 * Request-phase actions run before the origin is contacted; response-phase
 * actions run after the origin answered, before the client sees the bytes.
 * Request-phase short-circuits (Block / MockResponse / Abort) are honoured:
 * the origin is never contacted and the synthesized answer (or simulated
 * timeout) goes straight back to the client.
 * [com.ultra.trafficagent.transform.RuleAction.DelayMs] is honoured up to
 * [maxDelayMs] per phase to protect the tunnel from runaway rules.
 */
class MitmRewriteInterceptor(
    private val registry: RuleRegistry,
    private val maxDelayMs: Long = 5_000,
) : ExchangeInterceptor {

    override fun onRequest(ctx: MutableProxyExchange): ProxyDecision {
        val request = ctx.toMutableHttpRequest()
        val exchange = MutableExchange(request)
        val result = HttpRewriter(registry).applyTo(exchange)
        ctx.appliedRuleIds += result.appliedRuleIds
        if (result.appliedRuleIds.isNotEmpty()) {
            ctx.method = request.method
            ctx.host = request.host
            ctx.path = request.path
            val mappedPort = request.port
            if (mappedPort != null) ctx.port = mappedPort
            ctx.requestHeaders.replaceWith(MutableHeaders(request.headers().map { (k, v) -> k to v }))
            ctx.requestBody = request.body.toByteArray(StandardCharsets.UTF_8)
            if (request.header("content-length") != null) {
                ctx.requestHeaders.set("Content-Length", request.body.length.toString())
            }
        }
        val delay = result.delayedByMs.coerceAtMost(maxDelayMs)
        if (delay > 0) Thread.sleep(delay)

        if (result.dropped) {
            // Abort rule: emulate an origin that never answers.
            val timeout = result.abortTimeoutMs.coerceAtMost(maxDelayMs)
            if (timeout > 0) Thread.sleep(timeout)
            return ProxyDecision.ShortCircuit(
                504,
                "upstream timed out (rule abort after ${result.abortTimeoutMs}ms)"
                    .toByteArray(StandardCharsets.UTF_8),
                "text/plain; charset=utf-8",
            )
        }
        if (result.shortCircuited) {
            // Block / MockResponse: the rewriter wrote the answer into the
            // exchange's response slot — serve it locally.
            val resp = exchange.response ?: MutableHttpResponse(403)
            val mime = resp.header("content-type") ?: "text/plain; charset=utf-8"
            return ProxyDecision.ShortCircuit(
                resp.status,
                resp.body.toByteArray(StandardCharsets.UTF_8),
                mime,
            )
        }
        return ProxyDecision.Forward
    }

    override fun onResponse(ctx: MutableProxyExchange) {
        val request = ctx.toMutableHttpRequest()
        val response = MutableHttpResponse(
            status = ctx.status ?: 200,
            headers = ctx.responseHeaders.toList().toMap(),
            body = (ctx.responseBody ?: ByteArray(0)).toString(StandardCharsets.UTF_8),
        )
        val exchange = MutableExchange(request, response)
        val result = HttpRewriter(registry).applyTo(exchange)
        val newIds = result.appliedRuleIds.filter { it !in ctx.appliedRuleIds }
        ctx.appliedRuleIds += newIds
        if (result.appliedRuleIds.isNotEmpty()) {
            ctx.status = response.status
            ctx.responseHeaders.replaceWith(
                MutableHeaders(response.headers().map { (k, v) -> k to v }),
            )
            ctx.responseBody = response.body.toByteArray(StandardCharsets.UTF_8)
        }
        val delay = result.delayedByMs.coerceAtMost(maxDelayMs)
        if (delay > 0) Thread.sleep(delay)
    }

    private fun MutableProxyExchange.toMutableHttpRequest(): MutableHttpRequest {
        val bodyText = requestBody?.toString(StandardCharsets.UTF_8) ?: ""
        return MutableHttpRequest(
            method = method,
            host = host,
            path = path,
            headers = requestHeaders.toList().toMap(),
            body = bodyText,
        )
    }
}
