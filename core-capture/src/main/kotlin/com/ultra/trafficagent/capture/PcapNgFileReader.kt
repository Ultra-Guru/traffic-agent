package com.ultra.trafficagent.capture

/**
 * Pure-Kotlin pcapng reader for the capture-file import flow ("导入分析"):
 * walks Section Header / Interface Description / Enhanced Packet / Simple
 * Packet blocks, honours the per-interface `if_tsresol` (both the decimal
 * and the 2^n encoding) and both byte orders, and lifts the packet payloads
 * out as IPv4 datagrams ready to be replayed through the native engine.
 *
 * Only what the import path needs is parsed; ISB/NRB/custom blocks are
 * skipped by length, exactly like the C++ reader.
 */
class PcapNgFileReader(private val bytes: ByteArray) {

    companion object {
        private const val BLOCK_SHB = 0x0A0D0D0AL
        private const val BLOCK_IDB = 0x00000001L
        private const val BLOCK_EPB = 0x00000006L
        private const val BLOCK_SPB = 0x00000003L
        private const val BYTE_ORDER_MAGIC = 0x1A2B3C4DL
        /** The same magic seen through the other endianness. */
        private const val BYTE_ORDER_MAGIC_SWAPPED = 0x4D3C2B1AL
        private const val OPT_IF_TSRESOL = 9

        /** True when [bytes] starts with a pcapng Section Header Block. */
        fun looksLikePcapNg(bytes: ByteArray): Boolean {
            if (bytes.size < 12) return false
            // SHB: block type (4) + total length (4) + byte-order magic (4).
            val le = (bytes[11].toLong() and 0xFF) or ((bytes[10].toLong() and 0xFF) shl 8) or
                ((bytes[9].toLong() and 0xFF) shl 16) or ((bytes[8].toLong() and 0xFF) shl 24)
            val be = (bytes[8].toLong() and 0xFF) or ((bytes[9].toLong() and 0xFF) shl 8) or
                ((bytes[10].toLong() and 0xFF) shl 16) or ((bytes[11].toLong() and 0xFF) shl 24)
            return le == BYTE_ORDER_MAGIC || be == BYTE_ORDER_MAGIC
        }
    }

    /** One imported packet: link-layer payload + its timestamp. */
    data class NgPacket(
        val timestampNs: Long,
        val data: ByteArray,
    )

    data class Interface(
        val linkType: Int,
        val snaplen: Long,
        /** Nanoseconds per timestamp unit (derived from if_tsresol). */
        val unitNanos: Long,
    )

    private var bigEndian = false
    private val interfaces = mutableListOf<Interface>()
    private val packets = mutableListOf<NgPacket>()
    private var parsed = false

    private fun u16(pos: Int): Int {
        val v = if (bigEndian) {
            ((bytes[pos].toInt() and 0xFF) shl 8) or (bytes[pos + 1].toInt() and 0xFF)
        } else {
            ((bytes[pos + 1].toInt() and 0xFF) shl 8) or (bytes[pos].toInt() and 0xFF)
        }
        return v
    }

    private fun u32(pos: Int): Long {
        var v = 0L
        if (bigEndian) {
            for (i in 0 until 4) v = (v shl 8) or (bytes[pos + i].toLong() and 0xFF)
        } else {
            for (i in 3 downTo 0) v = (v shl 8) or (bytes[pos + i].toLong() and 0xFF)
        }
        return v
    }

    private fun parseOnce() {
        if (parsed) return
        parsed = true
        // The SHB's own length field is endian-dependent, so the byte order
        // must be sniffed from the byte-order magic (at offset 8) before the
        // block walk starts. 0x1A2B3C4D stored LE reads "4D 3C 2B 1A".
        if (bytes.size >= 12) {
            val b8 = bytes[8].toInt() and 0xFF
            val b9 = bytes[9].toInt() and 0xFF
            val b10 = bytes[10].toInt() and 0xFF
            val b11 = bytes[11].toInt() and 0xFF
            bigEndian = b8 == 0x1A && b9 == 0x2B && b10 == 0x3C && b11 == 0x4D
        }
        var pos = 0
        while (pos + 8 <= bytes.size) {
            val type = u32(pos)
            val total = u32(pos + 4).toInt()
            if (total < 12 || pos + total > bytes.size) break
            when (type) {
                BLOCK_SHB -> parseShb(pos + 8, total - 12)
                BLOCK_IDB -> parseIdb(pos + 8, total - 12)
                BLOCK_EPB -> parseEpb(pos + 8, total - 12)
                BLOCK_SPB -> parseSpb(pos + 8, total - 12)
                else -> Unit  // ISB / NRB / custom blocks: skipped by length
            }
            pos += total
        }
    }

