package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PcapFileReaderTest {

    private fun samplePackets(): List<ByteArray> = listOf(
        PcapBuilder.ethernet(PcapBuilder.ipv4(PcapBuilder.tcp("GET / HTTP/1.1\r\nHost: a\r\n\r\n".toByteArray()))),
        PcapBuilder.ethernet(PcapBuilder.ipv4(PcapBuilder.tcp("hello".toByteArray(), dstPort = 443))),
    )

    @Test
    fun `parses little-endian classic pcap header`() {
        val file = PcapBuilder.pcapFile(samplePackets(), bigEndian = false)
        val reader = PcapFileReader(file)
        val h = reader.pcapHeader()
        assertEquals(2, h.majorVersion)
        assertEquals(4, h.minorVersion)
        assertEquals(65535, h.snaplen)
        assertEquals(1, h.linkType)
        assertTrue(!h.bigEndian)
        assertTrue(!h.nanosecondTimestamps)
    }

    @Test
    fun `parses big-endian classic pcap header`() {
        val file = PcapBuilder.pcapFile(samplePackets(), bigEndian = true)
        val reader = PcapFileReader(file)
        val h = reader.pcapHeader()
        assertTrue(h.bigEndian)
        assertEquals(2, reader.records().size)
    }

    @Test
    fun `iterates records with timestamps and lengths`() {
        val reader = PcapFileReader(PcapBuilder.pcapFile(samplePackets()))
        val records = reader.records()
        assertEquals(2, records.size)
        assertEquals(1700000000L, records[0].timestampSec)
        assertEquals(1000L, records[0].timestampUsec)
        assertEquals(1700000001L, records[1].timestampSec)
        assertEquals(records[0].capturedLength, records[0].data.size)
    }

    @Test
    fun `extracts ethernet frames and filters ipv4`() {
        val reader = PcapFileReader(PcapBuilder.pcapFile(samplePackets()))
        assertEquals(2, reader.ethernetFrames().size)
        assertEquals(2, reader.ipv4Datagrams().size)
    }

    @Test
    fun `extracts tcp segments with payload`() {
        val reader = PcapFileReader(PcapBuilder.pcapFile(samplePackets()))
        val segments = reader.tcpSegments()
        assertEquals(2, segments.size)
        assertEquals(44444, segments[0].sourcePort)
        assertEquals(80, segments[0].destinationPort)
        assertEquals(1000L, segments[0].sequence)
        assertEquals(0x18, segments[0].flags)
        assertEquals("GET / HTTP/1.1\r\nHost: a\r\n\r\n", String(segments[0].payload))
    }

    @Test
    fun `formats ipv4 addresses`() {
        assertEquals("192.168.1.10", PcapFileReader.ipv4AddressToString(byteArrayOf(192.toByte(), 168.toByte(), 1, 10)))
        assertEquals("0.0.0.0", PcapFileReader.ipv4AddressToString(byteArrayOf(0, 0, 0, 0)))
    }

    @Test
    fun `rejects bad magic`() {
        val bad = ByteArray(40) { it.toByte() }
        assertThrows(PcapFormatException::class.java) { PcapFileReader(bad).pcapHeader() }
    }

    @Test
    fun `rejects truncated header`() {
        assertThrows(PcapFormatException::class.java) { PcapFileReader(ByteArray(10)).pcapHeader() }
    }

    @Test
    fun `rejects truncated record`() {
        val file = PcapBuilder.pcapFile(samplePackets())
        val cut = file.copyOfRange(0, file.size - 10) // chop into last record
        val reader = PcapFileReader(cut)
        assertThrows(PcapFormatException::class.java) { reader.records() }
    }
}

class RootCommandBuilderTest {

    @Test
    fun `wraps commands with su`() {
        assertEquals("su -c 'ls -la'", RootCommandBuilder.suWrap("ls -la"))
    }

    @Test
    fun `builds tcp redirect command`() {
        assertEquals(
            "iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-port 8188",
            RootCommandBuilder.redirectTcpToPort(8188),
        )
    }

    @Test
    fun `teardown deletes the rule`() {
        assertEquals(
            "iptables -t nat -D OUTPUT -p tcp -j REDIRECT --to-port 8188",
            RootCommandBuilder.removeRedirectTcpToPort(8188),
        )
    }

    @Test
    fun `builds tcpdump command with snaplen`() {
        assertEquals(
            "tcpdump -i any -s 65535 -w /sdcard/capture.pcap",
            RootCommandBuilder.tcpdumpToFile("/sdcard/capture.pcap"),
        )
        assertEquals(
            "tcpdump -i any -s 256 -w /sdcard/capture.pcap",
            RootCommandBuilder.tcpdumpToFile("/sdcard/capture.pcap", snaplen = 256),
        )
    }

    @Test
    fun `root setup contains tcp and udp redirects`() {
        val setup = RootCommandBuilder.rootIptablesSetup(9000)
        assertEquals(2, setup.size)
        assertTrue(setup[0].contains("-p tcp"))
        assertTrue(setup[1].contains("-p udp"))
        assertTrue(setup.all { it.startsWith("su -c '") })
    }

    @Test
    fun `teardown mirrors setup`() {
        val setup = RootCommandBuilder.rootIptablesSetup(9000)
        val teardown = RootCommandBuilder.rootIptablesTeardown(9000)
        assertEquals(setup.size, teardown.size)
        assertTrue(setup.zip(teardown).all { (a, b) ->
            a.replace("-A ", "") == b.replace("-D ", "")
        })
    }
}

class CaptureModelsTest {

    @Test
    fun `captured request computes sizes`() {
        val req = CapturedRequest(
            id = 1, timestampMs = 0, host = "a.com", path = "/x", method = "GET",
            status = 200, requestHeaders = mapOf("Host" to "a.com"), responseHeaders = emptyMap(),
            requestBody = "", responseBody = "", bytesUp = 100, bytesDown = 900,
            protocol = Protocol.HTTP1, appUid = 10042,
        )
        assertEquals(1000L, req.totalSize)
        assertEquals(900L, req.responseSize)
        assertTrue(!req.isSecure)
    }

    @Test
    fun `protocol enum values are stable`() {
        val expected = listOf("HTTP1", "HTTP2", "TLS", "WEBSOCKET", "QUIC", "DNS", "TCP", "UDP", "UNKNOWN")
        assertEquals(expected, Protocol.values().map { it.name })
    }
}
