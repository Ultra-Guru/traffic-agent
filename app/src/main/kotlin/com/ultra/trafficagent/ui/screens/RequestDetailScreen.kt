package com.ultra.trafficagent.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.exports.CurlExporter
import com.ultra.trafficagent.exports.HarExporter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RequestDetailScreen(
    request: CapturedRequest,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var tab by remember { mutableIntStateOf(0) }
    val clipboard = LocalClipboardManager.current
    val curl = remember(request.id) { CurlExporter.toCurl(request) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text(request.host, maxLines = 1) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    FilterChip(
                        selected = false,
                        onClick = { clipboard.setText(AnnotatedString(curl)) },
                        label = { Text("Copy cURL") },
                    )
                    Spacer(Modifier.width(8.dp))
                },
            )
        },
    ) { padding ->
        Column(Modifier.padding(padding).fillMaxSize().verticalScroll(rememberScrollState())) {
            TabRow(selectedTabIndex = tab) {
                Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("Overview") })
                Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("Headers") })
                Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("Body") })
            }
            when (tab) {
                0 -> OverviewPane(request, curl)
                1 -> HeadersPane(request)
                else -> BodyPane(request)
            }
        }
    }
}

@Composable
private fun OverviewPane(request: CapturedRequest, curl: String) {
    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        DetailRow("Method", request.method)
        DetailRow("URL", "https://${request.host}${request.path}")
        DetailRow("Status", request.status?.toString() ?: "pending")
        DetailRow("Protocol", request.protocol.name)
        DetailRow("Request size", formatBytes(request.bytesUp))
        DetailRow("Response size", formatBytes(request.bytesDown))
        DetailRow("App UID", request.appUid?.toString() ?: "-")

        Spacer(Modifier.height(4.dp))
        Text("cURL", style = MaterialTheme.typography.titleMedium)
        Card {
            Text(
                curl,
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.fillMaxWidth().padding(12.dp),
            )
        }
    }
}

@Composable
private fun HeadersPane(request: CapturedRequest) {
    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Request headers", style = MaterialTheme.typography.titleMedium)
        if (request.requestHeaders.isEmpty()) {
            EmptyHint()
        } else {
            Card {
                Column(Modifier.padding(12.dp)) {
                    request.requestHeaders.forEach { (k, v) -> DetailRow(k, v) }
                }
            }
        }
        Text("Response headers", style = MaterialTheme.typography.titleMedium)
        if (request.responseHeaders.isEmpty()) {
            EmptyHint()
        } else {
            Card {
                Column(Modifier.padding(12.dp)) {
                    request.responseHeaders.forEach { (k, v) -> DetailRow(k, v) }
                }
            }
        }
    }
}

@Composable
private fun BodyPane(request: CapturedRequest) {
    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Request body", style = MaterialTheme.typography.titleMedium)
        BodyCard(request.requestBody)
        Text("Response body", style = MaterialTheme.typography.titleMedium)
        BodyCard(request.responseBody)
        Text("HAR entry (excerpt)", style = MaterialTheme.typography.titleMedium)
        Card {
            Text(
                HarExporter.entry(request).take(600) + "…",
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.fillMaxWidth().padding(12.dp),
            )
        }
    }
}

@Composable
private fun BodyCard(body: String) {
    if (body.isEmpty()) {
        EmptyHint()
    } else {
        Card {
            Text(
                body,
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.fillMaxWidth().padding(12.dp),
            )
        }
    }
}

@Composable
private fun EmptyHint() {
    Text(
        "(empty)",
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            fontFamily = FontFamily.Monospace,
            modifier = Modifier.padding(start = 16.dp),
        )
    }
}
