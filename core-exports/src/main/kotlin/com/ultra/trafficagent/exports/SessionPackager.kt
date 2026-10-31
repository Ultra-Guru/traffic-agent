package com.ultra.trafficagent.exports

import java.io.ByteArrayOutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/**
 * Bundles every export format into a single shareable ZIP: manifest first,
 * then the artifacts (JSON / HAR / cURL / Markdown / CSV / timeline).
 * Pure JVM (java.util.zip) so it works on desktop tooling and Android.
 */
object SessionPackager {

    /** One artifact inside the package. */
    data class Artifact(
        /** File name inside the zip, e.g. "session.md". */
        val name: String,
        /** MIME type recorded in the manifest. */
        val mime: String,
        /** Artifact bytes (UTF-8 of the export, or binary pcap). */
        val data: ByteArray,
    ) {
        constructor(name: String, mime: String, text: String) : this(
            name, mime, text.toByteArray(Charsets.UTF_8),
        )
    }

    /** Metadata recorded in manifest.json. */
    data class Manifest(
        val generator: String = "traffic-agent",
        val formatVersion: Int = 1,
        val createdAtMs: Long,
        val exchangeCount: Int,
        val artifacts: List<ArtifactEntry>,
    ) {
        data class ArtifactEntry(val name: String, val mime: String, val bytes: Int)
    }

    /** Builds the zip bytes from the artifacts. */
    fun packageSession(artifacts: List<Artifact>, createdAtMs: Long, exchangeCount: Int): ByteArray {
        require(artifacts.isNotEmpty()) { "nothing to package" }
        val used = mutableSetOf<String>()
        val deduped = artifacts.map { a ->
            var name = a.name
            var n = 1
            while (name in used) {
                val dot = a.name.lastIndexOf('.')
                name = if (dot > 0) {
                    a.name.substring(0, dot) + "-" + n + a.name.substring(dot)
                } else {
                    a.name + "-" + n
                }
                n++
            }
            used.add(name)
            a.copy(name = name)
        }

        val manifest = Manifest(
            createdAtMs = createdAtMs,
            exchangeCount = exchangeCount,
            artifacts = deduped.map { Manifest.ArtifactEntry(it.name, it.mime, it.data.size) },
        )

        val out = ByteArrayOutputStream()
        ZipOutputStream(out).use { zip ->
            putEntry(zip, "manifest.json", manifestJson(manifest).toByteArray(Charsets.UTF_8))
            for (a in deduped) {
                putEntry(zip, a.name, a.data)
            }
        }
        return out.toByteArray()
    }

    /** Convenience: package the standard text formats in one call. */
    fun packageStandard(
        requests: List<com.ultra.trafficagent.capture.CapturedRequest>,
        title: String,
        nowMs: Long,
    ): ByteArray {
        val artifacts = mutableListOf(
            Artifact("session.md", "text/markdown", ReportExporter.export(requests, title)),
            Artifact("session.csv", "text/csv", CsvExporter.export(requests)),
            Artifact("session.har", "application/json", HarExporter.export(requests, title = title)),
            Artifact("session.jsonl", "application/x-ndjson", JsonlExporter.export(requests)),
            Artifact("session.curl", "text/x-shellscript",
                requests.joinToString("\n\n") { CurlExporter.toCurl(it) }),
            Artifact("session.timeline", "text/plain", FlowTimelineExporter.export(requests)),
        )
        return packageSession(artifacts, nowMs, requests.size)
    }

    private fun putEntry(zip: ZipOutputStream, name: String, data: ByteArray) {
        zip.putNextEntry(ZipEntry(name))
        zip.write(data)
        zip.closeEntry()
    }

    private fun manifestJson(m: Manifest): String {
        val sb = StringBuilder()
        sb.append("{\n")
        sb.append("  \"generator\": \"").append(m.generator).append("\",\n")
        sb.append("  \"formatVersion\": ").append(m.formatVersion).append(",\n")
        sb.append("  \"createdAtMs\": ").append(m.createdAtMs).append(",\n")
        sb.append("  \"exchangeCount\": ").append(m.exchangeCount).append(",\n")
        sb.append("  \"artifacts\": [\n")
        for ((i, a) in m.artifacts.withIndex()) {
            sb.append("    {\"name\": \"").append(a.name)
                .append("\", \"mime\": \"").append(a.mime)
                .append("\", \"bytes\": ").append(a.bytes).append('}')
            if (i < m.artifacts.size - 1) sb.append(',')
            sb.append('\n')
        }
        sb.append("  ]\n}\n")
        return sb.toString()
    }
}

