package com.ultra.trafficagent.transform

import com.ultra.trafficagent.transform.MiniJson.Json
import com.ultra.trafficagent.transform.MiniJson.asArrayOrNull
import com.ultra.trafficagent.transform.MiniJson.asBooleanOrNull
import com.ultra.trafficagent.transform.MiniJson.asLongOrNull
import com.ultra.trafficagent.transform.MiniJson.asStringOrNull
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Mutation-killer edge cases for [MiniJson] and [RuleCodec]: exact escape
 * handling, parser failure positions, numeric forms and decode defaults.
 */
class MutationKillersTest {

    // ------------------------------------------------------------- MiniJson

    @Test
    fun `writer escapes every control character exactly`() {
        val text = "a" + '\b' + '' + '\n' + '\r' + '\t' + "end"
        val encoded = MiniJson.write(MiniJson.str(text))
        // Round trip is the real contract.
        assertEquals(text, (MiniJson.parse(encoded) as Json.Str).value)
        assertTrue(encoded.contains("""\b"""))
        assertTrue(encoded.contains("""\f"""))
        assertTrue(encoded.contains("""\n"""))
        assertTrue(encoded.contains("""\r"""))
        assertTrue(encoded.contains("""\t"""))
    }

    @Test
    fun `unicode control chars escape as u sequences`() {
        val text = "\u0001\u001F"
        val encoded = MiniJson.write(MiniJson.str(text))
        assertEquals(text, (MiniJson.parse(encoded) as Json.Str).value)
        assertTrue(encoded.contains("\\u0001"))
        assertTrue(encoded.contains("\\u001f"))
    }

    @Test
    fun `parse honours escapes and nested containers`() {
        val doc = "{\"k\":\"a\\\"b\\\\c\\/d\",\"arr\":[{\"x\":[[]]}],\"n\":{}}"
        val root = MiniJson.parse(doc) as Json.Obj
        assertEquals("a\"b\\c/d", (root["k"] as Json.Str).value)
        val arr = root["arr"] as Json.Arr
        val x = (arr.items[0] as Json.Obj)["x"] as Json.Arr
        assertTrue((x.items[0] as Json.Arr).items.isEmpty())
        assertTrue((root["n"] as Json.Obj).fields.isEmpty())
    }

    @Test
    fun `parse handles all literal forms`() {
        assertEquals(true, (MiniJson.parse("true") as Json.Bool).value)
        assertEquals(false, (MiniJson.parse("false") as Json.Bool).value)
        assertEquals(Json.Null, MiniJson.parse("null"))
        assertEquals(-42.0, (MiniJson.parse("-42") as Json.Num).value)
        assertEquals(3.5, (MiniJson.parse("3.5") as Json.Num).value)
        assertEquals(1.25e3, (MiniJson.parse("1.25e3") as Json.Num).value)
        assertEquals(1.25E-3, (MiniJson.parse("1.25E-3") as Json.Num).value)
        assertEquals(7.0, (MiniJson.parse("+7".replace("+", "")) as Json.Num).value)
    }

