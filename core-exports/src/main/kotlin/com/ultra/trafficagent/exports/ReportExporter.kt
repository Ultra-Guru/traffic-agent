package com.ultra.trafficagent.exports

import com.ultra.trafficagent.analysis.DnsInsight
import com.ultra.trafficagent.analysis.SessionScore
import com.ultra.trafficagent.analysis.TimeSeriesStats
import com.ultra.trafficagent.analysis.TrafficStats
import com.ultra.trafficagent.capture.CapturedRequest

/**
 * Rich Markdown session report: summary header, scorecard, top hosts,
 * protocol mix, error list, slow requests, DNS insight and an ASCII
 * sparkline of the traffic timeline.
 */
object ReportExporter {

    fun export(
        requests: List<CapturedRequest>,
        title: String = "Traffic Agent session report",
        dnsInsight: DnsInsight? = null,
    ): String {
        val sb = StringBuilder()
        val stats = TrafficStats()
        val series = TimeSeriesStats()
        requests.forEach { stats.record(it); series.record(it) }
        val score = SessionScore.compute(requests, dnsInsight?.snapshot()?.nxdomainRatio ?: 0.0)

        sb.append("# ").append(title).append("\n\n")
        appendSummary(sb, requests, score)
        appendSparkline(sb, series)
        appendTopHosts(sb, stats)
        appendProtocolMix(sb, requests)
        appendErrors(sb, requests)
        appendSlow(sb, requests)
        appendDns(sb, dnsInsight)
        appendDetails(sb, requests)
        return sb.toString()
    }

    private fun appendSummary(sb: StringBuilder, requests: List<CapturedRequest>, score: Int) {
        val totalUp = requests.sumOf { it.bytesUp }
        val totalDown = requests.sumOf { it.bytesDown }
        val errors = requests.count { (it.status ?: 0) >= 500 || it.error != null }
        val spanSec = if (requests.size >= 2) {
            (requests.maxOf { it.timestampMs } - requests.minOf { it.timestampMs }) / 1000.0
        } else 0.0

        sb.append("## Summary\n\n")
        sb.append("| Metric | Value |\n|---|---|\n")
        sb.append("| Exchanges | ").append(requests.size).append(" |\n")
        sb.append("| Session score | ").append(score)
            .append(" (").append(SessionScore.grade(score)).append(") |\n")
        sb.append("| Bytes up | ").append(formatBytes(totalUp)).append(" |\n")
        sb.append("| Bytes down | ").append(formatBytes(totalDown)).append(" |\n")
        sb.append("| Total | ").append(formatBytes(totalUp + totalDown)).append(" |\n")
        sb.append("| Errors | ").append(errors).append(" |\n")
        if (spanSec > 0) {
            sb.append("| Duration | ").append(String.format("%.1f s", spanSec)).append(" |\n")
            sb.append("| Throughput | ")
                .append(formatBytes(((totalUp + totalDown) / spanSec).toLong()))
                .append("/s |\n")
        }
        sb.append('\n')
    }

    /** One-line Unicode block sparkline of per-second totals. */
    private fun appendSparkline(sb: StringBuilder, series: TimeSeriesStats) {
        val buckets = series.series()
        if (buckets.size < 2) return
        sb.append("## Timeline\n\n")
        val maxTotal = buckets.maxOf { it.totalBytes }.coerceAtLeast(1)
        val blocks = "▁▂▃▄▅▆▇█"
        val line = StringBuilder()
        val step = if (buckets.size > 120) buckets.size / 120 else 1
        var i = 0
        while (i < buckets.size) {
            val window = buckets.subList(i, minOf(i + step, buckets.size))
            val avg = window.sumOf { it.totalBytes } / window.size
            val idx = ((avg.toDouble() / maxTotal) * (blocks.length - 1)).toInt()
                .coerceIn(0, blocks.length - 1)
            line.append(blocks[idx])
            i += step
        }
        sb.append("```\n").append(line).append("\n```\n\n")
    }

    private fun appendTopHosts(sb: StringBuilder, stats: TrafficStats) {
        val hosts = stats.topHosts(10)
        if (hosts.isEmpty()) return
        sb.append("## Top hosts\n\n")
        sb.append("| Host | Requests | Up | Down | Total |\n|---|---|---|---|---|\n")
        for (h in hosts) {
            sb.append("| ").append(escape(h.host))
                .append(" | ").append(h.requests)
                .append(" | ").append(formatBytes(h.bytesUp))
                .append(" | ").append(formatBytes(h.bytesDown))
                .append(" | ").append(formatBytes(h.totalBytes))
                .append(" |\n")
        }
        sb.append('\n')
    }

