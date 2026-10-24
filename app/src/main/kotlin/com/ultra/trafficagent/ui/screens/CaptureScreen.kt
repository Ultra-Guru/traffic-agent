package com.ultra.trafficagent.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol

private enum class CaptureFilter(val label: String) {
    ALL("All"), HTTP("HTTP"), TLS("TLS"), WEBSOCKET("WS"), ERROR("Error");
}

/**
 * Parses the inline query with the same DSL the core [FilterEngine] uses:
 * "host:weibo status:4xx size>1024". Falls back to plain keyword search on
 * malformed input so typing never blocks the list.
 */
private fun filterWithQuery(requests: List<CapturedRequest>, query: String): List<CapturedRequest> {
    if (query.isBlank()) return requests
    return try {
        com.ultra.trafficagent.analysis.FilterEngine.parse(query).filter(requests)
    } catch (_: IllegalArgumentException) {
        requests.filter { it.host.contains(query, true) || it.path.contains(query, true) }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    requests: List<CapturedRequest>,
    captureEnabled: Boolean,
    onToggleCapture: () -> Unit,
    onOpenRequest: (CapturedRequest) -> Unit,
    modifier: Modifier = Modifier,
) {
    var query by remember { mutableStateOf("") }
    var filter by remember { mutableStateOf(CaptureFilter.ALL) }

    val visible = filterWithQuery(requests, query).filter { req ->
        val matchesFilter = when (filter) {
            CaptureFilter.ALL -> true
            CaptureFilter.HTTP -> req.protocol == Protocol.HTTP1 || req.protocol == Protocol.HTTP2
            CaptureFilter.TLS -> req.protocol == Protocol.TLS
            CaptureFilter.WEBSOCKET -> req.protocol == Protocol.WEBSOCKET
            CaptureFilter.ERROR -> req.error != null || (req.status ?: 200) >= 500
        }
        matchesFilter
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Traffic Agent") },
                actions = {
                    AssistChip(
                        onClick = onToggleCapture,
                        label = { Text(if (captureEnabled) "Stop" else "Start") },
                        leadingIcon = {
                            Icon(Icons.Filled.PlayArrow, contentDescription = null)
                        },
                    )
                    Spacer(Modifier.width(12.dp))
                },
            )
        },
    ) { padding ->
        Column(Modifier.padding(padding).fillMaxSize()) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text("Filter: host:weibo status:4xx size>1024") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
            )
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                CaptureFilter.entries.forEach { f ->
                    FilterChip(
                        selected = filter == f,
                        onClick = { filter = f },
                        label = { Text(f.label) },
                    )
                }
            }
            Spacer(Modifier.height(8.dp))
            LazyColumn(
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(visible, key = { it.id }) { req ->
                    RequestRow(req = req, onClick = { onOpenRequest(req) })
                }
            }
        }
    }
}

@Composable
private fun RequestRow(req: CapturedRequest, onClick: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth().clickable(onClick = onClick)) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(
                req.method,
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onPrimary,
                modifier = Modifier
                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(6.dp))
                    .padding(horizontal = 8.dp, vertical = 4.dp),
            )
            Spacer(Modifier.width(10.dp))
            Column(Modifier.weight(1f)) {
                Text(
                    req.host,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    req.path,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            Spacer(Modifier.width(10.dp))
            Column(horizontalAlignment = Alignment.End) {
                StatusBadge(status = req.status)
                Spacer(Modifier.height(4.dp))
                Text(
                    "${formatBytes(req.totalSize)} · ${req.protocol.name}",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
fun StatusBadge(status: Int?) {
    val color = when (status) {
        null -> MaterialTheme.colorScheme.outline
        in 200..299 -> MaterialTheme.colorScheme.primary
        in 300..399 -> MaterialTheme.colorScheme.tertiary
        else -> MaterialTheme.colorScheme.error
    }
    Text(
        status?.toString() ?: "···",
        style = MaterialTheme.typography.labelMedium,
        color = color,
        fontFamily = FontFamily.Monospace,
    )
}

fun formatBytes(bytes: Long): String = when {
    bytes < 1024 -> "${bytes}B"
    bytes < 1024 * 1024 -> "%.1fKB".format(bytes / 1024.0)
    else -> "%.1fMB".format(bytes / (1024.0 * 1024.0))
}
