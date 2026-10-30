package com.ultra.trafficagent.transform

import com.ultra.trafficagent.transform.MiniJson.Json
import com.ultra.trafficagent.transform.MiniJson.asArrayOrNull
import com.ultra.trafficagent.transform.MiniJson.asBooleanOrNull
import com.ultra.trafficagent.transform.MiniJson.asIntOrNull
import com.ultra.trafficagent.transform.MiniJson.asLongOrNull
import com.ultra.trafficagent.transform.MiniJson.asStringOrNull

/**
 * Rulepack serialization: [RewriteRule] sets <-> portable JSON documents
 * (`.tarule.json`). The format is self-describing and versioned so future
 * migrations stay mechanical:
 *
 * {
 *   "version": 1,
 *   "rules": [
 *     {
 *       "id": "block-ads", "name": "Block ad trackers",
 *       "enabled": true, "priority": 90,
 *       "match": { "host": "(ads|tracker)\\.net", "path": null,
 *                  "methods": ["GET"], "headers": {"x-a": "1"} },
 *       "actions": [ {"type": "setStatus", "code": 403}, ... ]
 *     }
 *   ]
 * }
 */
object RuleCodec {

    const val FORMAT_VERSION = 1

    class RuleFormatException(message: String) : Exception(message)

    // ------------------------------------------------------------- encode

    fun encodeRulepack(rules: List<RewriteRule>): String {
        val ruleJsons = rules.map { encodeRule(it) }
        return MiniJson.write(
            MiniJson.obj(
                "version" to MiniJson.num(FORMAT_VERSION.toLong()),
                "rules" to MiniJson.arr(ruleJsons),
            ),
        )
    }

    fun encodeRule(rule: RewriteRule): Json.Obj {
        val matchFields = LinkedHashMap<String, Json>()
        matchFields["host"] = rule.match.hostRegex?.let { MiniJson.str(it) } ?: Json.Null
        matchFields["path"] = rule.match.pathRegex?.let { MiniJson.str(it) } ?: Json.Null
        matchFields["methods"] = MiniJson.arr(rule.match.methods.map { MiniJson.str(it) })
        matchFields["headers"] = MiniJson.obj(
            rule.match.headerEquals.map { (k, v) -> k to MiniJson.str(v) },
        )
        return MiniJson.obj(
            "id" to MiniJson.str(rule.id),
            "name" to MiniJson.str(rule.name),
            "enabled" to Json.Bool(rule.enabled),
            "priority" to MiniJson.num(rule.priority.toLong()),
            "match" to Json.Obj(matchFields),
            "actions" to MiniJson.arr(rule.actions.map { encodeAction(it) }),
        )
    }

    private fun encodeAction(action: RuleAction): Json.Obj = when (action) {
        is RuleAction.SetHeader -> MiniJson.obj(
            "type" to MiniJson.str("setHeader"),
            "phase" to MiniJson.str(action.phase.name),
            "name" to MiniJson.str(action.name),
            "value" to MiniJson.str(action.value),
        )
        is RuleAction.RemoveHeader -> MiniJson.obj(
            "type" to MiniJson.str("removeHeader"),
            "phase" to MiniJson.str(action.phase.name),
            "name" to MiniJson.str(action.name),
        )
        is RuleAction.ReplacePath -> MiniJson.obj(
            "type" to MiniJson.str("replacePath"),
            "pattern" to MiniJson.str(action.pattern),
            "replacement" to MiniJson.str(action.replacement),
        )
        is RuleAction.ReplaceBody -> MiniJson.obj(
            "type" to MiniJson.str("replaceBody"),
            "phase" to MiniJson.str(action.phase.name),
            "pattern" to MiniJson.str(action.pattern),
            "replacement" to MiniJson.str(action.replacement),
            "max" to MiniJson.num(action.maxReplacements.toLong()),
        )
        is RuleAction.Redirect -> MiniJson.obj(
            "type" to MiniJson.str("redirect"),
            "host" to MiniJson.str(action.host),
            "path" to MiniJson.str(action.path),
        )
        is RuleAction.SetStatus -> MiniJson.obj(
            "type" to MiniJson.str("setStatus"),
            "code" to MiniJson.num(action.code.toLong()),
        )
        is RuleAction.DelayMs -> MiniJson.obj(
            "type" to MiniJson.str("delay"),
            "millis" to MiniJson.num(action.millis),
        )
        is RuleAction.MockResponse -> MiniJson.obj(
            "type" to MiniJson.str("mock"),
            "status" to MiniJson.num(action.status.toLong()),
            "body" to MiniJson.str(action.body),
            "contentType" to MiniJson.str(action.contentType),
        )
        is RuleAction.Block -> MiniJson.obj(
            "type" to MiniJson.str("block"),
            "status" to MiniJson.num(action.status.toLong()),
            "reason" to MiniJson.str(action.reason),
        )
        is RuleAction.Abort -> MiniJson.obj(
            "type" to MiniJson.str("abort"),
            "timeoutMs" to MiniJson.num(action.timeoutMs),
        )
        is RuleAction.ReplaceQueryParam -> MiniJson.obj(
            "type" to MiniJson.str("queryParam"),
            "name" to MiniJson.str(action.name),
            "value" to MiniJson.str(action.value),
        )
        is RuleAction.MapRemote -> MiniJson.obj(
            "type" to MiniJson.str("mapRemote"),
            "targetHost" to MiniJson.str(action.targetHost),
            "targetPort" to (action.targetPort?.let { MiniJson.num(it.toLong()) } ?: Json.Null),
            "keepHostHeader" to Json.Bool(action.keepHostHeader),
        )
    }

