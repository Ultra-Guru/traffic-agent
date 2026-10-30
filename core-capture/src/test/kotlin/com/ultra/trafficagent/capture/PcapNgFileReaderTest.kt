package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Byte-level pcapng builder for tests: emits SHB + IDB + EPBs in either
 * byte order, mirroring what PcapNgWriter produces on-device.
 */
internal object NgBuilder {

    fun shb(bigEndian: Boolean): ByteArray {
        val body = ByteSink()
        body.u32(0x1A2B3C4D, bigEndian)   // byte-order magic
        body.u16(1, bigEndian)             // major
        body.u16(0, bigEndian)             // minor
        body.u64(-1L, bigEndian)           // section length: unspecified
        body.u16(0, bigEndian)             // opt_endofopt
        body.u16(0, bigEndian)
        return block(0x0A0D0D0A, body.toByteArray(), bigEndian)
    }

    fun idb(linkType: Int, snaplen: Long = 0xFFFF, tsresol: Int = 6,
            bigEndian: Boolean = false): ByteArray {
        val body = ByteSink()
        body.u16(linkType, bigEndian)
        body.u16(0, bigEndian)
        body.u32(snaplen, bigEndian)
        // if_tsresol option: code 9, length 1, value, padded.
        body.u16(9, bigEndian)
        body.u16(1, bigEndian)
        body.bytes(byteArrayOf(tsresol.toByte(), 0, 0, 0))
        body.u16(0, bigEndian)  // opt_endofopt
        body.u16(0, bigEndian)
        return block(0x00000001, body.toByteArray(), bigEndian)
    }

    fun epb(data: ByteArray, tsUs: Long, interfaceId: Long = 0,
            bigEndian: Boolean = false): ByteArray {
        val body = ByteSink()
        body.u32(interfaceId, bigEndian)
        body.u32((tsUs ushr 32) and 0xFFFFFFFFL, bigEndian)
        body.u32(tsUs and 0xFFFFFFFFL, bigEndian)
        body.u32(data.size.toLong(), bigEndian)  // captured
        body.u32(data.size.toLong(), bigEndian)  // original
        body.bytes(data)
        val pad = (4 - (data.size % 4)) % 4
        body.bytes(ByteArray(pad))
        return block(0x00000006, body.toByteArray(), bigEndian)
    }

    fun file(packets: List<Pair<ByteArray, Long>>, linkType: Int = 101,
             tsresol: Int = 6, bigEndian: Boolean = false): ByteArray {
        val out = ByteSink()
        out.bytes(shb(bigEndian))
        out.bytes(idb(linkType, tsresol = tsresol, bigEndian = bigEndian))
        for ((data, ts) in packets) out.bytes(epb(data, ts, bigEndian = bigEndian))
        return out.toByteArray()
    }

    private fun block(type: Int, body: ByteArray, bigEndian: Boolean): ByteArray {
        val out = ByteSink()
        val total = 12 + body.size
        out.u32(type.toLong() and 0xFFFFFFFFL, bigEndian)
        out.u32(total.toLong(), bigEndian)
        out.bytes(body)
        out.u32(total.toLong(), bigEndian)
        return out.toByteArray()
    }
}

/** Tiny growable byte sink with endian-aware integer writers. */
internal class ByteSink {
    private val buf = ArrayList<Byte>()

    fun bytes(b: ByteArray) = b.forEach { buf.add(it) }

    fun u16(v: Int, bigEndian: Boolean) {
        if (bigEndian) {
            buf.add(((v shr 8) and 0xFF).toByte())
            buf.add((v and 0xFF).toByte())
        } else {
            buf.add((v and 0xFF).toByte())
            buf.add(((v shr 8) and 0xFF).toByte())
        }
    }

    fun u32(v: Long, bigEndian: Boolean) {
        val shifts = if (bigEndian) intArrayOf(24, 16, 8, 0) else intArrayOf(0, 8, 16, 24)
        for (s in shifts) buf.add(((v shr s) and 0xFF).toByte())
    }

    fun u64(v: Long, bigEndian: Boolean) {
        val hi = (v ushr 32) and 0xFFFFFFFFL
        val lo = v and 0xFFFFFFFFL
        if (bigEndian) {
            u32(hi, true)
            u32(lo, true)
        } else {
            u32(lo, false)
            u32(hi, false)
        }
    }

    fun toByteArray(): ByteArray = buf.toByteArray()
}

class PcapNgFileReaderTest {

    private fun httpPacket(): ByteArray =
        PcapBuilder.ipv4(PcapBuilder.tcp("GET /a HTTP/1.1\r\nHost: x\r\n\r\n".toByteArray()))

