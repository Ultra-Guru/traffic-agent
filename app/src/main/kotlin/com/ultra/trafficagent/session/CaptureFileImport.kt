package com.ultra.trafficagent.session

import com.ultra.trafficagent.capture.NativeEngine
import com.ultra.trafficagent.capture.PcapFileReader
import com.ultra.trafficagent.capture.PcapFormatException
import com.ultra.trafficagent.capture.PcapNgFileReader
import com.ultra.trafficagent.capture.VpnAnalysisTap

/**
 * Capture-file import ("导入分析"): takes a classic pcap or pcapng file and
 * replays every raw IPv4 packet through a fresh native engine instance,
 * draining the reassembled exchanges into the live session list — the same
 * analysis path the VPN data plane uses, just offline.
 */
object CaptureFileImport {

    data class Result(
        val packets: Int,
        val requests: Int,
        val error: String? = null,
    )

    /** Extracts (timestampMs, raw-IPv4-packet) pairs from either format. */
    fun rawIpPackets(bytes: ByteArray): List<Pair<Long, ByteArray>> {
        return if (PcapNgFileReader.looksLikePcapNg(bytes)) {
            val reader = PcapNgFileReader(bytes)
            val link = reader.interfaces().firstOrNull()?.linkType ?: 101
            reader.packets().mapNotNull { (tsNs, data) ->
                val ip = when {
                    link == 101 -> data
                    link == 1 && data.size >= 14 &&
                        data[12] == 0x08.toByte() && data[13] == 0x00.toByte() ->
                        data.copyOfRange(14, data.size)
                    else -> null
                } ?: return@mapNotNull null
                (tsNs / 1_000_000) to ip
            }
        } else {
            val reader = PcapFileReader(bytes)
            val link = reader.pcapHeader().linkType
            reader.records().mapNotNull { rec ->
                val ip = when {
                    link == 101 -> rec.data
                    link == 1 && rec.data.size >= 14 &&
                        rec.data[12] == 0x08.toByte() && rec.data[13] == 0x00.toByte() ->
                        rec.data.copyOfRange(14, rec.data.size)
                    else -> null
                } ?: return@mapNotNull null
                (rec.timestampSec * 1000 + rec.timestampUsec / 1000) to ip
            }
        }
    }

    /**
     * Runs the import: feeds all packets through a dedicated engine handle
     * and returns the drained exchanges (ids already re-assigned via
     * [CaptureSession.nextId]). Callers own the threading (use a worker).
     */
    fun import(bytes: ByteArray): Result {
        val packets = try {
            rawIpPackets(bytes)
        } catch (e: PcapFormatException) {
            return Result(0, 0, "Not a pcap/pcapng file: ${e.message}")
        } catch (e: Exception) {
            return Result(0, 0, "Read failed: ${e.message ?: e.javaClass.simpleName}")
        }
        if (packets.isEmpty()) {
            return Result(0, 0, "No IPv4 packets found in file")
        }

        val handle = try {
            NativeEngine.nativeInit()
        } catch (e: UnsatisfiedLinkError) {
            return Result(0, 0, "Native engine unavailable: ${e.message}")
        } catch (e: Exception) {
            return Result(0, 0, "Engine init failed: ${e.message}")
        }

        val tap = VpnAnalysisTap.fromEngineHandle(handle)
        var requests = 0
        try {
            for ((tsMs, packet) in packets) {
                tap.feed(packet, tsMs)
            }
            val drained = tap.drain()
            CaptureSession.publishEvents(drained.events)
            for (exchange in drained.exchanges) {
                CaptureSession.add(exchange.copy(id = CaptureSession.nextId()))
                requests++
            }
        } finally {
            runCatching { NativeEngine.nativeDestroy(handle) }
        }
        return Result(packets.size, requests)
    }
}