    private fun parseShb(body: Int, bodyLen: Int) {
        if (bodyLen < 16) return
        val bom = u32(body)
        if (bom != BYTE_ORDER_MAGIC && bom != BYTE_ORDER_MAGIC_SWAPPED) return
        // Multiple sections reset the interface list per spec.
        interfaces.clear()
    }

    private fun parseIdb(body: Int, bodyLen: Int) {
        if (bodyLen < 8) return
        val linkType = u16(body)
        val snaplen = u32(body + 4)
        var unitNanos = 1_000L  // default: microseconds
        var p = body + 8
        val end = body + bodyLen
        while (p + 4 <= end) {
            val code = u16(p)
            val len = u16(p + 2)
            if (code == 0) break  // opt_endofopt
            if (code == OPT_IF_TSRESOL && len == 1 && p + 5 <= end) {
                val v = bytes[p + 4].toInt() and 0xFF
                unitNanos = if (v and 0x80 != 0) {
                    1L shl (v and 0x7F)  // 2^n nanoseconds
                } else {
                    // 10^-v seconds in nanoseconds; 6 -> 1_000, 9 -> 1.
                    var ns = 1_000_000_000L
                    repeat(v) { ns /= 10 }
                    ns
                }
            }
            p += 4 + ((len + 3) / 4) * 4
        }
        interfaces.add(Interface(linkType, snaplen, unitNanos))
    }

    private fun parseEpb(body: Int, bodyLen: Int) {
        if (bodyLen < 20) return
        val ifId = u32(body).toInt()
        val tsHi = u32(body + 4)
        val tsLo = u32(body + 8)
        val captured = u32(body + 12).toInt()
        if (captured < 0 || body + 20 + captured > body + bodyLen) return
        val unit = interfaces.getOrNull(ifId)?.unitNanos ?: 1_000L
        val ts = (tsHi shl 32) or tsLo
        val data = bytes.copyOfRange(body + 20, body + 20 + captured)
        packets.add(NgPacket(ts * unit, data))
    }

    private fun parseSpb(body: Int, bodyLen: Int) {
        if (bodyLen < 4) return
        val original = u32(body).toInt()
        val captured = minOf(original, bodyLen - 4)
        if (captured < 0) return
        packets.add(NgPacket(0, bytes.copyOfRange(body + 4, body + 4 + captured)))
    }

    /** All imported packets in file order. */
    fun packets(): List<NgPacket> {
        parseOnce()
        return packets.toList()
    }

    /** Declared interfaces in file order. */
    fun interfaces(): List<Interface> {
        parseOnce()
        return interfaces.toList()
    }

    /**
     * Packet payloads lifted to IPv4 datagrams: LINKTYPE_RAW (101) payloads
     * are the datagrams themselves; LINKTYPE_ETHERNET (1) frames are
     * unwrapped at their 0x0800 boundary.
     */
    fun ipv4Datagrams(): List<Pair<Long, Ipv4Datagram>> {
        parseOnce()
        val linkTypes = interfaces().map { it.linkType }
        return packets().mapNotNull { pkt ->
            val link = linkTypes.getOrElse(0) { 101 }
            val candidate = if (link == 1 && pkt.data.size >= 14) {
                if (pkt.data[12].toInt() == 0x08 && pkt.data[13].toInt() == 0x00) {
                    pkt.data.copyOfRange(14, pkt.data.size)
                } else {
                    null
                }
            } else {
                pkt.data
            } ?: return@mapNotNull null
            parseIpv4(candidate)?.let { pkt.timestampNs to it }
        }
    }

    private fun parseIpv4(d: ByteArray): Ipv4Datagram? {
        if (d.size < 20) return null
        val version = (d[0].toInt() shr 4) and 0xF
        val ihl = d[0].toInt() and 0xF
        if (version != 4 || ihl < 5) return null
        val headerLen = ihl * 4
        if (headerLen > d.size) return null
        return Ipv4Datagram(
            version = version,
            ihl = ihl,
            protocol = d[9].toInt() and 0xFF,
            sourceAddress = d.copyOfRange(12, 16),
            destinationAddress = d.copyOfRange(16, 20),
            payload = d.copyOfRange(headerLen, d.size),
        )
    }
}