    @Test
    fun `detects pcapng by section header magic`() {
        val file = NgBuilder.file(listOf(httpPacket() to 1000L))
        assertTrue(PcapNgFileReader.looksLikePcapNg(file))
        assertTrue(!PcapNgFileReader.looksLikePcapNg(PcapBuilder.pcapFile(listOf(httpPacket()))))
        assertTrue(!PcapNgFileReader.looksLikePcapNg(byteArrayOf(1, 2, 3)))
    }

    @Test
    fun `parses interfaces and packets little-endian`() {
        val file = NgBuilder.file(
            listOf(
                httpPacket() to 1_700_000_123_456L,  // microseconds
                PcapBuilder.ipv4(PcapBuilder.tcp("hi".toByteArray())) to 1_700_000_999L,
            ),
        )
        val reader = PcapNgFileReader(file)
        val interfaces = reader.interfaces()
        assertEquals(1, interfaces.size)
        assertEquals(101, interfaces[0].linkType)
        assertEquals(1000L, interfaces[0].unitNanos)  // tsresol 6 -> microseconds

        val packets = reader.packets()
        assertEquals(2, packets.size)
        assertEquals(1_700_000_123_456_000L, packets[0].timestampNs)
        assertEquals(httpPacket().size, packets[0].data.size)
    }

    @Test
    fun `parses big-endian files`() {
        val file = NgBuilder.file(
            listOf(httpPacket() to 5L),
            linkType = 101,
            bigEndian = true,
        )
        val reader = PcapNgFileReader(file)
        assertEquals(1, reader.packets().size)
        val dg = reader.ipv4Datagrams()
        assertEquals(1, dg.size)
        assertEquals(6, dg[0].second.protocol)
    }

    @Test
    fun `lifts raw ipv4 datagrams with timestamps`() {
        val file = NgBuilder.file(listOf(httpPacket() to 42L))
        val dg = PcapNgFileReader(file).ipv4Datagrams()
        assertEquals(1, dg.size)
        assertEquals(42_000L, dg[0].first)  // us -> ns
        assertEquals(4, dg[0].second.version)
        assertEquals(6, dg[0].second.protocol)
        assertNotNull(dg[0].second.payload)
    }

    @Test
    fun `unwraps ethernet frames at 0800`() {
        val frame = PcapBuilder.ethernet(httpPacket())
        val file = NgBuilder.file(listOf(frame to 7L), linkType = 1)
        val dg = PcapNgFileReader(file).ipv4Datagrams()
        assertEquals(1, dg.size)
        assertEquals(6, dg[0].second.protocol)
    }

    @Test
    fun `drops non-ipv4 ethernet frames`() {
        val ipv6ish = PcapBuilder.ethernet(ByteArray(40), etherType = 0x86DD)
        val file = NgBuilder.file(listOf(ipv6ish to 7L), linkType = 1)
        assertEquals(0, PcapNgFileReader(file).ipv4Datagrams().size)
    }

    @Test
    fun `honours power-of-two tsresol`() {
        // 0x80 | 3: 2^3 = 8 nanoseconds per unit.
        val file = NgBuilder.file(listOf(httpPacket() to 125L), tsresol = 0x80 or 3)
        val packets = PcapNgFileReader(file).packets()
        assertEquals(1, packets.size)
        assertEquals(125L * 8L, packets[0].timestampNs)
    }

    @Test
    fun `skips unknown blocks by length`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(101))
        // Custom block type 0x00000BAD, body of 8 bytes.
        out.u32(0x00000BAD, false)
        out.u32(20L, false)
        out.bytes(ByteArray(8))
        out.u32(20L, false)
        out.bytes(NgBuilder.epb(httpPacket(), 10L))
        val reader = PcapNgFileReader(out.toByteArray())
        assertEquals(1, reader.packets().size)
    }

    @Test
    fun `snaplen clipping is visible in captured length`() {
        val pkt = ByteArray(100)
        pkt[0] = 0x45
        // Hand-build an EPB with captured=32, original=100.
        val body = ByteSink()
        body.u32(0L, false)
        body.u32(0L, false)
        body.u32(10L, false)
        body.u32(32L, false)
        body.u32(100L, false)
        body.bytes(pkt.copyOf(32))
        val total = 12 + 20 + 32
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(101))
        out.u32(0x00000006, false)
        out.u32(total.toLong(), false)
        out.bytes(body.toByteArray())
        out.u32(total.toLong(), false)

        val packets = PcapNgFileReader(out.toByteArray()).packets()
        assertEquals(1, packets.size)
        assertEquals(32, packets[0].data.size)
    }
}
