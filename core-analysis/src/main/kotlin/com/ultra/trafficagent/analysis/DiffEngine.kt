package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest

/** A single changed field between two captured exchanges. */
data class FieldChange(val key: String, val before: String, val after: String)

/** Diff of one matched request pair. */
data class RequestDiff(
    val key: String,
    val host: String,
    val path: String,
    val changes: List<FieldChange>,
) {
    val hasChanges: Boolean get() = changes.isNotEmpty()
}

/** Result of comparing two capture sets (SPEC v2.1: differential regression). */
data class CaptureDiffReport(
    val baselineLabel: String,
    val candidateLabel: String,
    val added: List<CapturedRequest>,
    val removed: List<CapturedRequest>,
    val changed: List<RequestDiff>,
) {
    val isIdentical: Boolean
        get() = added.isEmpty() && removed.isEmpty() && changed.isEmpty()

    /** Total number of differences found. */
    val changeScore: Int get() = added.size + removed.size + changed.size
}

/**
 * Differential regression engine: matches requests between two capture sets
 * by (method, host, path) in order, then reports status, header, body-size
 * and byte-count changes. Used to lock down app behaviour before/after a
 * release, a rewrite rule, or an agent action.
 */
class DiffEngine {

    fun diff(
        baseline: List<CapturedRequest>,
        candidate: List<CapturedRequest>,
        baselineLabel: String = "baseline",
        candidateLabel: String = "candidate",
    ): CaptureDiffReport {
        val baselineGroups = baseline.groupBy { it.matchKey() }
        val candidateGroups = candidate.groupBy { it.matchKey() }

        val added = mutableListOf<CapturedRequest>()
        val removed = mutableListOf<CapturedRequest>()
        val changed = mutableListOf<RequestDiff>()

        for ((key, baseList) in baselineGroups) {
            val candList = candidateGroups[key]
            if (candList == null) {
                removed += baseList
                continue
            }
            val pairs = baseList.size.coerceAtMost(candList.size)
            for (i in 0 until pairs) {
                val diff = diffPair(key, baseList[i], candList[i])
                if (diff.hasChanges) changed += diff
            }
            if (baseList.size > pairs) removed += baseList.subList(pairs, baseList.size)
            if (candList.size > pairs) added += candList.subList(pairs, candList.size)
        }
        for ((key, candList) in candidateGroups) {
            if (key !in baselineGroups) added += candList
        }

        return CaptureDiffReport(baselineLabel, candidateLabel, added, removed, changed)
    }

    private fun diffPair(key: String, a: CapturedRequest, b: CapturedRequest): RequestDiff {
        val changes = mutableListOf<FieldChange>()
        if (a.status != b.status) {
            changes += FieldChange("status", a.status.toString(), b.status.toString())
        }
        if (a.method != b.method) {
            changes += FieldChange("method", a.method, b.method)
        }
        changes += headerChanges("request", a.requestHeaders, b.requestHeaders)
        changes += headerChanges("response", a.responseHeaders, b.responseHeaders)
        if (a.requestBody.length != b.requestBody.length) {
            changes += FieldChange(
                "requestBody.length",
                a.requestBody.length.toString(),
                b.requestBody.length.toString(),
            )
        }
        if (a.responseBody.length != b.responseBody.length) {
            changes += FieldChange(
                "responseBody.length",
                a.responseBody.length.toString(),
                b.responseBody.length.toString(),
            )
        }
        if (a.protocol != b.protocol) {
            changes += FieldChange("protocol", a.protocol.name, b.protocol.name)
        }
        return RequestDiff(key, a.host, a.path, changes)
    }

    private fun headerChanges(
        phase: String,
        before: Map<String, String>,
        after: Map<String, String>,
    ): List<FieldChange> {
        val out = mutableListOf<FieldChange>()
        val beforeLower = before.mapKeys { it.key.lowercase() }
        val afterLower = after.mapKeys { it.key.lowercase() }
        for ((name, value) in beforeLower) {
            val other = afterLower[name]
            if (other == null) {
                out += FieldChange("$phase.header[$name]", value, "<absent>")
            } else if (other != value) {
                out += FieldChange("$phase.header[$name]", value, other)
            }
        }
        for ((name, value) in afterLower) {
            if (name !in beforeLower) {
                out += FieldChange("$phase.header[$name]", "<absent>", value)
            }
        }
        return out
    }

    private fun CapturedRequest.matchKey(): String = "$method $host$path"
}
