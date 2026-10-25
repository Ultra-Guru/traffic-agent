package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import java.nio.ByteBuffer

/** Decoders for the ForwardStack binary outbox frames (基建一). */
class TcpStackBridgeTest {

    private fun connectFrame(entries: List<Triple<StackFlow, Pair<Int, Int>, Boolean>>): ByteArray {
        val b = ByteBuffer.allocate(entries.size * 19)
        for ((orig, eff, isUdp) in entries) {
            b.put(if (isUdp) 1 else 0)
            b.putInt(orig.srcIp)
            b.putShort(orig.srcPort.toShort())
            b.putInt(orig.dstIp)
            b.putShort(orig.dstPort.toShort())
            b.putInt(eff.first)
            b.putShort(eff.second.toShort())
        }
        return b.array()
    }

    @Test
    fun `decodes connect entries with redirect info`() {
        val frame = connectFrame(
            listOf(
                Triple(StackFlow(1, 40000, 2, 443), StackFlow.parseIp("127.0.0.1") to 8843, false),
                Triple(StackFlow(3, 50000, 4, 53), 4 to 53, true),
            ),
        )
        val decoded = StackFrames.decodeConnects(frame)
        assertEquals(2, decoded.size)
        val tls = decoded[0]
        assertEquals(1, tls.original.srcIp)
        assertEquals(40000, tls.original.srcPort)
        assertEquals(443, tls.original.dstPort)
        assertEquals(StackFlow.parseIp("127.0.0.1"), tls.effectiveDstIp)
        assertEquals(8843, tls.effectiveDstPort)
        assertTrue(!tls.isUdp)
        val dns = decoded[1]
        assertTrue(dns.isUdp)
        assertEquals(4, dns.effectiveDstIp)
        assertEquals(53, dns.effectiveDstPort)
    }

    @Test
    fun `empty connect frame decodes to empty list`() {
        assertTrue(StackFrames.decodeConnects(ByteArray(0)).isEmpty())
    }

    @Test
    fun `truncated connect frame drops the partial entry`() {
        val full = connectFrame(listOf(Triple(StackFlow(1, 2, 3, 443), 5 to 6, false)))
        val truncated = full.copyOf(full.size - 1)
        assertTrue(StackFrames.decodeConnects(truncated).isEmpty())
    }

    @Test
    fun `decodes send entries with payload`() {
        val payload = "hello".toByteArray()
        val b = ByteBuffer.allocate(16 + payload.size)
        b.putInt(0xC0A8010A.toInt())
        b.putShort(40000.toShort())
        b.putInt(0x8EFA0A14.toInt())
        b.putShort(8081.toShort())
        b.putInt(payload.size)
        b.put(payload)
        val sends = StackFrames.decodeSends(b.array())
        assertEquals(1, sends.size)
        assertEquals(0xC0A8010A.toInt(), sends[0].flow.srcIp)
        assertEquals(40000, sends[0].flow.srcPort)
        assertEquals(8081, sends[0].flow.dstPort)
        assertEquals("hello", String(sends[0].data))
    }

    @Test
    fun `multiple sends and empty sends round trip`() {
        fun entry(data: ByteArray): ByteArray {
            val b = ByteBuffer.allocate(16 + data.size)
            b.putInt(1).putShort(10.toShort()).putInt(2).putShort(20.toShort())
            b.putInt(data.size).put(data)
            return b.array()
        }
        val frame = entry("a".toByteArray()) + entry("bc".toByteArray())
        val sends = StackFrames.decodeSends(frame)
        assertEquals(2, sends.size)
        assertEquals("a", String(sends[0].data))
        assertEquals("bc", String(sends[1].data))
        assertTrue(StackFrames.decodeSends(ByteArray(0)).isEmpty())
    }

    @Test
    fun `send frame with length beyond buffer is rejected`() {
        val b = ByteBuffer.allocate(16)
        b.putInt(1).putShort(10.toShort()).putInt(2).putShort(20.toShort())
        b.putInt(100)  // claims 100 bytes but none follow
        assertTrue(StackFrames.decodeSends(b.array()).isEmpty())
    }

    @Test
    fun `decodes close entries`() {
        val b = ByteBuffer.allocate(12)
        b.putInt(1).putShort(40000.toShort()).putInt(2).putShort(443.toShort())
        val closes = StackFrames.decodeCloses(b.array())
        assertEquals(1, closes.size)
        assertEquals(443, closes[0].flow.dstPort)
        assertEquals(40000, closes[0].flow.srcPort)
    }

    @Test
    fun `ip formatting round trips`() {
        assertEquals("192.168.1.10", StackFlow.formatIp(StackFlow.parseIp("192.168.1.10")))
        assertEquals("127.0.0.1", StackFlow.formatIp(StackFlow.parseIp("127.0.0.1")))
        assertEquals("0.0.0.0", StackFlow.formatIp(0))
        assertEquals("255.255.255.255", StackFlow.formatIp(-1))
        assertEquals("1.2.3.4", StackFlow.formatIp(0x01020304))
    }

    @Test
    fun `parseIp rejects malformed input`() {
        assertThrows<IllegalArgumentException> {
            StackFlow.parseIp("1.2.3")
        }
        assertThrows<IllegalArgumentException> {
            StackFlow.parseIp("1.2.3.999")
        }
    }
}
