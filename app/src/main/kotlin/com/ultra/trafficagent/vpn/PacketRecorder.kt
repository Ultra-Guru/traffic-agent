package com.ultra.trafficagent.vpn

import com.ultra.trafficagent.capture.PcapNgSessionFile
import com.ultra.trafficagent.capture.PcapSessionFile

/**
 * Format-agnostic packet sink for capture recording: the service records
 * TUN packets through this interface and picks the concrete file format
 * (classic pcap or pcapng) from user settings.
 */
interface PacketRecorder : AutoCloseable {
    fun start(): Boolean
    fun record(packet: ByteArray, timestampMs: Long)
    fun flush()
    fun packetsWritten(): Long
    val path: String
}

/** Classic libpcap dump (24-byte header + per-packet records). */
class ClassicPcapRecorder(
    private val file: PcapSessionFile,
    override val path: String,
) : PacketRecorder {
    override fun start(): Boolean = file.start()
    override fun record(packet: ByteArray, timestampMs: Long) = file.record(packet, timestampMs)
    override fun flush() = file.flush()
    override fun packetsWritten(): Long = file.packetsWritten
    override fun close() = file.close()
}

/** Modern block-based pcapng dump (SHB/IDB/EPB, microsecond tsresol). */
class PcapNgRecorder(
    private val file: PcapNgSessionFile,
    override val path: String,
) : PacketRecorder {
    override fun start(): Boolean = file.start()
    override fun record(packet: ByteArray, timestampMs: Long) = file.record(packet, timestampMs)
    override fun flush() = file.flush()
    override fun packetsWritten(): Long = file.packetsWritten
    override fun close() = file.close()
}
