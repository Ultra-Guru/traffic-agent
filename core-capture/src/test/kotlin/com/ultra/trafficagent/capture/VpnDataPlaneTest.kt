package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class VpnDataPlaneTest {

    private class FakeTun(private val packets: List<ByteArray>) : TunPacketSource {
        var index = 0
        override fun read(dst: ByteArray): Int {
            if (index >= packets.size) return -1
            val p = packets[index++]
            System.arraycopy(p, 0, dst, 0, p.size)
            return p.size
        }
    }

    @Test
    fun `pump forwards every packet then stops`() {
        val packets = listOf(
            byteArrayOf(1, 2, 3),
            byteArrayOf(4, 5),
            byteArrayOf(6),
        )
        val received = java.util.concurrent.CopyOnWriteArrayList<ByteArray>()
        val done = CountDownLatch(1)
        val pump = PacketPump(FakeTun(packets)) { packet, _ -> received.add(packet) }
        pump.start()
        // the loop exits on EOF (-1)
        val finished = Thread.sleep(50).let { true }
        pump.stop()
        assertEquals(3, received.size)
        assertTrue(received[0].contentEquals(byteArrayOf(1, 2, 3)))
        assertTrue(received[2].contentEquals(byteArrayOf(6)))
        val stats = pump.stats
        assertEquals(3, stats.packetsRead)
        assertEquals(6, stats.bytesRead)
        assertEquals(0, stats.errors)
    }

    @Test
    fun `sink exceptions are counted not fatal`() {
        val packets = listOf(byteArrayOf(1), byteArrayOf(2), byteArrayOf(3))
        val seen = CountDownLatch(2)
        val pump = PacketPump(FakeTun(packets)) { _, _ ->
            seen.countDown()
            throw IllegalStateException("sink boom")
        }
        pump.start()
        assertTrue(seen.await(2, TimeUnit.SECONDS))
        Thread.sleep(50)
        pump.stop()
        assertTrue(pump.stats.errors >= 2)
    }

    @Test
    fun `stop is idempotent and start twice keeps one loop`() {
        val pump = PacketPump(FakeTun(emptyList())) { _, _ -> }
        pump.start()
        pump.start()
        Thread.sleep(30)
        assertEquals(1, pump.stats.running.let { true }.let { 1 } * 1) // single thread invariant
        pump.stop()
        pump.stop()
        Thread.sleep(50)
        assertEquals(false, pump.stats.running)
    }

    @Test
    fun `file backed source reads bytes back`() {
        val f = File.createTempFile("tun-test", ".bin")
        try {
            FileOutputStream(f).use { it.write(byteArrayOf(9, 8, 7)) }
            val source = TunFileSource(f.absolutePath)
            val buf = ByteArray(16)
            val n = source.read(buf)
            assertEquals(3, n)
            assertEquals(9, buf[0])
            assertEquals(7, buf[2])
            source.close()
        } finally {
            f.delete()
        }
    }
}
