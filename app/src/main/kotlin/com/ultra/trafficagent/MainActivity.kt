package com.ultra.trafficagent

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import com.ultra.trafficagent.ui.DemoData
import com.ultra.trafficagent.ui.screens.AgentScreen
import com.ultra.trafficagent.ui.screens.CaptureScreen
import com.ultra.trafficagent.ui.screens.RequestDetailScreen
import com.ultra.trafficagent.ui.screens.RulesScreen
import com.ultra.trafficagent.ui.screens.SettingsScreen
import com.ultra.trafficagent.ui.theme.TrafficAgentTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TrafficAgentApp()
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
fun TrafficAgentApp() {
    var dynamicColor by rememberSaveable { mutableStateOf(true) }

    TrafficAgentTheme(dynamicColor = dynamicColor) {
        var selectedTab by rememberSaveable { mutableStateOf(0) }
        var selectedRequestId by rememberSaveable { mutableStateOf<Long?>(null) }
        var rules by remember { mutableStateOf(DemoData.initialRules) }
        var captureEnabled by rememberSaveable { mutableStateOf(false) }

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
            val request = DemoData.requests.firstOrNull { it.id == selectedRequestId }
            when {
                request != null -> RequestDetailScreen(
                    request = request,
                    onBack = { selectedRequestId = null },
                    modifier = modifier,
                )
                selectedTab == 0 -> CaptureScreen(
                    requests = DemoData.requests,
                    captureEnabled = captureEnabled,
                    onToggleCapture = { captureEnabled = !captureEnabled },
                    onOpenRequest = { selectedRequestId = it.id },
                    modifier = modifier,
                )
                selectedTab == 1 -> RulesScreen(
                    rules = rules,
                    onToggleRule = { id ->
                        rules = rules.map { if (it.id == id) it.copy(enabled = !it.enabled) else it }
                    },
                    onDeleteRule = { id -> rules = rules.filterNot { it.id == id } },
                    onAddRule = { rule -> rules = rules + rule },
                    modifier = modifier,
                )
                selectedTab == 2 -> AgentScreen(modifier = modifier)
                else -> SettingsScreen(
                    dynamicColor = dynamicColor,
                    onDynamicColorChange = { dynamicColor = it },
                    modifier = modifier,
                )
            }
        }
    }
}
