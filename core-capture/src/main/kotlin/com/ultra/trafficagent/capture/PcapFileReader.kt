package com.ultra.trafficagent.capture

/**
 * Minimal libpcap file reader: supports the classic and nanosecond magics in
 * both byte orders, Ethernet link type, and IPv4/TCP extraction. Used by the
 * ROOT_PCAP_FILE capture mode and by desktop-side offline analysis.
 */
class PcapFormatException(message: String) : Exception(message)

data class PcapHeader(
    val majorVersion: Int,
    val minorVersion: Int,
    val snaplen: Int,
    val linkType: Int,
    val nanosecondTimestamps: Boolean,
    val bigEndian: Boolean,
)

data class PcapRecord(
    val timestampSec: Long,
    val timestampUsec: Long,  // micro- or nanoseconds depending on the magic
    val capturedLength: Int,
    val originalLength: Int,
    val data: ByteArray,
)

data class EthernetFrame(
    val destination: ByteArray,
    val source: ByteArray,
    val etherType: Int,
    val payload: ByteArray,
)

data class Ipv4Datagram(
    val version: Int,
    val ihl: Int,
    val protocol: Int,
    val sourceAddress: ByteArray,
    val destinationAddress: ByteArray,
    val payload: ByteArray,
) {
    val headerLength: Int get() = ihl * 4
}

data class TcpSegmentData(
    val sourcePort: Int,
    val destinationPort: Int,
    val sequence: Long,
    val flags: Int,
    val payload: ByteArray,
) {
    companion object {
        const val FLAG_FIN = 0x01
        const val FLAG_SYN = 0x02
        const val FLAG_RST = 0x04
        const val FLAG_PSH = 0x08
        const val FLAG_ACK = 0x10
    }
}

class PcapFileReader(private val bytes: ByteArray) {

    companion object {
        private val MAGIC_LE = byteArrayOf(0xD4.toByte(), 0xC3.toByte(), 0xB2.toByte(), 0xA1.toByte())          // 0xa1b2c3d4 written little-endian
        private val MAGIC_BE = byteArrayOf(0xA1.toByte(), 0xB2.toByte(), 0xC3.toByte(), 0xD4.toByte())          // written big-endian
        private val MAGIC_LE_NANO = byteArrayOf(0x4D.toByte(), 0x3C.toByte(), 0x2B.toByte(), 0x1A.toByte())       // 0xa1b23c4d little-endian
        private val MAGIC_BE_NANO = byteArrayOf(0xA1.toByte(), 0xB2.toByte(), 0x3C.toByte(), 0x4D.toByte())      // big-endian

        fun ipv4AddressToString(addr: ByteArray): String {
            if (addr.size != 4) return "?"
            return "${addr[0].toInt() and 0xFF}.${addr[1].toInt() and 0xFF}.${addr[2].toInt() and 0xFF}.${addr[3].toInt() and 0xFF}"
        }
    }

    // Endianness is resolved eagerly (it must not depend on the lazy header,
    // which itself reads multi-byte fields).
    private val bigEndian: Boolean = detectBigEndian()

    private val header: PcapHeader by lazy { parseHeader() }

    fun pcapHeader(): PcapHeader = header

    fun records(): List<PcapRecord> {
        val out = mutableListOf<PcapRecord>()
        var pos = 24
        while (pos + 16 <= bytes.size) {
            val tsSec = readU32(pos).toLong()
            val tsFrac = readU32(pos + 4).toLong()
            val inclLen = readU32(pos + 8).toInt()
            val origLen = readU32(pos + 12).toInt()
            pos += 16
            if (inclLen < 0 || pos + inclLen > bytes.size) {
                throw PcapFormatException("record truncated: inclLen=$inclLen at offset $pos")
            }
            out += PcapRecord(tsSec, tsFrac, inclLen, origLen, bytes.copyOfRange(pos, pos + inclLen))
            pos += inclLen
        }
        return out
    }

