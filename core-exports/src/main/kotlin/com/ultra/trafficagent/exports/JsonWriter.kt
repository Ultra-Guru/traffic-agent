package com.ultra.trafficagent.exports

/**
 * Minimal dependency-free JSON writer covering the subset we emit
 * (objects, arrays, strings, numbers, booleans).
 */
object JsonWriter {

    /** JSON string literal with full escaping. */
    fun str(s: String?): String {
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
                '\u000C' -> sb.append("\\f")
                else -> {
                    if (c.code < 0x20) {
                        sb.append(String.format("\\u%04x", c.code))
                    } else {
                        sb.append(c)
                    }
                }
            }
        }
        sb.append('"')
        return sb.toString()
    }

    fun obj(vararg pairs: Pair<String, String>): String =
        pairs.joinToString(",", prefix = "{", postfix = "}") { (k, v) -> "${str(k)}:$v" }

    fun objOf(vararg pairs: Pair<String, String>): String = obj(*pairs)

    fun arr(items: List<String>): String =
        items.joinToString(",", prefix = "[", postfix = "]")

    fun num(n: Long): String = n.toString()

    fun bool(b: Boolean): String = if (b) "true" else "false"
}
