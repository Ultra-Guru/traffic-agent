package com.ultra.trafficagent.capture

import java.io.IOException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetSocketAddress
import java.net.Socket
import java.net.SocketException
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * TUN packet I/O contract: one [readPacket] = one raw IPv4 packet from the
 * device, one [writePacket] = one packet injected back. Implementations
 * must make [writePacket] safe to call from any thread (upstream socket
 * reader threads emit concurrently with the pump loop).
 */
interface TunIo {
    /** Reads one packet into [dst]; returns its length, or -1 on EOF. */
    fun readPacket(dst: ByteArray): Int

    /** Writes one packet back to the TUN; false when the write failed. */
    fun writePacket(packet: ByteArray): Boolean

    fun close()
}

/** The ForwardStack surface the orchestrator drives (JNI-backed in production). */
interface ForwardStackApi {
    fun onTunPacket(packet: ByteArray, tsMs: Long): List<ByteArray>
    fun onUpstreamData(flow: StackFlow, data: ByteArray, tsMs: Long): List<ByteArray>
    fun onUpstreamClosed(flow: StackFlow, tsMs: Long): List<ByteArray>
    fun sweep(nowMs: Long): List<ByteArray>
    fun takeConnects(): List<StackConnect>
    fun takeSends(): List<StackSend>
    fun takeCloses(): List<StackClose>
}

/** One opened upstream connection (TCP stream or UDP datagram pipe). */
interface UpstreamChannel {
    /** Writes payload towards the peer; false when the channel is gone. */
    fun send(data: ByteArray): Boolean
    fun close()
}

/** Callbacks the opener uses to hand upstream bytes back into the stack. */
interface UpstreamSink {
    fun onUpstreamBytes(flow: StackFlow, data: ByteArray)
    fun onUpstreamEof(flow: StackFlow)
}

/**
 * Opens the real sockets carrying a flow. [protect] must be applied to the
 * socket BEFORE connecting so it bypasses the VPN tunnel (Android
 * VpnService.protect) — otherwise the upstream connection loops back into
 * the TUN and the whole device deadlocks. [flow] is the original
 * client-side 4-tuple the stack knows; every callback on [sink] must name
 * it back verbatim.
 */
fun interface SocketOpener {
    fun open(flow: StackFlow, ip: String, port: Int, udp: Boolean, sink: UpstreamSink): UpstreamChannel?
}

/** Live counters of an orchestrator run. */
data class OrchestratorStats(
    val packetsFromTun: Long,
    val packetsToTun: Long,
    val bytesFromTun: Long,
    val bytesToTun: Long,
    val flowsOpened: Long,
    val flowsActive: Int,
    val connectFailures: Long,
    val running: Boolean,
)

/**
 * End-to-end VPN data plane (基建一「通」的上层编排):
 *
 *   TUN fd → pump loop → ForwardStack(C++) → connect/send/close commands
 *                    ↑                          ↓
 *            packets back to TUN        protected upstream sockets
 *                                        (or the local MITM proxy, per
 *                                         the stack's redirection)
 *
 * DNS (UDP/53) flows are optionally rewritten to [Config.dnsForward] so the
 * device resolves via a resolver the operator controls even when apps
 * hardcode their own.
 */
