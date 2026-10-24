package com.ultra.trafficagent.exports

import com.ultra.trafficagent.capture.CapturedRequest

/**
 * Postman Collection v2.1.0 export — one item per captured exchange,
 * replayable straight from the Postman importer (a step beyond
 * HttpCanary/Reqable, which stop at cURL/HAR).
 */
object PostmanExporter {

    fun toPostmanCollection(requests: List<CapturedRequest>, name: String = "Traffic Agent Export"): String {
        val items = requests.joinToString(",") { req -> itemOf(req) }
        return """{"info":{"name":${JsonWriter.str(name)},"_postman_id":"${idFor(requests)}","schema":"https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},"item":[$items]}"""
    }

    private fun idFor(requests: List<CapturedRequest>): String {
        val seed = requests.sumOf { it.id * 31L + it.totalSize }
        return "ta-%016x".format(seed)
    }

    private fun itemOf(req: CapturedRequest): String {
        val headers = req.requestHeaders.entries.joinToString(",") { (k, v) ->
            """{"key":${JsonWriter.str(k)},"value":${JsonWriter.str(v)}}"""
        }
        val raw = "https://${req.host}${req.path}"
        val (pathSegments, queryPairs) = splitUrl(req.path)
        val bodyBlock = if (req.method.uppercase() in METHODS_WITH_BODY && req.requestBody.isNotEmpty()) {
            ""","body":{"mode":"raw","raw":${JsonWriter.str(req.requestBody)},"options":{"raw":{"language":"json"}}}"""
        } else {
            ""
        }
        return """{"name":${JsonWriter.str("${req.method} ${req.host}${shortPath(req.path)}")},"request":{""" +
            """"method":${JsonWriter.str(req.method.uppercase())},"header":[$headers],""" +
            """"url":{"raw":${JsonWriter.str(raw)},"protocol":"https","host":${JsonWriter.arr(req.host.split(".").map { JsonWriter.str(it) })},"path":${JsonWriter.arr(pathSegments.map { JsonWriter.str(it) })},"query":${JsonWriter.arr(queryPairs)}}$bodyBlock}}"""
    }

    private fun shortPath(path: String): String =
        if (path.length > 40) path.take(37) + "..." else path

    private fun splitUrl(path: String): Pair<List<String>, List<String>> {
        val (pathPart, query) = path.split('?', limit = 2).let {
            if (it.size == 2) it[0] to it[1] else path to null
        }
        val segments = pathPart.split('/').filter { it.isNotEmpty() }
        val queryPairs = query?.split('&')?.filter { it.isNotEmpty() }?.map { pair ->
            val (k, v) = pair.split('=', limit = 2).let {
                if (it.size == 2) it[0] to it[1] else pair to ""
            }
            """{"key":${JsonWriter.str(k)},"value":${JsonWriter.str(v)}}"""
        } ?: emptyList()
        return segments to queryPairs
    }

    private val METHODS_WITH_BODY = setOf("POST", "PUT", "PATCH", "DELETE")
}
