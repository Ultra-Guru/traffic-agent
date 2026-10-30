package com.ultra.trafficagent.transform

/**
 * Minimal JSON reader/writer for the rulepack format — a strict subset
 * (objects, arrays, strings, numbers, booleans, null) with a hand-rolled
 * recursive-descent parser, mirroring the SessionCodec approach: zero
 * dependencies, fully deterministic, PIT-friendly.
 */
object MiniJson {

    // ------------------------------------------------------------------ AST

    sealed class Json {
        object Null : Json()
        data class Bool(val value: Boolean) : Json()
        data class Num(val value: Double) : Json()
        data class Str(val value: String) : Json()
        data class Arr(val items: List<Json>) : Json()
        data class Obj(val fields: LinkedHashMap<String, Json>) : Json() {
            operator fun get(key: String): Json? = fields[key]
        }
    }

    class JsonFormatException(message: String) : Exception(message)

    // --------------------------------------------------------------- writer

    fun write(value: Json): String {
        val sb = StringBuilder()
        writeTo(sb, value)
        return sb.toString()
    }

    private fun writeTo(sb: StringBuilder, value: Json) {
        when (value) {
            is Json.Null -> sb.append("null")
            is Json.Bool -> sb.append(if (value.value) "true" else "false")
            is Json.Num -> {
                val d = value.value
                if (d == Math.floor(d) && !d.isInfinite() && Math.abs(d) < 1e15) {
                    sb.append(d.toLong().toString())
                } else {
                    sb.append(d.toString())
                }
            }
            is Json.Str -> writeString(sb, value.value)
            is Json.Arr -> {
                sb.append('[')
                value.items.forEachIndexed { i, item ->
                    if (i > 0) sb.append(',')
                    writeTo(sb, item)
                }
                sb.append(']')
            }
            is Json.Obj -> {
                sb.append('{')
                var first = true
                for ((k, v) in value.fields) {
                    if (!first) sb.append(',')
                    first = false
                    writeString(sb, k)
                    sb.append(':')
                    writeTo(sb, v)
                }
                sb.append('}')
            }
        }
    }

