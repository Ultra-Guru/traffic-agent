package com.ultra.trafficagent.capture

/**
 * One protocol-detection event drained from the analysis engine, parsed
 * from the "kind\ttsMs\tsrc\tdst\ttext\tnumeric" line format emitted by
 * native-engine/src/export_lines.cpp.
 */
data class TapEvent(
    val kind: String,
    val timestampMs: Long,
    val src: String,
    val dst: String,
    val text: String,
    val numeric: Int,
) {
    companion object {
        /** Parses one line; null when malformed. */
        fun parse(line: String): TapEvent? {
            val parts = line.split('\t')
            if (parts.size != 6) return null
            val ts = parts[1].toLongOrNull() ?: return null
            val numeric = parts[5].toIntOrNull() ?: return null
            return TapEvent(parts[0], ts, parts[2], parts[3], parts[4], numeric)
        }
    }
}

/**
 * Passive analysis tap beside the forwarding stack (VPN 双通道捕获):
 * every TUN packet is fed to a native Engine purely for observation, and
 * periodic [drain]s surface protocol events (SNI / JA3 / DNS / HTTP/2
 * headers) plus completed plain-HTTP exchanges as [CapturedRequest]s.
 *
 * The native calls are injected so the parsing/merge logic stays
 * unit-testable without the .so.
 */
class VpnAnalysisTap(
    private val feedPacket: (packet: ByteArray, timestampMs: Long) -> Int,
    private val takeEvents: () -> Array<String>?,
    private val takeExchanges: () -> Array<String>?,
) {
    data class TapResult(
        val events: List<TapEvent>,
        val exchanges: List<CapturedRequest>,
    )

    /** Feeds one raw TUN packet into the analysis engine (never throws). */
    fun feed(packet: ByteArray, timestampMs: Long) {
        try {
            feedPacket(packet, timestampMs)
        } catch (_: Exception) {
        }
    }

    /** Drains everything accumulated since the last call. */
    fun drain(): TapResult {
        val events = try {
            (takeEvents() ?: emptyArray()).mapNotNull { TapEvent.parse(it) }
        } catch (_: Exception) {
            emptyList()
        }
        val exchanges = try {
            (takeExchanges() ?: emptyArray()).mapNotNull { SessionCodec.decode(it) }
        } catch (_: Exception) {
            emptyList()
        }
        return TapResult(events, exchanges)
    }

    companion object {
        /** Wires the tap to a live native Engine handle. */
        fun fromEngineHandle(handle: Long) = VpnAnalysisTap(
            feedPacket = { packet, ts -> NativeEngine.nativeFeedPacket(handle, packet, ts) },
            takeEvents = { NativeEngine.nativeTakeEvents(handle) },
            takeExchanges = { NativeEngine.nativeTakeExchanges(handle) },
        )
    }
}