    private fun appendProtocolMix(sb: StringBuilder, requests: List<CapturedRequest>) {
        if (requests.isEmpty()) return
        sb.append("## Protocol mix\n\n")
        val byProto = requests.groupingBy { it.protocol }.eachCount()
        for ((proto, count) in byProto.entries.sortedByDescending { it.value }) {
            val pct = count * 100 / requests.size
            sb.append("- ").append(proto.name).append(": ").append(count)
                .append(" (").append(pct).append("%)\n")
        }
        sb.append('\n')
    }

    private fun appendErrors(sb: StringBuilder, requests: List<CapturedRequest>) {
        val errors = requests.filter { (it.status ?: 0) >= 500 || it.error != null }
        if (errors.isEmpty()) return
        sb.append("## Errors (").append(errors.size).append(")\n\n")
        sb.append("| # | Host | Path | Status | Detail |\n|---|---|---|---|---|\n")
        for ((i, e) in errors.withIndex()) {
            if (i >= 25) {
                sb.append("| ... | ").append(errors.size - 25).append(" more | | | |\n")
                break
            }
            sb.append("| ").append(i + 1)
                .append(" | ").append(escape(e.host))
                .append(" | ").append(escapeCell(e.path))
                .append(" | ").append(e.status ?: "-")
                .append(" | ").append(escapeCell(e.error ?: ""))
                .append(" |\n")
        }
        sb.append('\n')
    }

    private fun appendSlow(sb: StringBuilder, requests: List<CapturedRequest>) {
        val slow = requests.filter { (it.durationMs ?: 0) > 1_000 }
            .sortedByDescending { it.durationMs ?: 0 }
        if (slow.isEmpty()) return
        sb.append("## Slow requests (> 1s)\n\n")
        sb.append("| Host | Path | Duration |\n|---|---|---|\n")
        for ((i, r) in slow.withIndex()) {
            if (i >= 15) break
            sb.append("| ").append(escape(r.host))
                .append(" | ").append(escapeCell(r.path))
                .append(" | ").append(r.durationMs).append(" ms |\n")
        }
        sb.append('\n')
    }

    private fun appendDns(sb: StringBuilder, insight: DnsInsight?) {
        if (insight == null || insight.size == 0) return
        val snap = insight.snapshot(topN = 10)
        sb.append("## DNS\n\n")
        sb.append("- Queries: ").append(snap.totalQueries)
            .append(" (").append(String.format("%.1f", snap.queryRatePerMinute)).append("/min)\n")
        sb.append("- Unique domains: ").append(snap.uniqueDomains).append('\n')
        sb.append("- NXDOMAIN: ").append(snap.nxdomainCount)
            .append(" (").append(String.format("%.1f%%", snap.nxdomainRatio * 100)).append(")\n")
        if (snap.dohDetected) sb.append("- DoH transport detected\n")
        if (snap.suspiciousDomains.isNotEmpty()) {
            sb.append("- Suspicious: ").append(snap.suspiciousDomains.take(5).joinToString(", "))
                .append('\n')
        }
        sb.append('\n')
        if (snap.topDomains.isNotEmpty()) {
            sb.append("| Domain | Queries | NXDOMAIN ratio |\n|---|---|---|\n")
            for (d in snap.topDomains) {
                sb.append("| ").append(escape(d.domain))
                    .append(" | ").append(d.queries)
                    .append(" | ").append(String.format("%.0f%%", d.nxdomainRatio * 100))
                    .append(" |\n")
            }
            sb.append('\n')
        }
    }

    private fun appendDetails(sb: StringBuilder, requests: List<CapturedRequest>) {
        if (requests.isEmpty()) return
        sb.append("## Requests\n\n")
        sb.append("| # | Method | Host | Path | Status | Up | Down |\n")
        sb.append("|---|--------|------|------|--------|----|------|\n")
        for ((index, req) in requests.withIndex()) {
            if (index >= 500) {
                sb.append("| ... | ").append(requests.size - 500).append(" more | | | | | |\n")
                break
            }
            sb.append("| ").append(index + 1)
                .append(" | ").append(req.method)
                .append(" | ").append(escape(req.host))
                .append(" | ").append(escapeCell(req.path))
                .append(" | ").append(req.status ?: "-")
                .append(" | ").append(formatBytes(req.bytesUp))
                .append(" | ").append(formatBytes(req.bytesDown))
                .append(" |\n")
        }
    }

    private fun escape(s: String): String = s.replace("|", "\\|").replace("\n", " ")

    private fun escapeCell(s: String): String = escape(s).take(60)

    internal fun formatBytes(bytes: Long): String = when {
        bytes >= 1 shl 20 -> String.format("%.1f MiB", bytes / 1048576.0)
        bytes >= 1 shl 10 -> String.format("%.1f KiB", bytes / 1024.0)
        else -> "$bytes B"
    }
}
