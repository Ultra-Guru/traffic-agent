package com.ultra.trafficagent.agent

import java.io.BufferedReader
import java.io.BufferedWriter
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

/**
 * Handle to the Python agent process (python -m traffic_agent.bridge).
 * Seams are kept narrow so tests can substitute a fake.
 */
interface AgentProcess : AutoCloseable {
    /** Sends one command line. */
    fun writeLine(line: String)

    /** Reads one response line; returns null at end of stream. */
    fun readLine(): String?

    val isAlive: Boolean
}

class RealAgentProcess(command: List<String>) : AgentProcess {
    private val process = ProcessBuilder(command).apply { redirectErrorStream(false) }.start()
    private val stdin = BufferedWriter(OutputStreamWriter(process.outputStream, StandardCharsets.UTF_8))
    private val stdout = BufferedReader(InputStreamReader(process.inputStream, StandardCharsets.UTF_8))

    override fun writeLine(line: String) {
        stdin.write(line)
        stdin.newLine()
        stdin.flush()
    }

    override fun readLine(): String? = stdout.readLine()

    override val isAlive: Boolean get() = process.isAlive

    override fun close() {
        try {
            stdin.close()
        } finally {
            process.destroyForcibly()
        }
    }
}

/** Response of one bridge call, decoded from the query-string line. */
data class BridgeResponse(val fields: Map<String, String>) {
    val ok: Boolean get() = fields["ok"] == "1"
    val errorCode: String? get() = fields["error_code"]
    val risk: RiskLevel? get() = fields["risk"]?.let { runCatching { RiskLevel.valueOf(it.uppercase()) }.getOrNull() }
    val error: String? get() = fields["error"]?.let { decodeUrl(it) }
    val payload: String? get() = fields["payload"]?.let { decodeUrl(it) }

    companion object {
        private fun decodeUrl(s: String): String =
            java.net.URLDecoder.decode(s, StandardCharsets.UTF_8)
    }
}

/**
 * Client of the Python agent bridge. Every call is locally gated with the
 * Kotlin risk mirror before it reaches the wire; `approved=true` marks calls
 * the user has explicitly approved in the UI.
 */
class AgentBridge(
    private val processFactory: () -> AgentProcess,
    private val gate: RiskGate = RiskGate(),
) {
    private var process: AgentProcess? = null

    companion object {
        fun encode(pairs: Map<String, String>): String =
            pairs.entries.joinToString("&") { (k, v) ->
                "${url(k)}=${url(v)}"
            }

        private fun url(s: String): String = URLEncoder.encode(s, StandardCharsets.UTF_8)

        fun decode(line: String): Map<String, String> {
            if (line.isEmpty()) return emptyMap()
            return line.split("&").mapNotNull { part ->
                val idx = part.indexOf('=')
                if (idx <= 0) return@mapNotNull null
                part.substring(0, idx) to part.substring(idx + 1)
            }.toMap()
        }

        fun decodeUrl(s: String): String =
            java.net.URLDecoder.decode(s, StandardCharsets.UTF_8)
    }

    fun ensureStarted() {
        if (process == null) process = processFactory()
    }

    fun shutdown() {
        process?.close()
        process = null
    }

    /** One gated round-trip. The gate result is returned for UI badges. */
    fun call(
        tool: String,
        params: Map<String, String> = emptyMap(),
        approved: Boolean = false,
    ): BridgeResponse {
        val decision = gate.evaluate(tool, approved)
        if (!decision.allowed) {
            val code = if (decision.risk == null) {
                "unknown_tool"
            } else if (decision.requiresApproval) {
                "approval_required"
            } else {
                "gate_denied"
            }
            val fields = mutableMapOf(
                "ok" to "0",
                "error_code" to code,
                "error" to (decision.reason ?: "denied"),
            )
            decision.risk?.let { fields["risk"] = it.name.lowercase() }
            return BridgeResponse(fields)
        }
        ensureStarted()
        val proc = process ?: return BridgeResponse(
            mapOf("ok" to "0", "error_code" to "process_error", "error" to "no agent process")
        )
        val line = buildString {
            append("method=").append(url(tool))
            for ((k, v) in params) {
                append('&').append(url(k)).append('=').append(url(v))
            }
            if (approved) append("&__approve=1")
        }
        proc.writeLine(line)
        val response = proc.readLine()
            ?: return BridgeResponse(mapOf("ok" to "0", "error_code" to "process_error", "error" to "agent exited"))
        return BridgeResponse(decode(response))
    }

    private fun url(s: String): String = URLEncoder.encode(s, StandardCharsets.UTF_8)
}
