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
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
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
import com.ultra.trafficagent.session.CaptureState
import com.ultra.trafficagent.session.LiveStats

private enum class CaptureFilter(val label: String) {
    ALL("All"), HTTP("HTTP"), TLS("TLS"), WEBSOCKET("WS"), ERROR("Error");
}

/**
 * Parses the inline query with a local subset of the core filter DSL:
 * "host:weibo status:4xx size>1024 time>500 error:true". Malformed input
 * falls back to plain keyword search so typing never blocks the list.
 */
private fun filterWithQuery(requests: List<CapturedRequest>, query: String): List<CapturedRequest> {
    if (query.isBlank()) return requests
    var hostKeyword: String? = null
    var pathKeyword: String? = null
    var bodyKeyword: String? = null
    val methods = mutableSetOf<String>()
    val statusClasses = mutableSetOf<Int>()
    val exactStatus = mutableSetOf<Int>()
    var minBytes: Long? = null
    var maxBytes: Long? = null
    var minTime: Long? = null
    var maxTime: Long? = null
    var errorOnly = false
    var bareWord: String? = null
    var ok = true
    for (token in query.trim().split(Regex("\\s+")).filter { it.isNotEmpty() }) {
        val lower = token.lowercase()
        try {
            when {
                lower.startsWith("host:") -> hostKeyword = token.substring(5)
                lower.startsWith("path:") -> pathKeyword = token.substring(5)
                lower.startsWith("body:") -> bodyKeyword = token.substring(5)
                lower.startsWith("method:") -> methods += token.substring(7).uppercase().split(',')
                lower.startsWith("status:") -> token.substring(7).split(',').forEach { part ->
                    val p = part.trim()
                    if (p.endsWith("xx", true)) statusClasses += p.dropLast(2).toInt()
                    else exactStatus += p.toInt()
                }
                lower.startsWith("size>") -> minBytes = token.substring(5).toLong()
                lower.startsWith("size<") -> maxBytes = token.substring(5).toLong()
                lower.startsWith("time>") -> minTime = token.substring(5).toLong()
                lower.startsWith("time<") -> maxTime = token.substring(5).toLong()
                lower.startsWith("error:") && token.substring(6).equals("true", true) -> errorOnly = true
                !token.contains(':') -> bareWord = token
                else -> {}
            }
        } catch (_: NumberFormatException) {
            ok = false
        }
    }
    if (!ok || (hostKeyword == null && pathKeyword == null && bodyKeyword == null && methods.isEmpty() &&
            statusClasses.isEmpty() && exactStatus.isEmpty() && minBytes == null && maxBytes == null &&
            minTime == null && maxTime == null && !errorOnly && bareWord == null)
    ) {
        return requests.filter {
            it.host.contains(query, true) || it.path.contains(query, true)
        }
    }
    val host = hostKeyword ?: bareWord
    return requests.filter { req ->
        (host == null || req.host.contains(host, true)) &&
            (pathKeyword == null || req.path.contains(pathKeyword, true)) &&
            (bodyKeyword == null || req.responseBody.contains(bodyKeyword, true)) &&
            (methods.isEmpty() || req.method.uppercase() in methods) &&
            (statusClasses.isEmpty() || req.status?.div(100) in statusClasses) &&
            (exactStatus.isEmpty() || req.status in exactStatus) &&
            (minBytes == null || req.totalSize >= minBytes) &&
            (maxBytes == null || req.totalSize <= maxBytes) &&
            (minTime == null || (req.durationMs ?: 0) >= minTime) &&
            (maxTime == null || (req.durationMs ?: 0) <= maxTime) &&
            (!errorOnly || req.error != null || (req.status ?: 200) >= 500)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    requests: List<CapturedRequest>,
    captureState: CaptureState,
    stats: LiveStats? = null,
    onToggleCapture: () -> Unit,
    onOpenRequest: (CapturedRequest) -> Unit,
    onClear: () -> Unit = {},
    onExportHar: () -> Unit = {},
    onExportPostman: () -> Unit = {},
    onExportCsv: () -> Unit = {},
    onExportMarkdown: () -> Unit = {},
    onExportPcap: () -> Unit = {},
    onImportFile: () -> Unit = {},
    importMessage: String? = null,
    pcapAvailable: Boolean = false,
    modifier: Modifier = Modifier,
) {
    var query by remember { mutableStateOf("") }
    var filter by remember { mutableStateOf(CaptureFilter.ALL) }
    var menuOpen by remember { mutableStateOf(false) }
    val capturing = captureState == CaptureState.ACTIVE || captureState == CaptureState.PREPARING

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
                        label = { Text(if (capturing) "Stop" else "Start") },
                        leadingIcon = {
                            Icon(
                                if (capturing) Icons.Filled.Close else Icons.Filled.PlayArrow,
                                contentDescription = null,
                            )
                        },
                    )
                    IconButton(onClick = { menuOpen = true }) {
                        Icon(Icons.Filled.MoreVert, contentDescription = "More")
                    }
                    DropdownMenu(expanded = menuOpen, onDismissRequest = { menuOpen = false }) {
                        DropdownMenuItem(
                            text = { Text("Export HAR") },
                            onClick = {
                                menuOpen = false
                                onExportHar()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Export Postman collection") },
                            onClick = {
                                menuOpen = false
                                onExportPostman()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Export CSV") },
                            onClick = {
                                menuOpen = false
                                onExportCsv()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Export Markdown") },
                            onClick = {
                                menuOpen = false
                                onExportMarkdown()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Share PCAP recording") },
                            enabled = pcapAvailable,
                            onClick = {
                                menuOpen = false
                                onExportPcap()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Import pcap/pcapng…") },
                            onClick = {
                                menuOpen = false
                                onImportFile()
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("Clear session") },
                            leadingIcon = { Icon(Icons.Filled.Delete, contentDescription = null) },
                            onClick = {
                                menuOpen = false
                                onClear()
                            },
                        )
                    }
                    Spacer(Modifier.width(8.dp))
                },
            )
        },
    ) { padding ->
        Column(Modifier.padding(padding).fillMaxSize()) {
            if (capturing) {
                CaptureBanner(stats)
            }
            if (importMessage != null) {
                Text(
                    importMessage,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.tertiary,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                )
            }
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
            if (visible.isEmpty()) {
                EmptyCaptureHint(capturing = capturing, requests = requests)
            } else {
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
}

@Composable
private fun EmptyCaptureHint(capturing: Boolean, requests: List<CapturedRequest>) {
    Column(
        Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text(
            if (requests.isEmpty()) "No captures yet" else "No matches for this filter",
            style = MaterialTheme.typography.titleLarge,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            if (requests.isEmpty()) {
                if (capturing) "Traffic will appear here as apps talk to the network." else
                    "Tap Start to begin capturing — enable HTTPS decryption in Settings for TLS bodies."
            } else {
                "Try clearing the filter chips or the query."
            },
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun CaptureBanner(stats: LiveStats?) {
    if (stats == null) {
        LinearProgressIndicator(Modifier.fillMaxWidth())
        return
    }
    Card(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                buildString {
                    append(stats.requests)
                    append(" requests · ↑")
                    append(formatBytes(stats.bytesUp))
                    append(" · ↓")
                    append(formatBytes(stats.bytesDown))
                },
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                buildString {
                    append(stats.flowsActive)
                    append(" live flows · ")
                    append(stats.packetsFromTun)
                    append(" pkts in / ")
                    append(stats.packetsToTun)
                    append(" out")
                    if (stats.mitmEnabled) append(" · HTTPS decrypted")
                    if (stats.recordingPcap) append(" · PCAP on")
                },
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
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
