package com.ultra.trafficagent.capture

/** Builds synthetic pcap files for tests (classic magic, both endiannesses). */
object PcapBuilder {

    fun pcapFile(packets: List<ByteArray>, bigEndian: Boolean = false): ByteArray {
        val out = mutableListOf<Byte>()
        val magic = if (bigEndian) {
            listOf(0xA1.toByte(), 0xB2.toByte(), 0xC3.toByte(), 0xD4.toByte())
        } else {
            listOf(0xD4.toByte(), 0xC3.toByte(), 0xB2.toByte(), 0xA1.toByte())
        }
        out += magic
        out += u16(2, bigEndian) // version major
        out += u16(4, bigEndian) // version minor
        out += u32(0, bigEndian) // thiszone
        out += u32(0, bigEndian) // sigfigs
        out += u32(65535, bigEndian) // snaplen
        out += u32(1, bigEndian) // linktype Ethernet
        for ((i, pkt) in packets.withIndex()) {
            out += u32(1700000000L + i, bigEndian) // ts_sec
            out += u32(1000L + i, bigEndian)       // ts_usec
            out += u32(pkt.size.toLong(), bigEndian)
            out += u32(pkt.size.toLong(), bigEndian)
            out += pkt.toList()
        }
        return out.toByteArray()
    }

    fun ethernet(payload: ByteArray, etherType: Int = 0x0800): ByteArray {
        val out = mutableListOf<Byte>()
        repeat(6) { out += 0x11 } // dst
        repeat(6) { out += 0x22 } // src
        out += ((etherType shr 8) and 0xFF).toByte()
        out += (etherType and 0xFF).toByte()
        out += payload.toList()
        return out.toByteArray()
    }

    fun ipv4(payload: ByteArray, protocol: Int = 6): ByteArray {
        val totalLength = 20 + payload.size
        val out = mutableListOf<Byte>()
        out += 0x45.toByte() // v4, IHL 5
        out += 0x00
        out += ((totalLength shr 8) and 0xFF).toByte()
        out += (totalLength and 0xFF).toByte()
        out += 0x00; out += 0x01 // id
        out += 0x40; out += 0x00 // flags DF
        out += 64.toByte()       // ttl
        out += protocol.toByte()
        out += 0x00; out += 0x00 // checksum (not verified)
        out += 192.toByte(); out += 168.toByte(); out += 1.toByte(); out += 10.toByte()   // src
        out += 142.toByte(); out += 250.toByte(); out += 10.toByte(); out += 20.toByte()  // dst
        out += payload.toList()
        return out.toByteArray()
    }

    fun tcp(payload: ByteArray, srcPort: Int = 44444, dstPort: Int = 80, seq: Long = 1000L, flags: Int = 0x18): ByteArray {
        val out = mutableListOf<Byte>()
        out += u16Bytes(srcPort)
        out += u16Bytes(dstPort)
        out += u32Bytes(seq)
        out += u32Bytes(0)
        out += 0x50.toByte() // data offset 5
        out += flags.toByte()
        out += u16Bytes(0xFFFF) // window
        out += u16Bytes(0)     // checksum
        out += u16Bytes(0)     // urgent
        out += payload.toList()
        return out.toByteArray()
    }

    private fun u16Bytes(v: Int): List<Byte> = listOf(((v shr 8) and 0xFF).toByte(), (v and 0xFF).toByte())
    private fun u32Bytes(v: Long): List<Byte> =
        listOf(((v shr 24) and 0xFF).toByte(), ((v shr 16) and 0xFF).toByte(), ((v shr 8) and 0xFF).toByte(), (v and 0xFF).toByte())

    private fun u16(v: Int, bigEndian: Boolean): List<Byte> = if (bigEndian) u16Bytes(v) else u16Bytes(v).reversed()
    private fun u32(v: Long, bigEndian: Boolean): List<Byte> = if (bigEndian) u32Bytes(v) else u32Bytes(v).reversed()
}