class VpnOrchestrator(
    private val tun: TunIo,
    private val stack: ForwardStackApi,
    private val opener: SocketOpener,
    private val config: Config = Config(),
) {
    data class Config(
        /** When set, every UDP/53 flow is forwarded to this resolver. */
        val dnsForward: String? = null,
        val sweepIntervalMs: Long = 5_000,
        /** Passive tap on every TUN packet (analysis engine / PCAP recording). */
        val onTunPacket: ((packet: ByteArray, timestampMs: Long) -> Unit)? = null,
    )

    private val running = AtomicBoolean(false)
    private val channels = ConcurrentHashMap<StackFlow, UpstreamChannel>()
    private val packetsFromTun = AtomicLong()
    private val packetsToTun = AtomicLong()
    private val bytesFromTun = AtomicLong()
    private val bytesToTun = AtomicLong()
    private val flowsOpened = AtomicLong()
    private val connectFailures = AtomicLong()

    private var pumpThread: Thread? = null
    private var sweepThread: Thread? = null

    private val sink = object : UpstreamSink {
        override fun onUpstreamBytes(flow: StackFlow, data: ByteArray) {
            if (!running.get()) return
            emitToTun(stack.onUpstreamData(flow, data, now()))
        }

        override fun onUpstreamEof(flow: StackFlow) {
            if (!running.get()) return
            emitToTun(stack.onUpstreamClosed(flow, now()))
        }
    }

    fun start() {
        if (!running.compareAndSet(false, true)) return
        pumpThread = Thread(::pumpLoop, "vpn-orchestrator-pump").apply {
            isDaemon = true
            start()
        }
        sweepThread = Thread(::sweepLoop, "vpn-orchestrator-sweep").apply {
            isDaemon = true
            start()
        }
    }

    fun stop() {
        if (!running.compareAndSet(true, false)) return
        pumpThread?.interrupt()
        sweepThread?.interrupt()
        for (channel in channels.values) {
            try {
                channel.close()
            } catch (_: Exception) {
            }
        }
        channels.clear()
        tun.close()
    }

    val stats: OrchestratorStats
        get() = OrchestratorStats(
            packetsFromTun = packetsFromTun.get(),
            packetsToTun = packetsToTun.get(),
            bytesFromTun = bytesFromTun.get(),
            bytesToTun = bytesToTun.get(),
            flowsOpened = flowsOpened.get(),
            flowsActive = channels.size,
            connectFailures = connectFailures.get(),
            running = running.get(),
        )

    // ------------------------------------------------------------ internals

    private fun pumpLoop() {
        val buf = ByteArray(32 * 1024)
        while (running.get()) {
            val n = try {
                tun.readPacket(buf)
            } catch (_: InterruptedException) {
                break
            } catch (_: IOException) {
                break
            }
            if (n < 0) break
            if (n == 0) continue
            val packet = buf.copyOf(n)
            val ts = now()
            packetsFromTun.incrementAndGet()
            bytesFromTun.addAndGet(n.toLong())
            config.onTunPacket?.let {
                try {
                    it(packet, ts)
                } catch (_: RuntimeException) {
                }
            }
            emitToTun(stack.onTunPacket(packet, ts))
            drainCommands()
        }
        running.set(false)
    }

    private fun sweepLoop() {
        while (running.get()) {
            try {
                Thread.sleep(config.sweepIntervalMs)
            } catch (_: InterruptedException) {
                break
            }
            if (!running.get()) break
            emitToTun(stack.sweep(now()))
            drainCommands()
        }
    }

    /** Acts on everything the stack asked for since the last drain. */
    private fun drainCommands() {
        for (connect in stack.takeConnects()) openChannel(connect)
        for (send in stack.takeSends()) {
            val channel = channels[send.flow]
            if (channel == null || !channel.send(send.data)) {
                connectFailures.incrementAndGet()
            }
        }
        for (close in stack.takeCloses()) {
            channels.remove(close.flow)?.let {
                try {
                    it.close()
                } catch (_: Exception) {
                }
            }
        }
    }

    private fun openChannel(connect: StackConnect) {
        val isDns = connect.isUdp && connect.original.dstPort == DNS_PORT
        val dnsForward = config.dnsForward
        val host = if (isDns && dnsForward != null) dnsForward else StackFlow.formatIp(connect.effectiveDstIp)
        val port = if (isDns && dnsForward != null) DNS_PORT else connect.effectiveDstPort
        val channel = try {
            opener.open(connect.original, host, port, connect.isUdp, sink)
        } catch (_: IOException) {
            null
        }
        if (channel == null) {
            connectFailures.incrementAndGet()
            // Tell the stack the upstream is gone so it resets the client
            // flow (FIN/RST towards the app instead of a silent black hole).
            emitToTun(stack.onUpstreamClosed(connect.original, now()))
            return
        }
        channels[connect.original] = channel
        flowsOpened.incrementAndGet()
    }

    private fun emitToTun(packets: List<ByteArray>) {
        for (p in packets) {
            if (tun.writePacket(p)) {
                packetsToTun.incrementAndGet()
                bytesToTun.addAndGet(p.size.toLong())
            }
        }
    }

    private fun now(): Long = System.currentTimeMillis()

    private companion object {
        const val DNS_PORT = 53
    }
}

