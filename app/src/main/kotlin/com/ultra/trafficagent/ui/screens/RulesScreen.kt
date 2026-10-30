package com.ultra.trafficagent.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.FilterChip
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.Switch
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.ultra.trafficagent.transform.Phase
import com.ultra.trafficagent.transform.RuleAction
import com.ultra.trafficagent.transform.RuleMatch
import com.ultra.trafficagent.transform.RewriteRule

/** Short human summary of an action, shown on the rule card. */
fun actionSummary(action: RuleAction): String = when (action) {
    is RuleAction.SetHeader -> "set ${if (action.phase == Phase.REQUEST) "req" else "resp"} header ${action.name}"
    is RuleAction.RemoveHeader -> "del ${if (action.phase == Phase.REQUEST) "req" else "resp"} header ${action.name}"
    is RuleAction.ReplacePath -> "path ${action.pattern} -> ${action.replacement}"
    is RuleAction.ReplaceBody -> "body ${if (action.phase == Phase.REQUEST) "req" else "resp"} ${action.pattern}"
    is RuleAction.Redirect -> "-> ${action.host}${action.path}"
    is RuleAction.SetStatus -> "status ${action.code}"
    is RuleAction.DelayMs -> "delay ${action.millis}ms"
    is RuleAction.MockResponse -> "mock ${action.status} ${action.contentType}"
    is RuleAction.Block -> "block ${action.status}"
    is RuleAction.Abort -> "abort after ${action.timeoutMs}ms"
    is RuleAction.ReplaceQueryParam -> "query ${action.name}=${action.value}"
    is RuleAction.MapRemote -> "map remote ${action.targetHost}" +
        (action.targetPort?.let { ":$it" } ?: "")
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun RulesScreen(
    rules: List<RewriteRule>,
    hitCounts: Map<String, Long>,
    onToggleRule: (String) -> Unit,
    onDeleteRule: (String) -> Unit,
    onAddRule: (RewriteRule) -> Unit,
    onExportRulepack: () -> Unit = {},
    onImportRulepack: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    var showAddDialog by remember { mutableStateOf(false) }
    var menuOpen by remember { mutableStateOf(false) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Rewrite rules") },
                actions = {
                    IconButton(onClick = { menuOpen = true }) {
                        Icon(Icons.Filled.MoreVert, contentDescription = "Rulepack menu")
                    }
                    DropdownMenu(expanded = menuOpen, onDismissRequest = { menuOpen = false }) {
                        DropdownMenuItem(
                            text = { Text("Export rulepack (.tarule.json)") },
                            onClick = {
                                menuOpen = false
                                onExportRulepack()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Import rulepack…") },
                            onClick = {
                                menuOpen = false
                                onImportRulepack()
                            },
                        )
                    }
                },
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Filled.Add, contentDescription = "Add rule")
            }
        },
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding).fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(rules, key = { it.id }) { rule ->
                Card(Modifier.fillMaxWidth()) {
                    Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(rule.name, style = MaterialTheme.typography.titleMedium)
                                Spacer(Modifier.width(8.dp))
                                val hits = hitCounts[rule.id] ?: 0L
                                if (hits > 0) {
                                    Text(
                                        "$hits hits",
                                        style = MaterialTheme.typography.labelMedium,
                                        color = MaterialTheme.colorScheme.tertiary,
                                    )
                                }
                            }
                            Text(
                                rule.match.hostRegex?.let { "host ~ $it" }
                                    ?: rule.match.pathRegex?.let { "path ~ $it" }
                                    ?: "matches everything",
                                style = MaterialTheme.typography.bodyMedium,
                                fontFamily = FontFamily.Monospace,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Text(
                                rule.actions.joinToString(" · ") { actionSummary(it) },
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 2,
                            )
                            Text(
                                "priority ${rule.priority}",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        Switch(checked = rule.enabled, onCheckedChange = { onToggleRule(rule.id) })
                        IconButton(onClick = { onDeleteRule(rule.id) }) {
                            Icon(Icons.Filled.Delete, contentDescription = "Delete rule")
                        }
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        AddRuleDialog(
            onDismiss = { showAddDialog = false },
            onConfirm = { rule ->
                onAddRule(rule)
                showAddDialog = false
            },
        )
    }
}

/** The 12 creatable action types, in editor order. */
private val ACTION_TYPES = listOf(
    "Header", "Mock", "Block", "Status", "Redirect", "Path",
    "Body", "Delay", "Abort", "Query", "MapRemote", "DelHeader",
)

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun AddRuleDialog(onDismiss: () -> Unit, onConfirm: (RewriteRule) -> Unit) {
    var name by remember { mutableStateOf("") }
    var hostRegex by remember { mutableStateOf("") }
    var pathRegex by remember { mutableStateOf("") }
    var priorityText by remember { mutableStateOf("50") }
    var actionType by remember { mutableStateOf(0) }

    // Shared fields for several action types.
    var headerName by remember { mutableStateOf("") }
    var headerValue by remember { mutableStateOf("") }
    var mockBody by remember { mutableStateOf("") }
    var statusText by remember { mutableStateOf("403") }
    var redirectHost by remember { mutableStateOf("") }
    var redirectPath by remember { mutableStateOf("/") }
    var patternText by remember { mutableStateOf("") }
    var replacementText by remember { mutableStateOf("") }
    var delayText by remember { mutableStateOf("500") }
    var queryName by remember { mutableStateOf("") }
    var queryValue by remember { mutableStateOf("") }
    var mapHost by remember { mutableStateOf("") }
    var mapPort by remember { mutableStateOf("") }
    var mapKeepHost by remember { mutableStateOf(false) }

    val canConfirm = name.isNotBlank() && when (ACTION_TYPES[actionType]) {
        "Header", "DelHeader" -> headerName.isNotBlank()
        "Redirect" -> redirectHost.isNotBlank()
        "Path", "Body" -> patternText.isNotBlank()
        "Query" -> queryName.isNotBlank()
        "MapRemote" -> mapHost.isNotBlank()
        else -> true
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("New rewrite rule") },
        text = {
            Column(
                Modifier
                    .height(420.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Rule name") },
                    singleLine = true,
                )
                OutlinedTextField(
                    value = hostRegex,
                    onValueChange = { hostRegex = it },
                    label = { Text("Host regex (blank = any)") },
                    singleLine = true,
                )
                OutlinedTextField(
                    value = pathRegex,
                    onValueChange = { pathRegex = it },
                    label = { Text("Path regex (blank = any)") },
                    singleLine = true,
                )
                OutlinedTextField(
                    value = priorityText,
                    onValueChange = { priorityText = it.filter { c -> c.isDigit() || c == '-' } },
                    label = { Text("Priority (higher runs first)") },
                    singleLine = true,
                )
                Text("Action type", style = MaterialTheme.typography.labelMedium)
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    ACTION_TYPES.forEachIndexed { index, label ->
                        FilterChip(
                            selected = actionType == index,
                            onClick = { actionType = index },
                            label = { Text(label, style = MaterialTheme.typography.labelSmall) },
                        )
                    }
                }
                when (ACTION_TYPES[actionType]) {
                    "Header" -> {
                        OutlinedTextField(headerName, { headerName = it }, label = { Text("Header name") }, singleLine = true)
                        OutlinedTextField(headerValue, { headerValue = it }, label = { Text("Header value") }, singleLine = true)
                    }
                    "DelHeader" -> OutlinedTextField(headerName, { headerName = it }, label = { Text("Header name") }, singleLine = true)
                    "Mock" -> OutlinedTextField(mockBody, { mockBody = it }, label = { Text("Mock response body (JSON)") })
                    "Block" -> Text(
                        "Blocked requests answer ${statusText.toIntOrNull() ?: 403} without contacting the origin.",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    "Status" -> OutlinedTextField(statusText, { statusText = it.filter(Char::isDigit) }, label = { Text("Status code") }, singleLine = true)
                    "Redirect" -> {
                        OutlinedTextField(redirectHost, { redirectHost = it }, label = { Text("Redirect host") }, singleLine = true)
                        OutlinedTextField(redirectPath, { redirectPath = it }, label = { Text("Redirect path") }, singleLine = true)
                    }
                    "Path" -> {
                        OutlinedTextField(patternText, { patternText = it }, label = { Text("Path regex") }, singleLine = true)
                        OutlinedTextField(replacementText, { replacementText = it }, label = { Text("Replacement") }, singleLine = true)
                    }
                    "Body" -> {
                        OutlinedTextField(patternText, { patternText = it }, label = { Text("Body regex") }, singleLine = true)
                        OutlinedTextField(replacementText, { replacementText = it }, label = { Text("Replacement") }, singleLine = true)
                    }
                    "Delay" -> OutlinedTextField(delayText, { delayText = it.filter(Char::isDigit) }, label = { Text("Delay (ms)") }, singleLine = true)
                    "Abort" -> OutlinedTextField(delayText, { delayText = it.filter(Char::isDigit) }, label = { Text("Timeout after (ms)") }, singleLine = true)
                    "Query" -> {
                        OutlinedTextField(queryName, { queryName = it }, label = { Text("Query param name") }, singleLine = true)
                        OutlinedTextField(queryValue, { queryValue = it }, label = { Text("Value") }, singleLine = true)
                    }
                    "MapRemote" -> {
                        OutlinedTextField(mapHost, { mapHost = it }, label = { Text("Target host") }, singleLine = true)
                        OutlinedTextField(mapPort, { mapPort = it.filter(Char::isDigit) }, label = { Text("Target port (blank = default)") }, singleLine = true)
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(checked = mapKeepHost, onCheckedChange = { mapKeepHost = it })
                            Spacer(Modifier.width(8.dp))
                            Text("Keep original Host header", style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    val action = when (ACTION_TYPES[actionType]) {
                        "Header" -> RuleAction.SetHeader(Phase.REQUEST, headerName.trim(), headerValue.trim())
                        "DelHeader" -> RuleAction.RemoveHeader(Phase.REQUEST, headerName.trim())
                        "Mock" -> RuleAction.MockResponse(200, mockBody.ifBlank { """{"mocked":true}""" })
                        "Block" -> RuleAction.Block(statusText.toIntOrNull() ?: 403)
                        "Status" -> RuleAction.SetStatus(statusText.toIntOrNull() ?: 200)
                        "Redirect" -> RuleAction.Redirect(redirectHost.trim(), redirectPath.ifBlank { "/" })
                        "Path" -> RuleAction.ReplacePath(patternText.trim(), replacementText.trim())
                        "Body" -> RuleAction.ReplaceBody(Phase.RESPONSE, patternText.trim(), replacementText.trim())
                        "Delay" -> RuleAction.DelayMs(delayText.toLongOrNull() ?: 500)
                        "Abort" -> RuleAction.Abort(delayText.toLongOrNull() ?: 1_000)
                        "Query" -> RuleAction.ReplaceQueryParam(queryName.trim(), queryValue.trim())
                        "MapRemote" -> RuleAction.MapRemote(
                            targetHost = mapHost.trim(),
                            targetPort = mapPort.toIntOrNull(),
                            keepHostHeader = mapKeepHost,
                        )
                        else -> return@TextButton
                    }
                    val match = RuleMatch(
                        hostRegex = hostRegex.trim().ifBlank { null },
                        pathRegex = pathRegex.trim().ifBlank { null },
                    )
                    onConfirm(
                        RewriteRule(
                            id = "rule-${System.currentTimeMillis()}",
                            name = name.trim(),
                            enabled = true,
                            priority = priorityText.toIntOrNull() ?: 50,
                            match = match,
                            actions = listOf(action),
                        ),
                    )
                },
                enabled = canConfirm,
            ) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        },
    )
}