/** One JSON object per line (NDJSON), optimized for streaming ingestion. */
object JsonlExporter {

    fun export(requests: List<com.ultra.trafficagent.capture.CapturedRequest>): String {
        val sb = StringBuilder()
        for (r in requests) {
            sb.append('{')
            jsonField(sb, "id", r.id.toString(), raw = true)
            jsonField(sb, "ts", r.timestampMs.toString(), comma = true, raw = true)
            jsonField(sb, "host", r.host, comma = true)
            jsonField(sb, "path", r.path, comma = true)
            jsonField(sb, "method", r.method, comma = true)
            jsonField(sb, "status", r.status?.toString() ?: "null", comma = true, raw = true)
            jsonField(sb, "proto", r.protocol.name, comma = true)
            jsonField(sb, "up", r.bytesUp.toString(), comma = true, raw = true)
            jsonField(sb, "down", r.bytesDown.toString(), comma = true, raw = true)
            if (r.durationMs != null) {
                jsonField(sb, "durationMs", r.durationMs.toString(), comma = true, raw = true)
            }
            if (!r.error.isNullOrEmpty()) {
                jsonField(sb, "error", r.error!!, comma = true)
            }
            sb.append("}\n")
        }
        return sb.toString()
    }

    private fun jsonField(sb: StringBuilder, name: String, value: String,
                          comma: Boolean = false, raw: Boolean = false) {
        if (comma) sb.append(", ")
        sb.append('"').append(name).append("\": ")
        if (raw) {
            sb.append(value)
        } else {
            sb.append('"').append(value
                .replace("\\", "\\\\")
                .replace("\"", "\\\""))
                .append('"')
        }
    }
}

/**
 * Chronological exchange timeline with direction arrows, terminal-friendly:
 *
 * ```
 * 12:00:01.123  -> api.example.com        GET /v1/data            412 B
 * 12:00:01.201  <- api.example.com        200 OK                5.2 KiB   78 ms
 * 12:00:02.000  -> cdn.example.com        GET /app.js             120 B
 * ```
 */
object FlowTimelineExporter {

    fun export(requests: List<com.ultra.trafficagent.capture.CapturedRequest>): String {
        val sb = StringBuilder()
        val byTs = requests.sortedBy { it.timestampMs }
        for (r in byTs) {
            sb.append(ts(r.timestampMs))
                .append("  -> ").append(pad(r.host, 24))
                .append(pad("${r.method} ${r.path.take(32)}", 40))
                .append(formatSize(r.bytesUp)).append('\n')
            val statusCode = r.status
            if (statusCode != null) {
                sb.append(ts(r.timestampMs + (r.durationMs ?: 0)))
                    .append("  <- ").append(pad(r.host, 24))
                    .append(pad("$statusCode ${statusText(statusCode)}", 40))
                    .append(formatSize(r.bytesDown))
                if (r.durationMs != null) {
                    sb.append("   ").append(r.durationMs).append(" ms")
                }
                sb.append('\n')
            }
        }
        return sb.toString()
    }

    private fun ts(ms: Long): String {
        val totalSec = ms / 1000
        val millis = (ms % 1000).toString().padStart(3, '0')
        val h = (totalSec / 3600) % 24
        val m = (totalSec / 60) % 60
        val s = totalSec % 60
        return String.format("%02d:%02d:%02d.%s", h, m, s, millis)
    }

    private fun statusText(code: Int): String = when (code) {
        200 -> "OK"
        201 -> "Created"
        204 -> "No Content"
        301 -> "Moved Permanently"
        302 -> "Found"
        304 -> "Not Modified"
        400 -> "Bad Request"
        401 -> "Unauthorized"
        403 -> "Forbidden"
        404 -> "Not Found"
        429 -> "Too Many Requests"
        500 -> "Internal Server Error"
        502 -> "Bad Gateway"
        503 -> "Service Unavailable"
        504 -> "Gateway Timeout"
        else -> ""
    }

    private fun pad(s: String, width: Int): String =
        if (s.length >= width) s.take(width - 1) + " " else s.padEnd(width)

    private fun formatSize(bytes: Long): String = when {
        bytes >= 1 shl 20 -> String.format("%.1f MiB", bytes / 1048576.0)
        bytes >= 1 shl 10 -> String.format("%.1f KiB", bytes / 1024.0)
        else -> "$bytes B"
    }
}
