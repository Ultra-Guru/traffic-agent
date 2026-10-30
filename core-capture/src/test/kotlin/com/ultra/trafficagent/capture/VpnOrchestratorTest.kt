package com.ultra.trafficagent.capture

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.IOException
import java.util.concurrent.CountDownLatch
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit

/**
 * VpnOrchestrator end-to-end over fakes: a scripted ForwardStack, an
 * in-memory TUN and loopback channels — verifying the command pump, DNS
 * rewriting, failure resets and statistics without any JNI.
 */
class VpnOrchestratorTest {

    // ------------------------------------------------------------- fakes

    /** In-memory TUN: packets in, packets out, all writes logged. */
    private class FakeTun : TunIo {
        val toTun = LinkedBlockingQueue<ByteArray>()
        val fromTun = LinkedBlockingQueue<ByteArray>()
        @Volatile
        var closed = false

        override fun readPacket(dst: ByteArray): Int {
            val pkt = fromTun.poll(2, TimeUnit.SECONDS) ?: return -1
            System.arraycopy(pkt, 0, dst, 0, pkt.size)
            return pkt.size
        }

        override fun writePacket(packet: ByteArray): Boolean {
            if (closed) return false
            toTun.add(packet)
            return true
        }

        override fun close() {
            closed = true
        }
    }

    /** Scriptable stack: records calls, answers with queued results. */
    private class FakeStack : ForwardStackApi {
        val tunPackets = LinkedBlockingQueue<ByteArray>()
        val upstreamData = LinkedBlockingQueue<Pair<StackFlow, ByteArray>>()
        val upstreamClosed = LinkedBlockingQueue<StackFlow>()
        val sweeps = intArrayOf(0)

        val nextConnects = LinkedBlockingQueue<StackConnect>()
        val nextSends = LinkedBlockingQueue<StackSend>()
        val nextCloses = LinkedBlockingQueue<StackClose>()

        /** Packets to emit for the NEXT onTunPacket call. */
        val respondToTun = LinkedBlockingQueue<ByteArray>()

        override fun onTunPacket(packet: ByteArray, tsMs: Long): List<ByteArray> {
            tunPackets.add(packet)
            val out = ArrayList<ByteArray>()
            respondToTun.drainTo(out)
            return out
        }

        override fun onUpstreamData(flow: StackFlow, data: ByteArray, tsMs: Long): List<ByteArray> {
            upstreamData.add(flow to data)
            return listOf(byteArrayOf(9))
        }

        override fun onUpstreamClosed(flow: StackFlow, tsMs: Long): List<ByteArray> {
            upstreamClosed.add(flow)
            return emptyList()
        }

        override fun sweep(nowMs: Long): List<ByteArray> {
            sweeps[0]++
            return emptyList()
        }

        override fun takeConnects(): List<StackConnect> {
            val out = ArrayList<StackConnect>()
            nextConnects.drainTo(out)
            return out
        }

        override fun takeSends(): List<StackSend> {
            val out = ArrayList<StackSend>()
            nextSends.drainTo(out)
            return out
        }

        override fun takeCloses(): List<StackClose> {
            val out = ArrayList<StackClose>()
            nextCloses.drainTo(out)
            return out
        }
    }

    /** Channel recording sends; optionally echoes bytes back as upstream data. */
    private class FakeChannel(
        val flow: StackFlow,
        val opened: CountDownLatch,
        val sends: LinkedBlockingQueue<ByteArray>,
        private val sink: UpstreamSink?,
        private val echo: Boolean,
    ) : UpstreamChannel {
        @Volatile
        var closed = false

        override fun send(data: ByteArray): Boolean {
            if (closed) return false
            sends.add(data)
            if (echo && sink != null) {
                sink.onUpstreamBytes(flow, data)
            }
            return true
        }

        override fun close() {
            closed = true
            sink?.onUpstreamEof(flow)
        }
    }

    private class FakeOpener(val failAll: Boolean = false) : SocketOpener {
        val opened = LinkedBlockingQueue<Triple<StackFlow, String, Int>>()
        val channels = ArrayList<FakeChannel>()
        val openLatches = ArrayList<CountDownLatch>()

        override fun open(
            flow: StackFlow,
            ip: String,
            port: Int,
            udp: Boolean,
            sink: UpstreamSink,
        ): UpstreamChannel? {
            if (failAll) return null
            opened.add(Triple(flow, ip, port))
            val latch = CountDownLatch(1)
            synchronized(openLatches) { openLatches.add(latch) }
            val channel = FakeChannel(flow, latch, LinkedBlockingQueue(), sink, echo = true)
            synchronized(channels) { channels.add(channel) }
            latch.countDown()
            return channel
        }