    private fun writeString(sb: StringBuilder, s: String) {
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
                else -> if (c < ' ') {
                    sb.append("\\u")
                    sb.append(String.format("%04x", c.code))
                } else {
                    sb.append(c)
                }
            }
        }
        sb.append('"')
    }

    // --------------------------------------------------------------- reader

    fun parse(text: String): Json {
        val p = Parser(text)
        val value = p.parseValue()
        p.skipWs()
        if (!p.atEnd()) throw JsonFormatException("trailing content at ${p.pos}")
        return value
    }

    private class Parser(private val text: String) {
        var pos = 0

        fun atEnd(): Boolean = pos >= text.length

        fun skipWs() {
            while (pos < text.length && text[pos].let { it == ' ' || it == '\t' || it == '\n' || it == '\r' }) {
                pos++
            }
        }

        fun parseValue(): Json {
            skipWs()
            if (atEnd()) throw JsonFormatException("unexpected end of input")
            return when (text[pos]) {
                '{' -> parseObject()
                '[' -> parseArray()
                '"' -> Json.Str(parseString())
                't' -> parseKeyword("true", Json.Bool(true))
                'f' -> parseKeyword("false", Json.Bool(false))
                'n' -> parseKeyword("null", Json.Null)
                else -> parseNumber()
            }
        }

        private fun parseKeyword(word: String, out: Json): Json {
            if (pos + word.length > text.length || text.substring(pos, pos + word.length) != word) {
                throw JsonFormatException("bad keyword at $pos")
            }
            pos += word.length
            return out
        }

        private fun parseObject(): Json.Obj {
            expect('{')
            val fields = LinkedHashMap<String, Json>()
            skipWs()
            if (peek() == '}') {
                pos++
                return Json.Obj(fields)
            }
            while (true) {
                skipWs()
                val key = parseString()
                skipWs()
                expect(':')
                fields[key] = parseValue()
                skipWs()
                when (peek()) {
                    ',' -> pos++
                    '}' -> {
                        pos++
                        return Json.Obj(fields)
                    }
                    else -> throw JsonFormatException("expected ',' or '}' at $pos")
                }
            }
        }

        private fun parseArray(): Json.Arr {
            expect('[')
            val items = mutableListOf<Json>()
            skipWs()
            if (peek() == ']') {
                pos++
                return Json.Arr(items)
            }
            while (true) {
                items.add(parseValue())
                skipWs()
                when (peek()) {
                    ',' -> pos++
                    ']' -> {
                        pos++
                        return Json.Arr(items)
                    }
                    else -> throw JsonFormatException("expected ',' or ']' at $pos")
                }
            }
        }

        private fun parseString(): String {
            expect('"')
            val sb = StringBuilder()
            while (true) {
                if (atEnd()) throw JsonFormatException("unterminated string at $pos")
                val c = text[pos]
                when {
                    c == '"' -> {
                        pos++
                        return sb.toString()
                    }
                    c == '\\' -> {
                        pos++
                        if (atEnd()) throw JsonFormatException("bad escape at $pos")
                        when (val e = text[pos]) {
                            '"' -> sb.append('"')
                            '\\' -> sb.append('\\')
                            '/' -> sb.append('/')
                            'n' -> sb.append('\n')
                            'r' -> sb.append('\r')
                            't' -> sb.append('\t')
                            'b' -> sb.append('\b')
                            'f' -> sb.append('\u000C')
                            'u' -> {
                                if (pos + 4 >= text.length) {
                                    throw JsonFormatException("bad unicode escape at $pos")
                                }
                                val hex = text.substring(pos + 1, pos + 5)
                                sb.append(hex.toInt(16).toChar())
                                pos += 4
                            }
                            else -> throw JsonFormatException("bad escape '\\$e' at $pos")
                        }
                        pos++
                    }
                    else -> {
                        sb.append(c)
                        pos++
                    }
                }
            }
        }

        private fun parseNumber(): Json.Num {
            val start = pos
            if (peek() == '-') pos++
            while (!atEnd() && text[pos].isDigit()) pos++
            var isDouble = false
            if (!atEnd() && text[pos] == '.') {
                isDouble = true
                pos++
                while (!atEnd() && text[pos].isDigit()) pos++
            }
            if (!atEnd() && (text[pos] == 'e' || text[pos] == 'E')) {
                isDouble = true
                pos++
                if (!atEnd() && (text[pos] == '+' || text[pos] == '-')) pos++
                while (!atEnd() && text[pos].isDigit()) pos++
            }
            if (pos == start) throw JsonFormatException("not a number at $pos")
            val token = text.substring(start, pos)
            return Json.Num(
                if (isDouble) token.toDouble() else token.toLong().toDouble(),
            )
        }

        private fun expect(c: Char) {
            if (atEnd() || text[pos] != c) throw JsonFormatException("expected '$c' at $pos")
            pos++
        }

        private fun peek(): Char {
            if (atEnd()) throw JsonFormatException("unexpected end at $pos")
            return text[pos]
        }
    }

    // -------------------------------------------------------- convenience

    fun obj(vararg pairs: Pair<String, Json>): Json.Obj = Json.Obj(LinkedHashMap(pairs.toMap()))

    fun obj(pairs: List<Pair<String, Json>>): Json.Obj = Json.Obj(LinkedHashMap(pairs.toMap()))

    fun str(s: String): Json.Str = Json.Str(s)

    fun num(n: Long): Json.Num = Json.Num(n.toDouble())

    fun arr(items: List<Json>): Json.Arr = Json.Arr(items)

    fun Json?.asStringOrNull(): String? = (this as? Json.Str)?.value

    fun Json?.asLongOrNull(): Long? {
        val n = this as? Json.Num ?: return null
        return n.value.toLong()
    }

    fun Json?.asIntOrNull(): Int? = asLongOrNull()?.toInt()

    fun Json?.asBooleanOrNull(): Boolean? = (this as? Json.Bool)?.value

    fun Json?.asArrayOrNull(): List<Json>? = (this as? Json.Arr)?.items
}
