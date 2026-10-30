package com.ultra.trafficagent

import android.content.Intent
import android.content.pm.PackageManager
import android.net.VpnService
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.FileProvider
import com.ultra.trafficagent.session.CaptureState
import com.ultra.trafficagent.session.RuleStore
import com.ultra.trafficagent.ui.CaptureViewModel
import com.ultra.trafficagent.ui.DemoData
import com.ultra.trafficagent.ui.screens.AgentScreen
import com.ultra.trafficagent.ui.screens.CaptureScreen
import com.ultra.trafficagent.ui.screens.RequestDetailScreen
import com.ultra.trafficagent.ui.screens.RulesScreen
import com.ultra.trafficagent.ui.screens.SettingsScreen
import com.ultra.trafficagent.ui.theme.TrafficAgentTheme
import java.io.File

class MainActivity : ComponentActivity() {

    private val viewModel: CaptureViewModel by viewModels()

    private val vpnPermission =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == RESULT_OK) {
                viewModel.toggleCapture()
            }
        }

    private val notificationPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermission.launch(android.Manifest.permission.POST_NOTIFICATIONS)
        }
        setContent {
            TrafficAgentApp(viewModel) { intent -> vpnPermission.launch(intent) }
        }
    }
}

private data class Tab(val label: String, val icon: ImageVector)

private val tabs = listOf(
    Tab("Capture", Icons.Filled.Home),
    Tab("Rules", Icons.Filled.List),
    Tab("Agent", Icons.Filled.Lock),
    Tab("Settings", Icons.Filled.Settings),
)

@Composable
fun TrafficAgentApp(
    viewModel: CaptureViewModel,
    requestVpnPermission: (Intent) -> Unit,
) {
    var dynamicColor by rememberSaveable { mutableStateOf(true) }

    TrafficAgentTheme(dynamicColor = dynamicColor) {
        var selectedTab by rememberSaveable { mutableStateOf(0) }
        var selectedRequestId by rememberSaveable { mutableStateOf<Long?>(null) }
        val requests by viewModel.requests.collectAsState()
        val captureState by viewModel.state.collectAsState()
        val stats by viewModel.stats.collectAsState()
        val mitmEnabled by viewModel.mitmEnabled.collectAsState()
        val recordPcap by viewModel.recordPcap.collectAsState()
        val exportFile by viewModel.exportFile.collectAsState()
        val rules by RuleStore.rules.collectAsState()

        // First-run seed so the Rules screen demonstrates real, working
        // rewrites (block-ads / auth injection) once MITM is enabled.
        LaunchedEffect(Unit) { RuleStore.seed(DemoData.initialRules) }

        // Auto-share whenever an export lands.
        val context = LocalContext.current
        LaunchedEffect(exportFile) {
            exportFile?.let { file ->
                runCatching {
                    val uri = FileProvider.getUriForFile(
                        context, "${context.packageName}.fileprovider", file,
                    )
                    val send = Intent(Intent.ACTION_SEND).apply {
                        type = mimeOf(file)
                        putExtra(Intent.EXTRA_STREAM, uri)
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }
                    context.startActivity(Intent.createChooser(send, "Share ${file.name}"))
                }
                viewModel.consumeExport()
            }
        }

        Scaffold(
            bottomBar = {
                NavigationBar {
                    tabs.forEachIndexed { index, tab ->
                        NavigationBarItem(
                            selected = selectedTab == index,
                            onClick = {
                                selectedRequestId = null
                                selectedTab = index
                            },
                            icon = { Icon(tab.icon, contentDescription = tab.label) },
                            label = { Text(tab.label) },
                        )
                    }
                }
            },
        ) { innerPadding ->
            val modifier = Modifier.padding(innerPadding)
            val request = requests.firstOrNull { it.id == selectedRequestId }
            when {
                request != null -> RequestDetailScreen(
                    request = request,
                    onBack = { selectedRequestId = null },
                    modifier = modifier,
                )
                selectedTab == 0 -> CaptureScreen(
                    requests = requests,
                    captureState = captureState,
                    stats = stats,
                    onToggleCapture = {
                        val needsPermission = VpnService.prepare(context)
                        if (needsPermission != null) {
                            requestVpnPermission(needsPermission)
                        } else {
                            viewModel.toggleCapture()
                        }
                    },
                    onOpenRequest = { selectedRequestId = it.id },
                    onClear = viewModel::clearSession,
                    onExportHar = viewModel::exportHar,
                    onExportPostman = viewModel::exportPostman,
                    onExportCsv = viewModel::exportCsv,
                    onExportMarkdown = viewModel::exportMarkdown,
                    onExportPcap = viewModel::exportPcap,
                    pcapAvailable = stats?.pcapPath != null,
                    modifier = modifier,
                )
                selectedTab == 1 -> RulesScreen(
                    rules = rules,
                    onToggleRule = { id ->
                        val rule = rules.firstOrNull { it.id == id }
                        if (rule != null) RuleStore.toggle(id, !rule.enabled)
                    },
                    onDeleteRule = { id -> RuleStore.remove(id) },
                    onAddRule = { rule -> RuleStore.add(rule) },
                    modifier = modifier,
                )
                selectedTab == 2 -> AgentScreen(modifier = modifier)
                else -> SettingsScreen(
                    dynamicColor = dynamicColor,
                    onDynamicColorChange = { dynamicColor = it },
                    mitmEnabled = mitmEnabled,
                    onMitmChange = { viewModel.mitmEnabled.value = it },
                    recordPcap = recordPcap,
                    onRecordPcapChange = { viewModel.recordPcap.value = it },
                    onExportCa = viewModel::exportCaCertificate,
                    modifier = modifier,
                )
            }
        }
    }
}

private fun mimeOf(file: File): String = when {
    file.name.endsWith(".har") -> "application/json"
    file.name.endsWith(".json") -> "application/json"
    file.name.endsWith(".csv") -> "text/csv"
    file.name.endsWith(".md") -> "text/markdown"
    file.name.endsWith(".pem") -> "application/x-pem-file"
    file.name.endsWith(".pcap") -> "application/vnd.tcpdump.pcap"
    else -> "application/octet-stream"
}