/**
 * JDK-backed upstream opener: real TCP sockets and UDP datagram sockets,
 * each protected (VPN bypass) before connecting, each with its own reader
 * thread pushing bytes back into the stack.
 */
class JdkSocketOpener(
    private val protect: (Any) -> Unit = {},
    private val connectTimeoutMs: Int = 10_000,
    private val soTimeoutMs: Int = 30_000,
) : SocketOpener {

    override fun open(flow: StackFlow, ip: String, port: Int, udp: Boolean, sink: UpstreamSink): UpstreamChannel? {
        return if (udp) openUdp(flow, ip, port, sink) else openTcp(flow, ip, port, sink)
    }

    private fun openTcp(flow: StackFlow, ip: String, port: Int, sink: UpstreamSink): UpstreamChannel? {
        return try {
            val socket = Socket()
            try {
                protect(socket)
            } catch (_: Exception) {
            }
            socket.tcpNoDelay = true
            socket.connect(InetSocketAddress(ip, port), connectTimeoutMs)
            try {
                socket.soTimeout = soTimeoutMs
            } catch (_: SocketException) {
            }
            TcpChannel(flow, socket, sink)
        } catch (_: IOException) {
            null
        }
    }

    private fun openUdp(flow: StackFlow, ip: String, port: Int, sink: UpstreamSink): UpstreamChannel? {
        return try {
            val socket = DatagramSocket()
            try {
                protect(socket)
            } catch (_: Exception) {
            }
            UdpChannel(flow, socket, InetSocketAddress(ip, port), sink)
        } catch (_: SocketException) {
            null
        }
    }

    private class TcpChannel(
        private val flow: StackFlow,
        private val socket: Socket,
        private val sink: UpstreamSink,
    ) : UpstreamChannel {
        init {
            Thread({
                val buf = ByteArray(16 * 1024)
                try {
                    val input = socket.getInputStream()
                    while (true) {
                        val n = input.read(buf)
                        if (n < 0) break
                        if (n > 0) sink.onUpstreamBytes(flow, buf.copyOf(n))
                    }
                } catch (_: IOException) {
                } finally {
                    sink.onUpstreamEof(flow)
                    close()
                }
            }, "upstream-tcp").apply {
                isDaemon = true
                start()
            }
        }

        override fun send(data: ByteArray): Boolean = try {
            socket.getOutputStream().apply {
                write(data)
                flush()
            }
            true
        } catch (_: IOException) {
            false
        }

        override fun close() {
            try {
                socket.close()
            } catch (_: IOException) {
            }
        }
    }

    private class UdpChannel(
        private val flow: StackFlow,
        private val socket: DatagramSocket,
        private val peer: InetSocketAddress,
        private val sink: UpstreamSink,
    ) : UpstreamChannel {
        init {
            Thread({
                val buf = ByteArray(65_507)
                try {
                    while (true) {
                        val packet = DatagramPacket(buf, buf.size)
                        socket.receive(packet)
                        if (packet.length > 0) {
                            sink.onUpstreamBytes(flow, buf.copyOf(packet.length))
                        }
                    }
                } catch (_: IOException) {
                }
            }, "upstream-udp").apply {
                isDaemon = true
                start()
            }
        }

        override fun send(data: ByteArray): Boolean = try {
            socket.send(DatagramPacket(data, data.size, peer))
            true
        } catch (_: IOException) {
            false
        }

        override fun close() {
            socket.close()
        }
    }
}
