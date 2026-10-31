package com.ultra.trafficagent.analysis

/**
 * Textual rule DSL shared with the desktop tooling and rule files:
 *
 * ```
 * rule block-ads priority 100
 *   when host matches "doubleclick\.net$" or category = ads
 *   then block
 *
 * rule slow-api priority 50 disabled
 *   when host contains "api.example.com" and duration > 2000
 *   then throttle rate=256
 *
 * rule mock-health
 *   when path = "/healthz" and method in GET,HEAD
 *   then mock status=200 body="ok"
 *
 * rule flag-video
 *   when mime starts_with "video/"
 *   then tag name="media"
 * ```
 *
 * Grammar (whitespace-separated tokens, `#` starts a line comment):
 *
 * ```
 * rules  := rule*
 * rule   := "rule" IDENT modifier* "when" expr "then" action param*
 * mod    := "priority" INT | "enabled" | "disabled"
 * expr   := andExpr ("or" andExpr)*
 * andExpr:= notExpr ("and" notExpr)*
 * notExpr:= "not" notExpr | primary
 * primary:= "(" expr ")" | FIELD OP value
 * OP     := = | != | > | < | >= | <= | contains | starts_with | ends_with
 *         | matches | in
 * value  := STRING | INT | IDENT ("," INT | "," IDENT | "," STRING)*
 * action := allow | block | throttle | mock | tag | redact
 * param  := rate=INT | status=INT | body=STRING | name=IDENT
 * ```
 */
object RuleDslParser {

    /** Parses a full rule document. Throws [IllegalArgumentException] on error. */
    fun parse(text: String): RuleSet {
        val rules = mutableListOf<Rule>()
        // Comments (full-line or trailing) are purely ignorable.
        val tokens = tokenize(text).filterNot { it is Tok.Comment }
        var i = 0
        while (i < tokens.size) {
            val t = tokens[i]
            when {
                t is Tok.Ident && t.value == "rule" -> {
                    val (rule, next) = parseRule(tokens, i + 1)
                    rules.add(rule)
                    i = next
                }
                else -> throw IllegalArgumentException("expected 'rule', got ${t.describe()}")
            }
        }
        return RuleSet(rules)
    }

    /** Parses one `rule ...` definition starting after the `rule` keyword. */
    private fun parseRule(tokens: List<Tok>, start: Int): Pair<Rule, Int> {
        var i = start
        val name = expectIdent(tokens, i, "rule name").also { i++ }

        var priority = 0
        var enabled = true
        while (true) {
            val t = tokens.getOrNull(i) as? Tok.ModifierKeyword ?: break
            when (t.word) {
                "priority" -> {
                    priority = expectInt(tokens, i + 1, "priority")
                    i += 2
                }
                "enabled" -> {
                    enabled = true
                    i++
                }
                "disabled" -> {
                    enabled = false
                    i++
                }
                // "when" / "then" terminate the modifier list.
                else -> break
            }
        }

        expectKeyword(tokens, i, "when").also { i++ }
        val (condition, afterExpr) = parseOr(tokens, i)
        i = afterExpr

        expectKeyword(tokens, i, "then").also { i++ }
        val actionTok = tokens.getOrNull(i) as? Tok.ActionKeyword
            ?: throw IllegalArgumentException("expected action at rule '$name', got ${tokens.getOrNull(i)?.describe() ?: "end of input"}")
        i++
        val action = actionTok.action

        var rate: Int? = null
        var status: Int? = null
        var body: String? = null
        var tagName: String? = null
        while (i < tokens.size && tokens[i] is Tok.Param) {
            val p = tokens[i] as Tok.Param
            when (p.key) {
                "rate" -> rate = p.intValue()
                "status" -> status = p.intValue()
                "body" -> body = p.stringValue()
                "name" -> tagName = p.stringValue()
            }
            i++
        }

        val rule = Rule(
            name = name,
            priority = priority,
            enabled = enabled,
            action = action,
            condition = condition,
            throttleRateKibPerS = rate,
            mockStatus = status,
            mockBody = body,
            tagName = tagName,
        )
        return rule to i
    }

    // ---------------- expression parsing ----------------

    private fun parseOr(tokens: List<Tok>, start: Int): Pair<RuleCondition, Int> {
        var (left, i) = parseAnd(tokens, start)
        while (true) {
            val t = tokens.getOrNull(i)
            if (t is Tok.OrKeyword) {
                val (right, next) = parseAnd(tokens, i + 1)
                left = RuleCondition.Or(left, right)
                i = next
            } else {
                return left to i
            }
        }
    }

    private fun parseAnd(tokens: List<Tok>, start: Int): Pair<RuleCondition, Int> {
        var (left, i) = parseNot(tokens, start)
        while (true) {
            val t = tokens.getOrNull(i)
            if (t is Tok.AndKeyword) {
                val (right, next) = parseNot(tokens, i + 1)
                left = RuleCondition.And(left, right)
                i = next
            } else {
                return left to i
            }
        }
    }

