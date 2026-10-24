package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest

/** Markdown report of a capture session. */
object MarkdownExporter {

    fun export(requests: List<CapturedRequest>, title: String = "Traffic Agent report"): String {
        val sb = StringBuilder()
        sb.append("# ").append(title).append("\n\n")
        sb.append("- Requests: ").append(requests.size).append('\n')
        val totalBytes = requests.sumOf { it.totalSize }
        sb.append("- Total traffic: ").append(totalBytes).append(" bytes\n\n")
        sb.append("| # | Method | Host | Path | Status | Up | Down |\n")
        sb.append("|---|--------|------|------|--------|----|------|\n")
        for ((index, req) in requests.withIndex()) {
            sb.append("| ").append(index + 1)
                .append(" | ").append(req.method)
                .append(" | ").append(req.host)
                .append(" | ").append(escapeCell(req.path))
                .append(" | ").append(req.status ?: "-")
                .append(" | ").append(req.bytesUp)
                .append(" | ").append(req.bytesDown)
                .append(" |\n")
        }
        return sb.toString()
    }

    private fun escapeCell(s: String): String = s.replace("|", "\\|").replace("\n", " ")
}

/** RFC 4180 CSV export. */
object CsvExporter {

    fun export(requests: List<CapturedRequest>): String {
        val sb = StringBuilder()
        sb.append("id,timestamp_ms,method,host,path,status,bytes_up,bytes_down,protocol\n")
        for (req in requests) {
            sb.append(field(req.id.toString())).append(',')
                .append(field(req.timestampMs.toString())).append(',')
                .append(field(req.method)).append(',')
                .append(field(req.host)).append(',')
                .append(field(req.path)).append(',')
                .append(field((req.status ?: -1).toString())).append(',')
                .append(field(req.bytesUp.toString())).append(',')
                .append(field(req.bytesDown.toString())).append(',')
                .append(field(req.protocol.name))
                .append('\n')
        }
        return sb.toString()
    }

    /** RFC 4180: quote when needed, double embedded quotes. */
    fun field(s: String): String {
        val needsQuoting = s.any { it == ',' || it == '"' || it == '\n' || it == '\r' }
        if (!needsQuoting) return s
        return "\"" + s.replace("\"", "\"\"") + "\""
    }
}
