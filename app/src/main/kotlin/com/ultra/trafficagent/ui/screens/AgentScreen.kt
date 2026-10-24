package com.ultra.trafficagent.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.ultra.trafficagent.agent.RiskLevel
import com.ultra.trafficagent.agent.RiskPolicy
import com.ultra.trafficagent.agent.RiskGate
import com.ultra.trafficagent.agent.ToolRisk

private data class AuditRow(val tool: String, val decision: String, val detail: String)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AgentScreen(modifier: Modifier = Modifier) {
    val gate = remember { RiskGate(RiskPolicy(maxLevel = RiskLevel.CAUTION)) }
    val tools = remember { ToolRisk.map.entries.sortedBy { it.key } }
    val audit = remember {
        listOf(
            AuditRow("list_requests", "allowed", "read-only store query"),
            AuditRow("modify_header", "allowed", "auth-bearer rule applied"),
            AuditRow("modify_body", "denied", "exceeds policy level CAUTION"),
            AuditRow("install_cert", "denied", "approval required"),
        )
    }

    Scaffold(
        modifier = modifier,
        topBar = { TopAppBar(title = { Text("Agent console") }) },
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding).fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item {
                Card {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text("Risk policy", style = MaterialTheme.typography.titleMedium)
                        Text(
                            "Max level: CAUTION · approval required from CRITICAL",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            "The Python sidecar enforces the same table; this console previews decisions.",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
            item {
                Text("Tool registry", style = MaterialTheme.typography.titleMedium)
            }
            items(tools, key = { it.key }) { (tool, risk) ->
                val decision = gate.evaluate(tool)
                Card {
                    Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(tool, style = MaterialTheme.typography.bodyLarge, fontFamily = FontFamily.Monospace)
                            Text(
                                if (decision.allowed) "allowed by policy" else (decision.reason ?: "denied"),
                                style = MaterialTheme.typography.labelMedium,
                                color = if (decision.allowed) {
                                    MaterialTheme.colorScheme.onSurfaceVariant
                                } else {
                                    MaterialTheme.colorScheme.error
                                },
                            )
                        }
                        RiskBadge(risk)
                    }
                }
            }
            item {
                Spacer(Modifier.height(4.dp))
                Text("Audit log (demo)", style = MaterialTheme.typography.titleMedium)
            }
            items(audit, key = { it.tool + it.decision }) { row ->
                Card {
                    Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            row.decision,
                            style = MaterialTheme.typography.labelLarge,
                            color = if (row.decision == "allowed") {
                                MaterialTheme.colorScheme.primary
                            } else {
                                MaterialTheme.colorScheme.error
                            },
                        )
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text(row.tool, style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace)
                            Text(
                                row.detail,
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RiskBadge(level: RiskLevel) {
    val (label, color) = when (level) {
        RiskLevel.SAFE -> "SAFE" to MaterialTheme.colorScheme.primary
        RiskLevel.CAUTION -> "CAUTION" to MaterialTheme.colorScheme.tertiary
        RiskLevel.DANGEROUS -> "DANGER" to MaterialTheme.colorScheme.error
        RiskLevel.CRITICAL -> "CRITICAL" to MaterialTheme.colorScheme.error
    }
    Text(
        label,
        style = MaterialTheme.typography.labelMedium,
        color = color,
        modifier = Modifier
            .background(color.copy(alpha = 0.12f), RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp),
    )
}