        fun awaitOpened(n: Int, timeoutMs: Long = 5_000) {
            val deadline = System.nanoTime() + timeoutMs * 1_000_000
            while (true) {
                val channelCount = synchronized(channels) { channels.size }
                if (opened.size >= n && channelCount >= n) return
                if (System.nanoTime() > deadline) return
                Thread.sleep(10)
            }
        }
    }

    // ------------------------------------------------------------ helpers

    private fun flow(dstIp: Int = 0x08080808, dstPort: Int = 80, srcPort: Int = 44444) =
        StackFlow(srcIp = 0x0A000002, srcPort = srcPort, dstIp = dstIp, dstPort = dstPort)

    // -------------------------------------------------------------- tests

    @Test
    fun `connect and send flow through to the opener and back`() {
        val tun = FakeTun()
        val stack = FakeStack()
        val opener = FakeOpener()
        val orch = VpnOrchestrator(tun, stack, opener, VpnOrchestrator.Config(sweepIntervalMs = 60_000))
        orch.start()
        try {
            val f = flow()
            stack.nextConnects.add(StackConnect(original = f, effectiveDstIp = f.dstIp, effectiveDstPort = 80, isUdp = false))
            stack.nextSends.add(StackSend(f, "ping".toByteArray()))
            tun.fromTun.add(byteArrayOf(1, 2, 3))

            opener.awaitOpened(1)
            // The send is delivered to the (echoing) fake channel, which
            // pushes the bytes back as upstream data, which the stack turns
            // into a TUN packet (our fake answers with [9]).
            val back = tun.toTun.poll(5, TimeUnit.SECONDS)
            assertTrue(back.contentEquals(byteArrayOf(9)), "expected echo packet, got ${back?.toList()}")

            val sent = opener.channels.first().sends.poll(5, TimeUnit.SECONDS)
            assertEquals("ping", String(sent ?: ByteArray(0)))
            val recorded = stack.tunPackets.poll(5, TimeUnit.SECONDS)
            assertTrue(recorded.contentEquals(byteArrayOf(1, 2, 3)))
        } finally {
            orch.stop()
        }
    }

    @Test
    fun `dns flows are rewritten to the configured resolver`() {
        val tun = FakeTun()
        val stack = FakeStack()
        val opener = FakeOpener()
        val orch = VpnOrchestrator(
            tun, stack, opener,
            VpnOrchestrator.Config(dnsForward = "223.5.5.5", sweepIntervalMs = 60_000),
        )
        orch.start()
        try {
            // App asks the advertised (fake) DNS 10.111.0.1:53.
            val dnsFlow = flow(dstIp = 0x0A6F0001, dstPort = 53, srcPort = 55555)
            stack.nextConnects.add(
                StackConnect(original = dnsFlow, effectiveDstIp = dnsFlow.dstIp, effectiveDstPort = 53, isUdp = true),
            )
            // A plain flow must NOT be rewritten.
            val webFlow = flow(dstIp = 0x08080808, dstPort = 80, srcPort = 44444)
            stack.nextConnects.add(
                StackConnect(original = webFlow, effectiveDstIp = webFlow.dstIp, effectiveDstPort = 80, isUdp = false),
            )
            tun.fromTun.add(byteArrayOf(1))

            opener.awaitOpened(2)
            val opened = listOf(opener.opened.poll(5, TimeUnit.SECONDS)!!, opener.opened.poll(5, TimeUnit.SECONDS)!!)
            val dns = opened.first { it.third == 53 }
            assertEquals("223.5.5.5", dns.second)
            val web = opened.first { it.third == 80 }
            assertEquals(StackFlow.formatIp(webFlow.dstIp), web.second)
        } finally {
            orch.stop()
        }
    }

    @Test
    fun `failed connects reset the flow through the stack`() {
        val tun = FakeTun()
        val stack = FakeStack()
        val opener = FakeOpener(failAll = true)
        val orch = VpnOrchestrator(tun, stack, opener, VpnOrchestrator.Config(sweepIntervalMs = 60_000))
        orch.start()
        try {
            val f = flow()
            stack.nextConnects.add(StackConnect(original = f, effectiveDstIp = f.dstIp, effectiveDstPort = 80, isUdp = false))
            tun.fromTun.add(byteArrayOf(1))

            val closed = stack.upstreamClosed.poll(5, TimeUnit.SECONDS)
            assertEquals(f, closed)
            assertTrue(orch.stats.connectFailures >= 1)
        } finally {
            orch.stop()
        }
    }

    @Test
    fun `close command closes the channel`() {
        val tun = FakeTun()
        val stack = FakeStack()
        val opener = FakeOpener()
        val orch = VpnOrchestrator(tun, stack, opener, VpnOrchestrator.Config(sweepIntervalMs = 60_000))
        orch.start()
        try {
            val f = flow()
            stack.nextConnects.add(StackConnect(original = f, effectiveDstIp = f.dstIp, effectiveDstPort = 80, isUdp = false))
            tun.fromTun.add(byteArrayOf(1))
            opener.awaitOpened(1)
            val channel = opener.channels.first()

            stack.nextCloses.add(StackClose(f))
            tun.fromTun.add(byteArrayOf(2))

            val deadline = System.nanoTime() + 5_000_000_000L
            while (!channel.closed) {
                assertTrue(System.nanoTime() < deadline, "channel was never closed")
                Thread.sleep(10)
            }
        } finally {
            orch.stop()
        }
    }

