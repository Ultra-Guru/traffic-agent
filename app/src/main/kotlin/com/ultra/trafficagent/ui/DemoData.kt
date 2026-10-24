package com.ultra.trafficagent.ui

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import com.ultra.trafficagent.transform.Phase
import com.ultra.trafficagent.transform.RuleAction
import com.ultra.trafficagent.transform.RuleMatch
import com.ultra.trafficagent.transform.RewriteRule

/** Demo capture set powering the first-run UI. */
object DemoData {

    val requests: List<CapturedRequest> = listOf(
        CapturedRequest(
            id = 1, timestampMs = 1700000000000, host = "api.github.com", path = "/repos/ultra-guru/traffic-agent",
            method = "GET", status = 200,
            requestHeaders = mapOf("Accept" to "application/vnd.github+json", "User-Agent" to "traffic-agent/0.1"),
            responseHeaders = mapOf("Content-Type" to "application/json", "X-RateLimit-Remaining" to "42"),
            requestBody = "", responseBody = """{"full_name":"ultra-guru/traffic-agent","stargazers_count":128}""",
            bytesUp = 320, bytesDown = 4820, protocol = Protocol.TLS, appUid = 10042,
            ja3 = "21d2e3024b63e0bac86dd07f7fb8c2bf", responseMime = "application/json",
            durationMs = 312, responseDecompressedBytes = 9218,
        ),
        CapturedRequest(
            id = 2, timestampMs = 1700000001200, host = "fonts.googleapis.com", path = "/css2?family=Roboto",
            method = "GET", status = 200,
            requestHeaders = mapOf("Accept" to "text/css"),
            responseHeaders = mapOf("Content-Type" to "text/css"),
            requestBody = "", responseBody = "/* css body */",
            bytesUp = 180, bytesDown = 1240, protocol = Protocol.HTTP2, appUid = 10042,
            responseMime = "text/css", durationMs = 87,
        ),
        CapturedRequest(
            id = 3, timestampMs = 1700000002400, host = "telemetry.example.net", path = "/v2/batch",
            method = "POST", status = 204,
            requestHeaders = mapOf("Content-Type" to "application/json"),
            responseHeaders = emptyMap(),
            requestBody = """{"events":[{"name":"app_open"}]}""", responseBody = "",
            bytesUp = 512, bytesDown = 0, protocol = Protocol.HTTP1, appUid = 10021,
            requestMime = "application/json", durationMs = 141,
        ),
        CapturedRequest(
            id = 4, timestampMs = 1700000003600, host = "cdn.example.io", path = "/assets/app-v3.js",
            method = "GET", status = 304,
            requestHeaders = mapOf("If-None-Match" to "\"v2\""),
            responseHeaders = mapOf("Cache-Control" to "max-age=604800"),
            requestBody = "", responseBody = "",
            bytesUp = 140, bytesDown = 0, protocol = Protocol.HTTP2, appUid = 10042,
        ),
        CapturedRequest(
            id = 5, timestampMs = 1700000004800, host = "ws.push.example.com", path = "/live",
            method = "GET", status = 101,
            requestHeaders = mapOf("Upgrade" to "websocket"),
            responseHeaders = mapOf("Connection" to "Upgrade"),
            requestBody = "", responseBody = "",
            bytesUp = 96, bytesDown = 2048, protocol = Protocol.WEBSOCKET, appUid = 10042,
            durationMs = 4_500,
        ),
        CapturedRequest(
            id = 6, timestampMs = 1700000006000, host = "ads.tracker.net", path = "/pixel.gif?uid=x",
            method = "GET", status = 403,
            requestHeaders = emptyMap(), responseHeaders = emptyMap(),
            requestBody = "", responseBody = "blocked by rule",
            bytesUp = 60, bytesDown = 96, protocol = Protocol.HTTP1, appUid = 10011,
            error = "blocked by rule: block-ads", durationMs = 3,
        ),
    )

    val initialRules: List<RewriteRule> = listOf(
        RewriteRule(
            id = "block-ads", name = "Block ad trackers", enabled = true, priority = 90,
            match = RuleMatch(hostRegex = "(ads|tracker)\\.net"),
            actions = listOf(RuleAction.SetStatus(403)),
        ),
        RewriteRule(
            id = "auth-bearer", name = "Inject auth header", enabled = true, priority = 50,
            match = RuleMatch(hostRegex = "api\\.github\\.com", methods = setOf("GET")),
            actions = listOf(RuleAction.SetHeader(Phase.REQUEST, "Authorization", "Bearer demo-token")),
        ),
        RewriteRule(
            id = "v1-to-v2", name = "Migrate /v1 to /v2", enabled = false, priority = 10,
            match = RuleMatch(pathRegex = "^/v1/"),
            actions = listOf(RuleAction.ReplacePath("^/v1/", "/v2/")),
        ),
    )
}