    private fun parseNot(tokens: List<Tok>, start: Int): Pair<RuleCondition, Int> {
        val t = tokens.getOrNull(start)
        if (t is Tok.NotKeyword) {
            val (inner, next) = parseNot(tokens, start + 1)
            return RuleCondition.Not(inner) to next
        }
        return parsePrimary(tokens, start)
    }

    private fun parsePrimary(tokens: List<Tok>, start: Int): Pair<RuleCondition, Int> {
        val t = tokens.getOrNull(start)
        if (t is Tok.OpenParen) {
            val (expr, after) = parseOr(tokens, start + 1)
            if (tokens.getOrNull(after) !is Tok.CloseParen) {
                throw IllegalArgumentException("expected ')' at token ${after}")
            }
            return expr to after + 1
        }
        if (t == null) throw IllegalArgumentException("unexpected end of condition")

        // `true` literal for empty-match rules.
        if (t is Tok.Ident && t.value == "true") {
            return RuleCondition.Always to start + 1
        }

        val field = (t as? Tok.Ident)?.let { RuleField.fromToken(it.value) }
            ?: throw IllegalArgumentException("expected field name, got ${t.describe()}")
        val opTok = tokens.getOrNull(start + 1) as? Tok.Op
            ?: throw IllegalArgumentException("expected operator after '${field.displayName}', got ${tokens.getOrNull(start + 1)?.describe() ?: "end"}")
        val op = RuleOp.fromToken(opTok.symbol)
            ?: throw IllegalArgumentException("unknown operator '${opTok.symbol}'")

        // Value: single literal or comma-separated list (only for `in`).
        val (value, after) = parseValue(tokens, start + 2, op)
        return RuleCondition.Field(field, op, value) to after
    }

    private fun parseValue(tokens: List<Tok>, start: Int, op: RuleOp): Pair<ConditionValue, Int> {
        val first = tokens.getOrNull(start)
            ?: throw IllegalArgumentException("expected value after operator '${op.symbol}'")
        val firstValue = first.toConditionValue()
            ?: throw IllegalArgumentException("expected value, got ${first.describe()}")
        var i = start + 1
        if (op != RuleOp.IN) return firstValue to i

        val items = mutableListOf(firstValue)
        while (tokens.getOrNull(i) is Tok.Comma) {
            val next = tokens.getOrNull(i + 1)
                ?: throw IllegalArgumentException("dangling ',' in list value")
            items.add(
                next.toConditionValue()
                    ?: throw IllegalArgumentException("expected value after ',', got ${next.describe()}"),
            )
            i += 2
        }
        return ConditionValue.ListOf(items) to i
    }

    // ---------------- token model ----------------

    private sealed class Tok {
        abstract fun describe(): String

        data class Ident(val value: String) : Tok() {
            override fun describe() = "'$value'"
        }

        data class IntLit(val value: Long) : Tok() {
            override fun describe() = value.toString()
        }

        data class StrLit(val value: String) : Tok() {
            override fun describe() = "\"$value\""
        }

        data class Op(val symbol: String) : Tok() {
            override fun describe() = "'$symbol'"
        }

        object OpenParen : Tok() {
            override fun describe() = "'('"
        }

        object CloseParen : Tok() {
            override fun describe() = "')'"
        }

        object Comma : Tok() {
            override fun describe() = "','"
        }

        object AndKeyword : Tok() {
            override fun describe() = "'and'"
        }

        object OrKeyword : Tok() {
            override fun describe() = "'or'"
        }

        object NotKeyword : Tok() {
            override fun describe() = "'not'"
        }

        data class ModifierKeyword(val word: String) : Tok() {
            override fun describe() = "'$word'"
        }

        data class ActionKeyword(val action: RuleAction) : Tok() {
            override fun describe() = "'${action.name.lowercase()}'"
        }

        data class Param(val key: String, val raw: String) : Tok() {
            override fun describe() = "'$key=...'"
            fun intValue(): Int =
                raw.toIntOrNull() ?: throw IllegalArgumentException("param '$key' needs an integer, got '$raw'")

            fun stringValue(): String = raw
        }

        data class Comment(val text: String) : Tok() {
            override fun describe() = "comment"
        }

        fun toConditionValue(): ConditionValue? = when (this) {
            is StrLit -> ConditionValue.Str(value)
            is IntLit -> ConditionValue.Num(value)
            is Ident -> ConditionValue.Str(value)
            else -> null
        }
    }

