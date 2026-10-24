package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest

/**
 * Time-bucketed index over captured requests: one bucket per second, with
 * range queries and peak detection for the timeline UI.
 */
class TimelineIndex {

    private val buckets = LinkedHashMap<Long, MutableList<CapturedRequest>>()

    fun add(request: CapturedRequest) {
        val second = request.timestampMs / 1000
        buckets.getOrPut(second) { mutableListOf() }.add(request)
    }

    fun addAll(requests: List<CapturedRequest>) = requests.forEach { add(it) }

    fun bucketCount(): Int = buckets.size

    fun requestsInSecond(secondEpoch: Long): List<CapturedRequest> =
        buckets[secondEpoch]?.toList() ?: emptyList()

    /** Inclusive range query [fromMs, toMs]. */
    fun requestsIn(fromMs: Long, toMs: Long): List<CapturedRequest> {
        if (toMs < fromMs) return emptyList()
        val fromSec = fromMs / 1000
        val toSec = toMs / 1000
        return buckets.filterKeys { it in fromSec..toSec }
            .values.flatten()
            .filter { it.timestampMs in fromMs..toMs }
    }

    fun countIn(fromMs: Long, toMs: Long): Int = requestsIn(fromMs, toMs).size

    /** The busiest second (epoch) so far, or null when empty. */
    fun peakSecond(): Long? =
        buckets.maxByOrNull { it.value.size }?.key

    fun peakCount(): Int = buckets.maxOfOrNull { it.value.size } ?: 0

    fun totalCount(): Int = buckets.values.sumOf { it.size }

    fun clear() = buckets.clear()
}
