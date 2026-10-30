package com.ultra.trafficagent.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.exports.CsvExporter
import com.ultra.trafficagent.exports.HarExporter
import com.ultra.trafficagent.exports.MarkdownExporter
import com.ultra.trafficagent.exports.PostmanExporter
import com.ultra.trafficagent.session.CaptureFileImport
import com.ultra.trafficagent.session.CaptureSession
import com.ultra.trafficagent.session.CaptureState
import com.ultra.trafficagent.session.LiveStats
import com.ultra.trafficagent.session.RuleStore
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

    /** Record as pcapng instead of classic pcap. */
    val pcapngFormat = MutableStateFlow(false)

    /** Latest import outcome (null until the first import finishes). */
    val lastImport = MutableStateFlow<CaptureFileImport.Result?>(null)

    /** Latest export file ready to share (filename under filesDir/exports). */
    val exportFile = MutableStateFlow<File?>(null)

    fun toggleCapture() {
        when (state.value) {
            CaptureState.ACTIVE, CaptureState.PREPARING ->
                TrafficVpnService.stop(getApplication())
            else -> TrafficVpnService.start(
                getApplication(),
                mitmEnabled.value,
                recordPcap.value,
                pcapngFormat.value,
            )
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

    /** Imports a pcap/pcapng capture file into the live session list. */
    fun importCaptureFile(bytes: ByteArray) {
        viewModelScope.launch(Dispatchers.IO) {
            lastImport.value = CaptureFileImport.import(bytes)
        }
    }

    /** Content-uri variant of [importCaptureFile]; reads on a worker. */
    fun importCaptureFile(uri: android.net.Uri) {
        viewModelScope.launch(Dispatchers.IO) {
            lastImport.value = try {
                val bytes = getApplication<Application>().contentResolver
                    .openInputStream(uri)?.use { it.readBytes() }
                if (bytes == null) {
                    CaptureFileImport.Result(0, 0, "Could not read the selected file")
                } else {
                    CaptureFileImport.import(bytes)
                }
            } catch (e: Exception) {
                CaptureFileImport.Result(0, 0, "Read failed: ${e.message ?: e.javaClass.simpleName}")
            }
        }
    }

    /** Writes the current rule set to exports/rules.tarule.json and shares it. */
    fun exportRulepack() {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val dir = File(getApplication<Application>().filesDir, "exports").apply { mkdirs() }
                File(dir, "rules.tarule.json").apply { writeText(RuleStore.exportRulepack()) }
            }.onSuccess { exportFile.value = it }
        }
    }

    /** Installs a rulepack picked via SAF. */
    fun importRulepack(uri: android.net.Uri) {
        viewModelScope.launch(Dispatchers.IO) {
            lastImport.value = try {
                val text = getApplication<Application>().contentResolver
                    .openInputStream(uri)?.use { it.readBytes().toString(Charsets.UTF_8) }
                when {
                    text == null -> CaptureFileImport.Result(0, 0, "Could not read the rulepack")
                    else -> {
                        val error = RuleStore.importRulepack(text)
                        CaptureFileImport.Result(0, 0, error ?: "Rulepack imported")
                    }
                }
            } catch (e: Exception) {
                CaptureFileImport.Result(0, 0, "Read failed: ${e.message ?: e.javaClass.simpleName}")
            }
        }
    }
}