    @Test
    fun `stop closes everything and marks stats stopped`() {
        val tun = FakeTun()
        val stack = FakeStack()
        val opener = FakeOpener()
        val orch = VpnOrchestrator(tun, stack, opener, VpnOrchestrator.Config(sweepIntervalMs = 60_000))
        orch.start()
        val f = flow()
        stack.nextConnects.add(StackConnect(original = f, effectiveDstIp = f.dstIp, effectiveDstPort = 80, isUdp = false))
        tun.fromTun.add(byteArrayOf(1))
        opener.awaitOpened(1)
        val channel = opener.channels.first()

        orch.stop()

        assertTrue(channel.closed)
        assertTrue(tun.closed)
        assertTrue(!orch.stats.running)
        assertEquals(0, orch.stats.flowsActive)
    }

    @Test
    fun `tun packet observer receives every packet`() {
        val tun = FakeTun()
        val stack = FakeStack()
        val opener = FakeOpener()
        val seen = LinkedBlockingQueue<ByteArray>()
        val orch = VpnOrchestrator(
            tun, stack, opener,
            VpnOrchestrator.Config(sweepIntervalMs = 60_000, onTunPacket = { p, _ -> seen.add(p) }),
        )
        orch.start()
        try {
            tun.fromTun.add(byteArrayOf(7, 7, 7))
            val got = seen.poll(5, TimeUnit.SECONDS)
            assertTrue(got.contentEquals(byteArrayOf(7, 7, 7)))
        } finally {
            orch.stop()
        }
    }

    @Test
    fun `tap event lines parse into structured events`() {
        val ev = TapEvent.parse("sni\t1700000000123\t10.0.0.2:44444\t1.2.3.4:443\tapi.example.com\t0")
        assertEquals("sni", ev?.kind)
        assertEquals(1700000000123L, ev?.timestampMs)
        assertEquals("10.0.0.2:44444", ev?.src)
        assertEquals("1.2.3.4:443", ev?.dst)
        assertEquals("api.example.com", ev?.text)
        assertEquals(0, ev?.numeric)

        assertEquals(null, TapEvent.parse("bad line"))
        assertEquals(null, TapEvent.parse("a\tb\tc\td\te\tf"))
    }

    @Test
    fun `analysis tap decodes exchange jsonl into captured requests`() {
        val json = """{"id":11,"ts":1700000000999,"host":"h.example.com","path":"/a","method":"GET",""" +
            """"status":200,"reqHeaders":{"Host":"h.example.com"},"respHeaders":{},"reqBody":"",""" +
            """"respBody":"ok","up":10,"down":20,"protocol":"HTTP1","uid":null}"""
        // One-shot natives: the second drain must see empty arrays.
        var eventsLeft: Array<String>? = arrayOf("dns\t7\t10.0.0.2:5555\t10.111.0.1:53\th.example.com A 1.2.3.4\t1")
        var exchangesLeft: Array<String>? = arrayOf(json)
        val tap = VpnAnalysisTap(
            feedPacket = { _, _ -> 0 },
            takeEvents = { eventsLeft.also { eventsLeft = null } },
            takeExchanges = { exchangesLeft.also { exchangesLeft = null } },
        )
        tap.feed(byteArrayOf(1), 1)
        val drained = tap.drain()
        assertEquals(1, drained.events.size)
        assertEquals("dns", drained.events[0].kind)
        assertEquals("h.example.com A 1.2.3.4", drained.events[0].text)
        assertEquals(1, drained.exchanges.size)
        assertEquals("h.example.com", drained.exchanges[0].host)
        assertEquals("/a", drained.exchanges[0].path)
        assertEquals("ok", drained.exchanges[0].responseBody)
        assertEquals(Protocol.HTTP1, drained.exchanges[0].protocol)

        // Second drain is empty (state was consumed).
        val again = tap.drain()
        assertTrue(again.events.isEmpty())
        assertTrue(again.exchanges.isEmpty())
    }

    @Test
    fun `analysis tap swallows native failures`() {
        val tap = VpnAnalysisTap(
            feedPacket = { _, _ -> throw IOException("engine gone") },
            takeEvents = { throw RuntimeException("jni") },
            takeExchanges = { null },
        )
        tap.feed(byteArrayOf(1), 1)
        val drained = tap.drain()
        assertTrue(drained.events.isEmpty())
        assertTrue(drained.exchanges.isEmpty())
    }
}
