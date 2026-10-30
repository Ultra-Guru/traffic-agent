package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Mutation-killer tests for [PcapNgFileReader]: byte-exact big-endian
 * walks, Simple Packet Blocks, corrupt-length guards, tsresol variants
 * and multi-interface/multi-section behaviour.
 */
class PcapNgFileReaderKillerTest {

    private val ip = PcapBuilder.ipv4(PcapBuilder.tcp("GET /b HTTP/1.1\r\nHost: y\r\n\r\n".toByteArray()))

    @Test
    fun `big endian epb timestamps and lengths are exact`() {
        val file = NgBuilder.file(
            listOf(
                ip to 4_294_967_296L + 5L,  // forces non-zero high 32 bits
                ip to 123_456L,
            ),
            bigEndian = true,
        )
        val reader = PcapNgFileReader(file)
        val packets = reader.packets()
        assertEquals(2, packets.size)
        // 0x1_00000005 us -> ns = 0x1_00000005 * 1000 (fits in Long).
        assertEquals(4_294_967_301_000L, packets[0].timestampNs)
        assertEquals(123_456_000L, packets[1].timestampNs)
        assertEquals(ip.size, packets[0].data.size)
        assertEquals(ip[0], packets[0].data[0])
        assertEquals(ip[ip.size - 1], packets[0].data[ip.size - 1])
    }

    @Test
    fun `big endian interfaces report linktype and snaplen`() {
        val file = NgBuilder.file(listOf(ip to 1L), linkType = 1, bigEndian = true)
        val interfaces = PcapNgFileReader(file).interfaces()
        assertEquals(1, interfaces.size)
        assertEquals(1, interfaces[0].linkType)
        assertEquals(0xFFFFL, interfaces[0].snaplen)
        assertEquals(1000L, interfaces[0].unitNanos)
    }

    @Test
    fun `simple packet blocks yield packets without timestamps`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(101))
        // SPB: type 3, total 12+4+len, original len, data (no padding needed
        // for the reader but total must be multiple of 4).
        out.u32(0x00000003, false)
        out.u32((12 + 4 + 7 + 1).toLong(), false)
        out.u32(7, false)
        out.bytes(byteArrayOf(9, 8, 7, 6, 5, 4, 3, 0))
        out.u32((12 + 4 + 7 + 1).toLong(), false)  // trailing total length
        val reader = PcapNgFileReader(out.toByteArray())
        val packets = reader.packets()
        assertEquals(1, packets.size)
        assertEquals(0L, packets[0].timestampNs)
        assertEquals(7, packets[0].data.size)
        assertEquals(9.toByte(), packets[0].data[0])
    }

    @Test
    fun `corrupt total length stops the walk instead of crashing`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(101))
        // Truncated EPB claiming more bytes than the buffer holds.
        out.u32(0x00000006, false)
        out.u32(1_000_000L, false)
        out.bytes(ByteArray(16))
        val reader = PcapNgFileReader(out.toByteArray())
        assertEquals(0, reader.packets().size)
    }

    @Test
    fun `captured length beyond the block is rejected`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(101))
        out.u32(0x00000006, false)
        out.u32(36, false)  // 12 + body 24
        val body = ByteSink()
        body.u32(0, false)
        body.u32(0, false)
        body.u32(1, false)
        body.u32(100, false)  // captured > body remainder
        body.u32(100, false)
        out.bytes(body.toByteArray())
        out.u32(36, false)
        assertEquals(0, PcapNgFileReader(out.toByteArray()).packets().size)
    }

    @Test
    fun `tsresol decimal variants map to exact nanos`() {
        for ((resol, nanos) in listOf(0 to 1_000_000_000L, 3 to 1_000_000L, 6 to 1_000L, 9 to 1L)) {
            val file = NgBuilder.file(listOf(ip to 2L), tsresol = resol)
            val packets = PcapNgFileReader(file).packets()
            assertEquals(2L * nanos, packets[0].timestampNs, "tsresol=$resol")
        }
    }

    @Test
    fun `multiple interfaces select per-packet tsresol`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(101, tsresol = 6))   // if 0: microseconds
        out.bytes(NgBuilder.idb(101, tsresol = 9))   // if 1: nanoseconds
        out.bytes(NgBuilder.epb(ip, 5, interfaceId = 0))
        out.bytes(NgBuilder.epb(ip, 5, interfaceId = 1))
        val packets = PcapNgFileReader(out.toByteArray()).packets()
        assertEquals(2, packets.size)
        assertEquals(5_000L, packets[0].timestampNs)
        assertEquals(5L, packets[1].timestampNs)
    }

    @Test
    fun `two sections reset the interface list`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        out.bytes(NgBuilder.idb(1))                  // Ethernet
        out.bytes(NgBuilder.shb(false))              // new section
        out.bytes(NgBuilder.idb(101))                // RAW
        out.bytes(NgBuilder.epb(ip, 7))
        val reader = PcapNgFileReader(out.toByteArray())
        assertEquals(1, reader.interfaces().size)
        assertEquals(101, reader.interfaces()[0].linkType)
        // And the packet survived the section boundary.
        assertEquals(1, reader.packets().size)
    }

    @Test
    fun `options longer than the block stop parsing safely`() {
        val out = ByteSink()
        out.bytes(NgBuilder.shb(false))
        // IDB whose tsresol option claims more length than the block has.
        out.u32(0x00000001, false)
        out.u32(28, false)  // 12 + 16 body
        val body = ByteSink()
        body.u16(101, false)
        body.u16(0, false)
        body.u32(0xFFFF, false)
        body.u16(9, false)
        body.u16(200, false)  // absurd option length
        body.bytes(ByteArray(4))
        out.bytes(body.toByteArray())
        out.u32(28, false)
        val interfaces = PcapNgFileReader(out.toByteArray()).interfaces()
        // The IDB itself still registers with the default unit.
        assertEquals(1, interfaces.size)
        assertEquals(1000L, interfaces[0].unitNanos)
    }

    @Test
    fun `empty and header-only files are inert`() {
        assertEquals(0, PcapNgFileReader(ByteArray(0)).packets().size)
        assertEquals(0, PcapNgFileReader(NgBuilder.shb(false)).packets().size)
        assertEquals(0, PcapNgFileReader(NgBuilder.shb(false)).interfaces().size)
    }

    @Test
    fun `arbitrary bytes neither parse nor detect as pcapng`() {
        val junk = ByteArray(64) { it.toByte() }
        assertTrue(!PcapNgFileReader.looksLikePcapNg(junk))
        assertEquals(0, PcapNgFileReader(junk).packets().size)
        assertEquals(0, PcapNgFileReader(junk).ipv4Datagrams().size)
    }
}