    // ------------------------------------------------------------- decode

    fun decodeRulepack(text: String): List<RewriteRule> {
        val root = try {
            MiniJson.parse(text)
        } catch (e: MiniJson.JsonFormatException) {
            throw RuleFormatException("not valid JSON: ${e.message}")
        }
        val obj = root as? Json.Obj ?: throw RuleFormatException("root must be an object")
        val version = obj["version"].asIntOrNull()
            ?: throw RuleFormatException("missing version")
        if (version > FORMAT_VERSION) {
            throw RuleFormatException("rulepack version $version is newer than supported $FORMAT_VERSION")
        }
        val rulesJson = obj["rules"].asArrayOrNull()
            ?: throw RuleFormatException("missing rules array")
        return rulesJson.mapIndexed { i, r ->
            decodeRule(r, i) ?: throw RuleFormatException("rule #$i is malformed")
        }
    }

    /** Decodes one rule; returns null (rather than throwing) on soft errors. */
    fun decodeRule(json: Json, index: Int): RewriteRule? {
        val obj = json as? Json.Obj ?: return null
        val id = obj["id"].asStringOrNull()?.takeIf { it.isNotEmpty() }
            ?: "imported-$index"
        val name = obj["name"].asStringOrNull() ?: id
        val enabled = obj["enabled"].asBooleanOrNull() ?: true
        val priority = obj["priority"].asIntOrNull() ?: 0
        val match = decodeMatch(obj["match"]) ?: RuleMatch()
        val actionsJson = obj["actions"].asArrayOrNull() ?: emptyList()
        val actions = actionsJson.mapNotNull { decodeAction(it) }
        if (actions.isEmpty()) return null
        return RewriteRule(
            id = id,
            name = name,
            enabled = enabled,
            priority = priority,
            match = match,
            actions = actions,
        )
    }

    private fun decodeMatch(json: Json?): RuleMatch? {
        if (json == null || json is Json.Null) return RuleMatch()
        val obj = json as? Json.Obj ?: return null
        val methods = (obj["methods"].asArrayOrNull() ?: emptyList())
            .mapNotNull { it.asStringOrNull()?.uppercase() }
            .toSet()
        val headersJson = obj["headers"] as? Json.Obj
        val headers = headersJson?.fields?.mapValues { (_, v) ->
            v.asStringOrNull() ?: ""
        } ?: emptyMap()
        return RuleMatch(
            hostRegex = obj["host"].asStringOrNull(),
            pathRegex = obj["path"].asStringOrNull(),
            methods = methods,
            headerEquals = headers,
        )
    }

    private fun decodeAction(json: Json): RuleAction? {
        val obj = json as? Json.Obj ?: return null
        val phase = { name: String ->
            when (obj[name].asStringOrNull()?.uppercase()) {
                "REQUEST" -> Phase.REQUEST
                "RESPONSE" -> Phase.RESPONSE
                else -> Phase.REQUEST
            }
        }
        return when (obj["type"].asStringOrNull()) {
            "setHeader" -> obj["name"].asStringOrNull()?.let { name ->
                RuleAction.SetHeader(phase("phase"), name, obj["value"].asStringOrNull() ?: "")
            }
            "removeHeader" -> obj["name"].asStringOrNull()?.let { name ->
                RuleAction.RemoveHeader(phase("phase"), name)
            }
            "replacePath" -> {
                val pattern = obj["pattern"].asStringOrNull() ?: return null
                RuleAction.ReplacePath(pattern, obj["replacement"].asStringOrNull() ?: "")
            }
            "replaceBody" -> {
                val pattern = obj["pattern"].asStringOrNull() ?: return null
                RuleAction.ReplaceBody(
                    phase("phase"),
                    pattern,
                    obj["replacement"].asStringOrNull() ?: "",
                    obj["max"].asIntOrNull() ?: 10,
                )
            }
            "redirect" -> {
                val host = obj["host"].asStringOrNull() ?: return null
                RuleAction.Redirect(host, obj["path"].asStringOrNull() ?: "/")
            }
            "setStatus" -> obj["code"].asIntOrNull()?.let { RuleAction.SetStatus(it) }
            "delay" -> obj["millis"].asLongOrNull()?.let { RuleAction.DelayMs(it) }
            "mock" -> RuleAction.MockResponse(
                status = obj["status"].asIntOrNull() ?: 200,
                body = obj["body"].asStringOrNull() ?: "",
                contentType = obj["contentType"].asStringOrNull() ?: "application/json",
            )
            "block" -> RuleAction.Block(
                status = obj["status"].asIntOrNull() ?: 403,
                reason = obj["reason"].asStringOrNull() ?: "Blocked by Traffic Agent",
            )
            "abort" -> obj["timeoutMs"].asLongOrNull()?.let { RuleAction.Abort(it) }
            "queryParam" -> {
                val name = obj["name"].asStringOrNull() ?: return null
                RuleAction.ReplaceQueryParam(name, obj["value"].asStringOrNull() ?: "")
            }
            "mapRemote" -> {
                val host = obj["targetHost"].asStringOrNull() ?: return null
                RuleAction.MapRemote(
                    targetHost = host,
                    targetPort = obj["targetPort"].asIntOrNull(),
                    keepHostHeader = obj["keepHostHeader"].asBooleanOrNull() ?: false,
                )
            }
            else -> null
        }
    }
}
