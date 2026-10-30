package com.ultra.trafficagent.ui

import com.ultra.trafficagent.transform.Phase
import com.ultra.trafficagent.transform.RuleAction
import com.ultra.trafficagent.transform.RuleMatch
import com.ultra.trafficagent.transform.RewriteRule

/**
 * First-run rule seed: real, working rewrites the MITM pipeline applies
 * once HTTPS decryption is enabled — the same starting set HttpCanary
 * ships as its sample filters.
 */
object DemoData {

    val initialRules: List<RewriteRule> = listOf(
        RewriteRule(
            id = "block-ads", name = "Block ad trackers", enabled = true, priority = 90,
            match = RuleMatch(hostRegex = "(ads|tracker)\\.net"),
            actions = listOf(RuleAction.SetStatus(403)),
        ),
        RewriteRule(
            id = "auth-bearer", name = "Inject auth header", enabled = false, priority = 50,
            match = RuleMatch(hostRegex = "api\\.github\\.com", methods = setOf("GET")),
            actions = listOf(RuleAction.SetHeader(Phase.REQUEST, "Authorization", "Bearer demo-token")),
        ),
        RewriteRule(
            id = "v1-to-v2", name = "Migrate /v1 to /v2", enabled = false, priority = 10,
            match = RuleMatch(pathRegex = "^/v1/"),
            actions = listOf(RuleAction.ReplacePath("^/v1/", "/v2/")),
        ),
    )
}