    fun ethernetFrames(): List<EthernetFrame> {
        if (header.linkType != 1) {
            throw PcapFormatException("unsupported link type ${header.linkType} (need Ethernet=1)")
        }
        return records().mapNotNull { rec ->
            val d = rec.data
            if (d.size < 14) return@mapNotNull null
            val dst = d.copyOfRange(0, 6)
            val src = d.copyOfRange(6, 12)
            val etherType = ((d[12].toInt() and 0xFF) shl 8) or (d[13].toInt() and 0xFF)
            EthernetFrame(dst, src, etherType, d.copyOfRange(14, d.size))
        }
    }

    fun ipv4Datagrams(): List<Ipv4Datagram> {
        // LINKTYPE_RAW (101): record payload IS the IPv4 datagram — the layout
        // our own PcapWriterBridge emits for TUN captures. Otherwise fall
        // back to Ethernet-framed files (link type 1).
        if (header.linkType == 101) {
            return records().mapNotNull { rec -> parseIpv4(rec.data) }
        }
        return ethernetFrames().filter { it.etherType == 0x0800 }.mapNotNull { frame ->
            parseIpv4(frame.payload)
        }
    }

    private fun parseIpv4(d: ByteArray): Ipv4Datagram? {
        if (d.size < 20) return null
        val version = (d[0].toInt() shr 4) and 0xF
        val ihl = d[0].toInt() and 0xF
        if (version != 4 || ihl < 5) return null
        val protocol = d[9].toInt() and 0xFF
        val headerLen = ihl * 4
        if (headerLen > d.size) return null
        return Ipv4Datagram(
            version = version,
            ihl = ihl,
            protocol = protocol,
            sourceAddress = d.copyOfRange(12, 16),
            destinationAddress = d.copyOfRange(16, 20),
            payload = d.copyOfRange(headerLen, d.size),
        )
    }

    fun tcpSegments(): List<TcpSegmentData> =
        ipv4Datagrams().filter { it.protocol == 6 }.mapNotNull { ip ->
            val t = ip.payload
            if (t.size < 20) return@mapNotNull null
            val dataOffset = (t[12].toInt() shr 4) and 0xF
            if (dataOffset < 5) return@mapNotNull null
            val headerLen = dataOffset * 4
            if (headerLen > t.size) return@mapNotNull null
            TcpSegmentData(
                sourcePort = ((t[0].toInt() and 0xFF) shl 8) or (t[1].toInt() and 0xFF),
                destinationPort = ((t[2].toInt() and 0xFF) shl 8) or (t[3].toInt() and 0xFF),
                sequence = readU32Big(t, 4),
                flags = t[13].toInt() and 0xFF,
                payload = t.copyOfRange(headerLen, t.size),
            )
        }

    // ---------- internals ----------

    private fun detectBigEndian(): Boolean {
        if (bytes.size < 24) throw PcapFormatException("file too short for pcap header")
        val magic = bytes.copyOfRange(0, 4)
        return when {
            magic.contentEquals(MAGIC_BE) -> true
            magic.contentEquals(MAGIC_BE_NANO) -> true
            magic.contentEquals(MAGIC_LE) -> false
            magic.contentEquals(MAGIC_LE_NANO) -> false
            else -> throw PcapFormatException("not a pcap file (bad magic)")
        }
    }

    private fun parseHeader(): PcapHeader {
        val magic = bytes.copyOfRange(0, 4)
        val nano = magic.contentEquals(MAGIC_LE_NANO) || magic.contentEquals(MAGIC_BE_NANO)
        val major = readU16(4)
        val minor = readU16(6)
        val snaplen = readU32(16).toInt()
        val linkType = readU32(20).toInt()
        return PcapHeader(major, minor, snaplen, linkType, nano, bigEndian)
    }

    private fun readU16(pos: Int): Int {
        val b0 = bytes[pos].toInt() and 0xFF
        val b1 = bytes[pos + 1].toInt() and 0xFF
        return if (bigEndian) (b0 shl 8) or b1 else (b1 shl 8) or b0
    }

    private fun readU32(pos: Int): Long {
        var v = 0L
        for (i in 0 until 4) {
            val b = bytes[pos + if (bigEndian) i else 3 - i].toLong() and 0xFF
            v = (v shl 8) or b
        }
        return v
    }

    private fun readU32Big(data: ByteArray, pos: Int): Long {
        var v = 0L
        for (i in 0 until 4) v = (v shl 8) or (data[pos + i].toLong() and 0xFF)
        return v
    }
}
