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

    private data class Modifiers(val priority: Int, val enabled: Boolean, val next: Int)

    /** Consumes the `priority N / enabled / disabled` prefix of a rule. */
    private fun parseModifiers(tokens: List<Tok>, start: Int, ruleName: String): Modifiers {
        var priority = 0
        var enabled = true
        var i = start
        val modifiable = setOf("priority", "enabled", "disabled")
        while ((tokens.getOrNull(i) as? Tok.ModifierKeyword)?.word in modifiable) {
            val t = tokens[i] as Tok.ModifierKeyword
            if (t.word == "priority") {
                priority = expectInt(tokens, i + 1, "priority of '$ruleName'")
                i += 2
            } else {
                enabled = t.word != "disabled"
                i++
            }
        }
        return Modifiers(priority, enabled, i)
    }

    private data class ActionParams(
        val rate: Int? = null,
        val status: Int? = null,
        val body: String? = null,
        val tagName: String? = null,
    )

    /** Consumes trailing `rate=/status=/body=/name=` params after the action. */
    private fun parseActionParams(tokens: List<Tok>, start: Int): Pair<ActionParams, Int> {
        var rate: Int? = null
        var status: Int? = null
        var body: String? = null
        var tagName: String? = null
        var i = start
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
        return ActionParams(rate, status, body, tagName) to i
    }

    /** Parses one `rule ...` definition starting after the `rule` keyword. */
    private fun parseRule(tokens: List<Tok>, start: Int): Pair<Rule, Int> {
        var i = start
        val name = expectIdent(tokens, i, "rule name").also { i++ }

        val mods = parseModifiers(tokens, i, name)
        i = mods.next

        expectKeyword(tokens, i, "when").also { i++ }
        val (condition, afterExpr) = parseOr(tokens, i)
        i = afterExpr

        expectKeyword(tokens, i, "then").also { i++ }
        val actionTok = tokens.getOrNull(i) as? Tok.ActionKeyword
            ?: throw IllegalArgumentException(
                "expected action at rule '$name', got ${tokens.getOrNull(i)?.describe() ?: "end of input"}",
            )
        i++
        val action = actionTok.action

        val (params, afterParams) = parseActionParams(tokens, i)
        i = afterParams

        val rule = Rule(
            name = name,
            priority = mods.priority,
            enabled = mods.enabled,
            action = action,
            condition = condition,
            throttleRateKibPerS = params.rate,
            mockStatus = params.status,
            mockBody = params.body,
            tagName = params.tagName,
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
        val t = requireNotNull(tokens.getOrNull(start)) { "unexpected end of condition" }
        if (t is Tok.OpenParen) {
            val (expr, after) = parseOr(tokens, start + 1)
            require(tokens.getOrNull(after) is Tok.CloseParen) { "expected ')' at token ${after}" }
            return expr to after + 1
        }

        // `true` literal for empty-match rules.
        if (t is Tok.Ident && t.value == "true") {
            return RuleCondition.Always to start + 1
        }

        val fieldTok = t as? Tok.Ident
        requireNotNull(fieldTok) { "expected field name, got ${t.describe()}" }
        val field = RuleField.fromToken(fieldTok.value)
        requireNotNull(field) { "unknown field '${fieldTok.value}'" }
        val opTok = tokens.getOrNull(start + 1) as? Tok.Op
        requireNotNull(opTok) {
            "expected operator after '${field.displayName}', got " +
                "${tokens.getOrNull(start + 1)?.describe() ?: "end"}"
        }
        val op = RuleOp.fromToken(opTok.symbol)
        requireNotNull(op) { "unknown operator '${opTok.symbol}'" }

        // Value: single literal or comma-separated list (only for `in`).
        val (value, after) = parseValue(tokens, start + 2, op)
        return RuleCondition.Field(field, op, value) to after
    }

    private fun parseValue(tokens: List<Tok>, start: Int, op: RuleOp): Pair<ConditionValue, Int> {
        val first = requireNotNull(tokens.getOrNull(start)) {
            "expected value after operator '${op.symbol}'"
        }
        val firstValue = requireNotNull(first.toConditionValue()) {
            "expected value, got ${first.describe()}"
        }
        var i = start + 1
        if (op != RuleOp.IN) return firstValue to i

        val items = mutableListOf(firstValue)
        while (tokens.getOrNull(i) is Tok.Comma) {
            val next = requireNotNull(tokens.getOrNull(i + 1)) { "dangling ',' in list value" }
            items.add(
                requireNotNull(next.toConditionValue()) {
                    "expected value after ',', got ${next.describe()}"
                },
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

    /** Scans a double-quoted string with backslash escapes; [start] points at the opening quote. */
    private fun scanQuoted(text: String, start: Int, what: String): Pair<String, Int> {
        val n = text.length
        val sb = StringBuilder()
        var j = start + 1
        while (j < n && text[j] != '"') {
            if (text[j] == '\\' && j + 1 < n) {
                sb.append(unescape(text[j + 1]))
                j += 2
            } else {
                sb.append(text[j])
                j++
            }
        }
        require(j < n) { "unterminated $what at offset $start" }
        return sb.toString() to j + 1
    }

    /** Scans a `word=value` parameter; [i] points at the '='. */
    private fun scanParam(text: String, word: String, i: Int): Pair<Tok.Param, Int> {
        val n = text.length
        return if (i + 1 < n && text[i + 1] == '"') {
            val (value, next) = scanQuoted(text, i + 1, "param string for '$word'")
            Tok.Param(word, value) to next
        } else {
            var k = i + 1
            while (k < n && !text[k].isWhitespace()) k++
            Tok.Param(word, text.substring(i + 1, k)) to k
        }
    }

    /** Single-character punctuation: ( ) , */
    private fun tokenizePunct(c: Char): Tok = when (c) {
        '(' -> Tok.OpenParen
        ')' -> Tok.CloseParen
        ',' -> Tok.Comma
        else -> throw IllegalArgumentException("unexpected punctuation '$c'")
    }

    /** Dispatches one token starting at [i]; returns the next index. */
    private fun tokenizeOne(text: String, i: Int, tokens: MutableList<Tok>): Int {
        val n = text.length
        val c = text[i]
        return when {
            c.isWhitespace() -> i + 1
            c == '#' -> emit(tokens, tokenizeComment(text, i))
            c == '"' -> emit(tokens, scanQuoted(text, i, "string").let { (v, next) -> Tok.StrLit(v) to next })
            c in "()," -> {
                tokens.add(tokenizePunct(c))
                i + 1
            }
            c == '>' || c == '<' || c == '!' || c == '=' -> emit(tokens, tokenizeOperator(text, i))
            c.isDigit() || (c == '-' && i + 1 < n && text[i + 1].isDigit()) ->
                emit(tokens, tokenizeInt(text, i))
            else -> emit(tokens, tokenizeWord(text, i))
        }
    }

    private inline fun <reified T : Tok> emit(tokens: MutableList<Tok>, pair: Pair<T, Int>): Int {
        tokens.add(pair.first)
        return pair.second
    }

    private fun tokenize(text: String): List<Tok> {
        val tokens = mutableListOf<Tok>()
        var i = 0
        while (i < text.length) {
            i = tokenizeOne(text, i, tokens)
        }
        return tokens
    }

    private fun tokenizeComment(text: String, start: Int): Pair<Tok.Comment, Int> {
        val end = text.indexOf('\n', start)
        val stop = if (end == -1) text.length else end
        return Tok.Comment(text.substring(start + 1, stop)) to stop
    }

    private fun tokenizeOperator(text: String, i: Int): Pair<Tok.Op, Int> {
        val c = text[i]
        if (i + 1 < text.length && text[i + 1] == '=') {
            return Tok.Op(text.substring(i, i + 2)) to i + 2
        }
        if (c == '=') return Tok.Op("=") to i + 1
        require(c != '!') { "lone '!' at offset $i (use !=)" }
        return Tok.Op(c.toString()) to i + 1
    }

    private fun tokenizeInt(text: String, start: Int): Pair<Tok.IntLit, Int> {
        var j = start
        while (j < text.length && text[j].isDigit()) j++
        return Tok.IntLit(text.substring(start, j).toLong()) to j
    }

    private fun tokenizeWord(text: String, start: Int): Pair<Tok, Int> {
        val n = text.length
        var j = start
        while (j < n && !text[j].isWhitespace() && text[j] !in "()\",#<>!=") j++
        require(j > start) { "unexpected character '${text[start]}' at offset $start" }
        val word = text.substring(start, j)
        // `word=param` form
        if (j < n && text[j] == '=') {
            return scanParam(text, word, j)
        }
        return keywordOrIdent(word) to j
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
