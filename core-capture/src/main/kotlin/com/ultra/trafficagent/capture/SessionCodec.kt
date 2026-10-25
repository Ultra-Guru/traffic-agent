package com.ultra.trafficagent.capture

/**
 * One-line JSON serialization for [CapturedRequest] (基建三「存」).
 *
 * Self-contained: no JSON library dependency, matching the encoding subset of
 * core-exports' JsonWriter so captures survive across module boundaries.
 */
object SessionCodec {

    fun escape(s: String?): String {
        if (s == null) return "null"
        val sb = StringBuilder(s.length + 2)
        sb.append('"')
        for (c in s) {
            when (c) {
                '"' -> sb.append("\\\"")
                '\\' -> sb.append("\\\\")
                '\n' -> sb.append("\\n")
                '\r' -> sb.append("\\r")
                '\t' -> sb.append("\\t")
                '\b' -> sb.append("\\b")
                '' -> sb.append("\\f")
                else -> if (c.code < 0x20) sb.append("\\u%04x".format(c.code)) else sb.append(c)
            }
        }
        sb.append('"')
        return sb.toString()
    }

    /** Encodes one session as a single JSONL line (no trailing newline). */
    fun encode(session: CapturedRequest): String {
        fun headersJson(map: Map<String, String>): String =
            map.entries.joinToString(",", prefix = "{", postfix = "}") {
                "${escape(it.key)}:${escape(it.value)}"
            }
        return buildString {
            append('{')
            append("\"id\":").append(session.id)
            append(",\"ts\":").append(session.timestampMs)
            append(",\"host\":").append(escape(session.host))
            append(",\"path\":").append(escape(session.path))
            append(",\"method\":").append(escape(session.method))
            append(",\"status\":").append(session.status ?: "null")
            append(",\"reqHeaders\":").append(headersJson(session.requestHeaders))
            append(",\"respHeaders\":").append(headersJson(session.responseHeaders))
            append(",\"reqBody\":").append(escape(session.requestBody))
            append(",\"respBody\":").append(escape(session.responseBody))
            append(",\"up\":").append(session.bytesUp)
            append(",\"down\":").append(session.bytesDown)
            append(",\"protocol\":\"").append(session.protocol.name).append('"')
            append(",\"uid\":").append(session.appUid ?: "null")
            append('}')
        }
    }

    /** Decodes one JSONL line; null when the line is blank or malformed. */
    fun decode(line: String): CapturedRequest? {
        val text = line.trim()
        if (!text.startsWith("{") || !text.endsWith("}")) return null
        return try {
            val p = Parser(text)
            val root = p.parseObject()
            // The parser yields Double for all numbers and String for text,
            // so coerce through Number/String instead of String-only helpers.
            fun num(key: String): Long = (root[key] as? Number)?.toLong() ?: 0L
            fun numInt(key: String): Int? = (root[key] as? Number)?.toInt()
            fun str(key: String): String = root[key] as? String ?: ""
            CapturedRequest(
                id = (root["id"] as? Number)?.toLong() ?: return null,
                timestampMs = num("ts"),
                host = str("host"),
                path = str("path"),
                method = str("method"),
                status = numInt("status"),
                requestHeaders = decodeMap(root["reqHeaders"]),
                responseHeaders = decodeMap(root["respHeaders"]),
                requestBody = str("reqBody"),
                responseBody = str("respBody"),
                bytesUp = num("up"),
                bytesDown = num("down"),
                protocol = (root["protocol"] as? String)
                    ?.let { name -> Protocol.entries.firstOrNull { it.name == name } }
                    ?: Protocol.UNKNOWN,
                appUid = numInt("uid"),
            )
        } catch (_: Exception) {
            null
        }
    }

    private fun decodeMap(v: Any?): Map<String, String> {
        val map = v as? Map<*, *> ?: return emptyMap()
        val out = LinkedHashMap<String, String>()
        for ((k, value) in map) {
            if (k is String && value is String) out[k] = value
        }
        return out
    }

    /** Minimal recursive-descent JSON parser for the subset we emit. */
    private class Parser(private val s: String) {
        private var i = 0

        fun parseObject(): Map<String, Any?> {
            expect('{')
            val out = LinkedHashMap<String, Any?>()
            skipWs()
            if (peek() == '}') {
                i++
                return out
            }
            while (true) {
                skipWs()
                val key = parseString()
                skipWs()
                expect(':')
                out[key] = parseValue()
                skipWs()
                when (peek()) {
                    ',' -> i++
                    '}' -> {
                        i++
                        return out
                    }
                    else -> throw IllegalArgumentException("bad object at $i")
                }
            }
        }

        private fun parseValue(): Any? = when (val c = peek()) {
            '{' -> parseObject()
            '"' -> parseString()
            't' -> {
                expectWord("true")
                true
            }
            'f' -> {
                expectWord("false")
                false
            }
            'n' -> {
                expectWord("null")
                null
            }
            else -> if (c == '-' || c in '0'..'9') parseNumber() else throw IllegalArgumentException("bad value at $i")
        }

        private fun peek(): Char = if (i < s.length) s[i] else throw IllegalArgumentException("eof")

        private fun expect(c: Char) {
            if (peek() != c) throw IllegalArgumentException("expected $c at $i")
            i++
        }

        private fun expectWord(w: String) {
            if (!s.startsWith(w, i)) throw IllegalArgumentException("bad word at $i")
            i += w.length
        }

        private fun skipWs() {
            while (i < s.length && s[i].isWhitespace()) i++
        }

        private fun parseString(): String {
            expect('"')
            val sb = StringBuilder()
            while (true) {
                if (i >= s.length) throw IllegalArgumentException("unterminated string")
                val c = s[i++]
                if (c == '"') return sb.toString()
                if (c == '\\') {
                    if (i >= s.length) throw IllegalArgumentException("bad escape")
                    when (val e = s[i++]) {
                        '"' -> sb.append('"')
                        '\\' -> sb.append('\\')
                        '/' -> sb.append('/')
                        'n' -> sb.append('\n')
                        'r' -> sb.append('\r')
                        't' -> sb.append('\t')
                        'b' -> sb.append('\b')
                        'f' -> sb.append('')
                        'u' -> {
                            if (i + 4 > s.length) throw IllegalArgumentException("bad unicode escape")
                            sb.append(s.substring(i, i + 4).toInt(16).toChar())
                            i += 4
                        }
                        else -> throw IllegalArgumentException("bad escape $e")
                    }
                } else {
                    sb.append(c)
                }
            }
        }

        private fun parseNumber(): Double {
            val start = i
            if (peek() == '-') i++
            while (i < s.length && (s[i].isDigit() || s[i] in ".eE+-")) i++
            return s.substring(start, i).toDouble()
        }
    }
}