    @Test
    fun `parse rejects malformed documents at exact positions`() {
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("{") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("[1,") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("{\"a\" 1}") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("tru") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("\"unterminated") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("\\q") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("{\"a\":1} trailing") }
        assertThrows(MiniJson.JsonFormatException::class.java) { MiniJson.parse("1 2") }
    }

    fun `parse tolerates whitespace between tokens`() {
        val root = MiniJson.parse("  {  \"a\" : [ 1 , 2 ] , \"b\" : true }  ") as Json.Obj
        assertEquals(2, (root["a"] as Json.Arr).items.size)
        assertEquals(true, (root["b"] as Json.Bool).value)
    }

    @Test
    fun `writer emits integral numbers without decimals`() {
        assertEquals("5", MiniJson.write(MiniJson.num(5)))
        assertEquals("5.5", MiniJson.write(Json.Num(5.5)))
        assertEquals("[]", MiniJson.write(MiniJson.arr(emptyList())))
    }

    @Test
    fun `accessors reject wrong json types`() {
        val obj: MiniJson.Json? = Json.Obj(LinkedHashMap())
        assertEquals(null, obj.asStringOrNull())
        assertEquals(null, obj.asLongOrNull())
        assertEquals(null, obj.asBooleanOrNull())
        assertEquals(null, obj.asArrayOrNull())
    }

    // ------------------------------------------------------------ RuleCodec

    @Test
    fun `decode fills defaults for optional fields`() {
        val rule = RuleCodec.decodeRulepack(
            """{"version":1,"rules":[{"id":"m","name":"m",
               "match":{},
               "actions":[{"type":"mock"},{"type":"block"},{"type":"delay","millis":0}]}]}""",
        )[0]
        val mock = rule.actions[0] as RuleAction.MockResponse
        assertEquals(200, mock.status)
        assertEquals("", mock.body)
        assertEquals("application/json", mock.contentType)
        val block = rule.actions[1] as RuleAction.Block
        assertEquals(403, block.status)
        assertEquals("Blocked by Traffic Agent", block.reason)
        val delay = rule.actions[2] as RuleAction.DelayMs
        assertEquals(0L, delay.millis)
    }

    @Test
    fun `decode lowercases methods and phases case-insensitively`() {
        val rule = RuleCodec.decodeRulepack(
            """{"version":1,"rules":[{"id":"x","name":"x",
               "match":{"methods":["get","PoSt"]},
               "actions":[{"type":"setHeader","phase":"RESPONSE","name":"A","value":"1"}]}]}""",
        )[0]
        assertEquals(setOf("GET", "POST"), rule.match.methods)
        assertEquals(Phase.RESPONSE, (rule.actions[0] as RuleAction.SetHeader).phase)
    }

    @Test
    fun `decode rejects actions missing required strings`() {
        val text = """{"version":1,"rules":[
            {"id":"a","name":"a","actions":[{"type":"replacePath","pattern":null}]},
            {"id":"b","name":"b","actions":[{"type":"redirect"}]},
            {"id":"c","name":"c","actions":[{"type":"queryParam"}]},
            {"id":"d","name":"d","actions":[{"type":"mapRemote"}]}
        ]}"""
        assertThrows(RuleCodec.RuleFormatException::class.java) { RuleCodec.decodeRulepack(text) }
    }

    @Test
    fun `decode replaces absent max and ports with defaults`() {
        val rule = RuleCodec.decodeRulepack(
            """{"version":1,"rules":[{"id":"r","name":"r",
               "actions":[{"type":"replaceBody","pattern":"a","replacement":"b"},
                          {"type":"mapRemote","targetHost":"h.com"}]}]}""",
        )[0]
        assertEquals(10, (rule.actions[0] as RuleAction.ReplaceBody).maxReplacements)
        assertEquals(null, (rule.actions[1] as RuleAction.MapRemote).targetPort)
        assertEquals(false, (rule.actions[1] as RuleAction.MapRemote).keepHostHeader)
    }

    @Test
    fun `encode nulls are explicit for optional match fields`() {
        val text = RuleCodec.encodeRulepack(
            listOf(
                RewriteRule(
                    id = "n", name = "n",
                    match = RuleMatch(),
                    actions = listOf(RuleAction.DelayMs(1)),
                ),
            ),
        )
        assertTrue(text.contains("\"host\":null"))
        assertTrue(text.contains("\"path\":null"))
    }

    @Test
    fun `encode decode mapRemote with port round trips`() {
        val rules = listOf(
            RewriteRule(
                id = "mp", name = "mp",
                match = RuleMatch(hostRegex = "a.com"),
                actions = listOf(RuleAction.MapRemote("b.com", 8443, keepHostHeader = true)),
            ),
        )
        assertEquals(rules, RuleCodec.decodeRulepack(RuleCodec.encodeRulepack(rules)))
    }
}