    private fun tokenize(text: String): List<Tok> {
        val tokens = mutableListOf<Tok>()
        var i = 0
        val n = text.length
        while (i < n) {
            val c = text[i]
            when {
                c == ' ' || c == '\t' || c == '\r' || c == '\n' -> i++
                c == '#' -> {
                    val end = text.indexOf('\n', i)
                    val stop = if (end == -1) n else end
                    tokens.add(Tok.Comment(text.substring(i + 1, stop)))
                    i = stop
                }
                c == '"' -> {
                    val sb = StringBuilder()
                    var j = i + 1
                    while (j < n && text[j] != '"') {
                        if (text[j] == '\\' && j + 1 < n) {
                            sb.append(unescape(text[j + 1]))
                            j += 2
                        } else {
                            sb.append(text[j])
                            j++
                        }
                    }
                    if (j >= n) throw IllegalArgumentException("unterminated string at offset $i")
                    tokens.add(Tok.StrLit(sb.toString()))
                    i = j + 1
                }
                c == '(' -> {
                    tokens.add(Tok.OpenParen)
                    i++
                }
                c == ')' -> {
                    tokens.add(Tok.CloseParen)
                    i++
                }
                c == ',' -> {
                    tokens.add(Tok.Comma)
                    i++
                }
                c == '>' || c == '<' || c == '!' || c == '=' -> {
                    // Multi-char operators: >= <= != =
                    if (i + 1 < n && text[i + 1] == '=') {
                        tokens.add(Tok.Op(text.substring(i, i + 2)))
                        i += 2
                    } else if (c == '=') {
                        tokens.add(Tok.Op("="))
                        i++
                    } else if (c == '!' ) {
                        throw IllegalArgumentException("lone '!' at offset $i (use !=)")
                    } else {
                        tokens.add(Tok.Op(c.toString()))
                        i++
                    }
                }
                c.isDigit() || (c == '-' && i + 1 < n && text[i + 1].isDigit()) -> {
                    var j = i
                    while (j < n && text[j].isDigit()) j++
                    tokens.add(Tok.IntLit(text.substring(i, j).toLong()))
                    i = j
                }
                else -> {
                    var j = i
                    while (j < n && !text[j].isWhitespace() && text[j] !in "()\",#<>!=") j++
                    if (j == i) {
                        throw IllegalArgumentException("unexpected character '$c' at offset $i")
                    }
                    val word = text.substring(i, j)
                    i = j
                    // word=param form
                    if (i < n && text[i] == '=') {
                        // peek the param value: string or bare token
                        if (i + 1 < n && text[i + 1] == '"') {
                            val sb = StringBuilder()
                            var k = i + 2
                            while (k < n && text[k] != '"') {
                                if (text[k] == '\\' && k + 1 < n) {
                                    sb.append(unescape(text[k + 1]))
                                    k += 2
                                } else {
                                    sb.append(text[k])
                                    k++
                                }
                            }
                            if (k >= n) throw IllegalArgumentException("unterminated param string for '$word'")
                            tokens.add(Tok.Param(word, sb.toString()))
                            i = k + 1
                        } else {
                            var k = i + 1
                            while (k < n && !text[k].isWhitespace()) k++
                            tokens.add(Tok.Param(word, text.substring(i + 1, k)))
                            i = k
                        }
                    } else {
                        tokens.add(keywordOrIdent(word))
                    }
                }
            }
        }
        return tokens
    }

    private fun keywordOrIdent(word: String): Tok = when (word.lowercase()) {
        "and" -> Tok.AndKeyword
        "or" -> Tok.OrKeyword
        "not" -> Tok.NotKeyword
        "priority", "enabled", "disabled", "when", "then" -> Tok.ModifierKeyword(word.lowercase())
        "allow" -> Tok.ActionKeyword(RuleAction.ALLOW)
        "block" -> Tok.ActionKeyword(RuleAction.BLOCK)
        "throttle" -> Tok.ActionKeyword(RuleAction.THROTTLE)
        "mock" -> Tok.ActionKeyword(RuleAction.MOCK)
        "tag" -> Tok.ActionKeyword(RuleAction.TAG)
        "redact" -> Tok.ActionKeyword(RuleAction.REDACT)
        "=", "!=", ">", "<", ">=", "<=", "contains", "starts_with", "ends_with", "matches", "in" ->
            Tok.Op(word.lowercase())
        else -> Tok.Ident(word)
    }

    private fun unescape(c: Char): Char = when (c) {
        'n' -> '\n'
        't' -> '\t'
        'r' -> '\r'
        '\\' -> '\\'
        '"' -> '"'
        else -> c
    }

    private fun expectIdent(tokens: List<Tok>, i: Int, what: String): String {
        val t = tokens.getOrNull(i)
        require(t is Tok.Ident) { "expected $what, got ${t?.describe() ?: "end of input"}" }
        return t.value
    }

    private fun expectInt(tokens: List<Tok>, i: Int, what: String): Int {
        val t = tokens.getOrNull(i)
        require(t is Tok.IntLit) { "expected integer $what, got ${t?.describe() ?: "end of input"}" }
        return t.value.toInt()
    }

    private fun expectKeyword(tokens: List<Tok>, i: Int, keyword: String) {
        val t = tokens.getOrNull(i)
        require(t is Tok.ModifierKeyword && t.word == keyword) {
            "expected '$keyword', got ${t?.describe() ?: "end of input"}"
        }
    }
}
