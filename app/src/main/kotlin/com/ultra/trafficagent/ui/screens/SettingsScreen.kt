package com.ultra.trafficagent.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.ultra.trafficagent.capture.CaptureMode
import com.ultra.trafficagent.capture.RootCommandBuilder
import com.ultra.trafficagent.vpn.CaManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.security.MessageDigest

private val captureModes = listOf(
    CaptureMode.VPN to "VPN (tun)",
    CaptureMode.ROOT_IPTABLES to "Root · iptables",
    CaptureMode.ROOT_PCAP_FILE to "Root · pcap",
)

/** Lazy CA info for the settings card (null until loaded off the main thread). */
private data class CaInfo(
    val subject: String,
    val validTo: String,
    val sha256Short: String,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    dynamicColor: Boolean,
    onDynamicColorChange: (Boolean) -> Unit,
    mitmEnabled: Boolean,
    onMitmChange: (Boolean) -> Unit,
    recordPcap: Boolean,
    onRecordPcapChange: (Boolean) -> Unit,
    pcapngFormat: Boolean,
    onPcapngFormatChange: (Boolean) -> Unit,
    onExportCa: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var selectedMode by remember { mutableStateOf(CaptureMode.VPN) }
    var caInfo by remember { mutableStateOf<CaInfo?>(null) }
    val context = LocalContext.current

    Scaffold(
        modifier = modifier,
        topBar = { TopAppBar(title = { Text("Settings") }) },
    ) { padding ->
        Column(
            Modifier
                .padding(padding)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            SectionCard("Capture mode") {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    captureModes.forEach { (mode, label) ->
                        FilterChip(
                            selected = selectedMode == mode,
                            onClick = { selectedMode = mode },
                            label = { Text(label) },
                        )
                    }
                }
                Spacer(Modifier.height(8.dp))
                Text(
                    when (selectedMode) {
                        CaptureMode.VPN -> "VpnService TUN fd feeds the native engine directly. No root needed."
                        CaptureMode.ROOT_IPTABLES -> RootCommandBuilder.redirectTcpToPort(8188)
                        CaptureMode.ROOT_PCAP_FILE -> RootCommandBuilder.tcpdumpToFile("/sdcard/capture.pcap")
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    fontFamily = FontFamily.Monospace,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            SectionCard("HTTPS decryption (MITM)") {
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Column {
                        Text("Decrypt HTTPS traffic", style = MaterialTheme.typography.bodyLarge)
                        Text(
                            "Transparent TLS termination with SNI-driven leaf\n" +
                                "certificates. Applied on the next capture session.",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    Switch(checked = mitmEnabled, onCheckedChange = onMitmChange)
                }
            }

            SectionCard("CA certificate") {
                LaunchedEffect(Unit) {
                    if (caInfo == null) {
                        caInfo = withContext(Dispatchers.IO) {
                            runCatching { loadCaInfo(context.filesDir) }.getOrNull()
                        }
                    }
                }
                val info = caInfo
                if (info != null) {
                    Text(info.subject, style = MaterialTheme.typography.bodyMedium)
                    Text(
                        "Valid until ${info.validTo}",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(
                        "SHA-256: ${info.sha256Short}…",
                        style = MaterialTheme.typography.labelMedium,
                        fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    Text(
                        "The CA is generated on first capture with decryption on.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Spacer(Modifier.height(4.dp))
                OutlinedButton(onClick = onExportCa) {
                    Text("Export certificate (.pem)")
                }
                Spacer(Modifier.height(4.dp))
                Text(
                    "Install: share the .pem, open it, then Settings → Security → " +
                        "Encrypt & credential storage → Install a certificate → CA certificate. " +
                        "Apps targeting API 24+ additionally require the certificate in the " +
                        "system store (root) to trust it inside their own traffic.",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            SectionCard("PCAP recording") {
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Column {
                        Text("Record raw packets", style = MaterialTheme.typography.bodyLarge)
                        Text(
                            "Every TUN packet is written via the native writer —\n" +
                                "open the file in Wireshark/tcpdump.",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    Switch(checked = recordPcap, onCheckedChange = onRecordPcapChange)
                }
                Spacer(Modifier.height(8.dp))
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Column {
                        Text("pcapng format", style = MaterialTheme.typography.bodyLarge)
                        Text(
                            "Modern block format: microsecond timestamps and\n" +
                                "per-interface options. Files end in .pcapng.",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    Switch(
                        checked = pcapngFormat,
                        onCheckedChange = onPcapngFormatChange,
                        enabled = recordPcap,
                    )
                }
            }

            SectionCard("Appearance") {
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Column {
                        Text("Dynamic color", style = MaterialTheme.typography.bodyLarge)
                        Text(
                            "Material You palette on Android 12+",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    Switch(checked = dynamicColor, onCheckedChange = onDynamicColorChange)
                }
            }

            SectionCard("About") {
                Text("Traffic Agent 0.4.0", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(4.dp))
                Text(
                    "Kotlin + C++ + Python on-device traffic agent.\n" +
                        "Modules: core-capture · core-analysis · core-transform · core-agent · core-exports · core-mitm · native-engine\n" +
                        "github.com/Ultra-Guru/traffic-agent",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

private fun loadCaInfo(filesDir: java.io.File): CaInfo {
    val ca = CaManager.loadOrCreate(filesDir)
    val cert = ca.caCertificate()
    val sha256 = MessageDigest.getInstance("SHA-256")
        .digest(cert.encoded)
        .joinToString("") { "%02x".format(it) }
    return CaInfo(
        subject = cert.subjectX500Principal.name,
        validTo = cert.notAfter.toString(),
        sha256Short = sha256.take(16),
    )
}

@Composable
private fun SectionCard(title: String, content: @Composable () -> Unit) {
    Card {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            content()
        }
    }
}
