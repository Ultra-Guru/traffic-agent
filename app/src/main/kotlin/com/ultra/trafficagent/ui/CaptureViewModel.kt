package com.ultra.trafficagent.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.exports.CsvExporter
import com.ultra.trafficagent.exports.HarExporter
import com.ultra.trafficagent.exports.MarkdownExporter
import com.ultra.trafficagent.exports.PostmanExporter
import com.ultra.trafficagent.session.CaptureSession
import com.ultra.trafficagent.session.CaptureState
import com.ultra.trafficagent.session.LiveStats
import com.ultra.trafficagent.vpn.CaManager
import com.ultra.trafficagent.vpn.TrafficVpnService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

/**
 * Live capture UI state: mirrors [CaptureSession] flows, drives the VPN
 * service start/stop intents and materializes exports into shareable files.
 */
class CaptureViewModel(app: Application) : AndroidViewModel(app) {

    val requests: StateFlow<List<CapturedRequest>> = CaptureSession.requests
    val state: StateFlow<CaptureState> = CaptureSession.state
    val stats: StateFlow<LiveStats> = CaptureSession.stats

    /** User toggles applied on the next capture session. */
    val mitmEnabled = MutableStateFlow(false)
    val recordPcap = MutableStateFlow(false)

    /** Latest export file ready to share (filename under filesDir/exports). */
    val exportFile = MutableStateFlow<File?>(null)

    fun toggleCapture() {
        when (state.value) {
            CaptureState.ACTIVE, CaptureState.PREPARING ->
                TrafficVpnService.stop(getApplication())
            else -> TrafficVpnService.start(getApplication(), mitmEnabled.value, recordPcap.value)
        }
    }

    fun clearSession() = CaptureSession.clear()

    fun exportCaCertificate() {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { CaManager.exportPem(getApplication<Application>().filesDir) }
                .onSuccess { exportFile.value = it }
        }
    }

    fun exportHar() = export("capture.har") { HarExporter.export(CaptureSession.requests.value) }

    fun exportPostman() = export(
        "capture.postman_collection.json",
    ) { PostmanExporter.toPostmanCollection(CaptureSession.requests.value) }

    fun exportCsv() = export("capture.csv") { CsvExporter.export(CaptureSession.requests.value) }

    fun exportMarkdown() = export("capture.md") { MarkdownExporter.export(CaptureSession.requests.value) }

    /** Copies the last PCAP recording into exports/ and shares it. */
    fun exportPcap() {
        viewModelScope.launch(Dispatchers.IO) {
            val path = CaptureSession.stats.value.pcapPath ?: return@launch
            runCatching {
                val source = File(path)
                val dir = File(getApplication<Application>().filesDir, "exports").apply { mkdirs() }
                File(dir, source.name).apply { source.copyTo(this, overwrite = true) }
            }.onSuccess { exportFile.value = it }
        }
    }

    private fun export(name: String, render: () -> String) {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val dir = File(getApplication<Application>().filesDir, "exports").apply { mkdirs() }
                File(dir, name).apply { writeText(render()) }
            }.onSuccess { exportFile.value = it }
        }
    }

    fun consumeExport() {
        exportFile.value = null
    }
}
