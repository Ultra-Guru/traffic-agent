package com.ultra.trafficagent.capture

import java.io.File
import java.io.FileDescriptor
import java.io.FileInputStream
import java.io.IOException
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * Source of raw IPv4 packets arriving from a TUN interface (VPN mode).
 * One [read] returns one packet; -1 signals EOF.
 */
interface TunPacketSource {
    fun read(dst: ByteArray): Int
}

/**
 * TUN backed by a file descriptor. On Android pass
 * `parcelFileDescriptor.fileDescriptor`; on Linux `/dev/net/tun` or a
 * duplicated fd path both work via the [fdPath] constructor.
 */
class TunFileSource : TunPacketSource {
    private val input: FileInputStream

    constructor(fd: FileDescriptor) {
        input = FileInputStream(fd)
    }

    constructor(fdPath: String) {
        input = FileInputStream(File(fdPath))
    }

    override fun read(dst: ByteArray): Int = input.read(dst)

    fun close() {
        try {
            input.close()
        } catch (_: IOException) {
        }
    }
}

/** Counters exposed by [PacketPump]. */
data class PumpStats(
    val packetsRead: Long,
    val bytesRead: Long,
    val errors: Long,
    val running: Boolean,
    val startedAtMs: Long,
)

/**
 * Single-threaded pump that drains a [TunPacketSource] and forwards every
 * packet to [sink] with its arrival timestamp — the glue between a
 * VpnService TUN fd and the native engine's feedPacket (SPEC v2.1, roadmap
 * v0.2 data plane).
 */
class PacketPump(
    private val source: TunPacketSource,
    private val sink: (packet: ByteArray, timestampMs: Long) -> Unit,
) {
    private val running = AtomicBoolean(false)
    private val packetsRead = AtomicLong(0)
    private val bytesRead = AtomicLong(0)
    private val errors = AtomicLong(0)
    @Volatile
    private var startedAtMs: Long = 0

    private var thread: Thread? = null

    fun start() {
        if (!running.compareAndSet(false, true)) return
        startedAtMs = System.currentTimeMillis()
        thread = Thread(::loop, THREAD_NAME).apply {
            isDaemon = true
            start()
        }
    }

    fun stop() {
        running.set(false)
        thread?.interrupt()
    }

    val stats: PumpStats
        get() = PumpStats(
            packetsRead = packetsRead.get(),
            bytesRead = bytesRead.get(),
            errors = errors.get(),
            running = running.get(),
            startedAtMs = startedAtMs,
        )

    private fun loop() {
        val buf = ByteArray(BUFFER_SIZE)
        while (running.get()) {
            val n = try {
                source.read(buf)
            } catch (_: InterruptedException) {
                break
            } catch (_: IOException) {
                errors.incrementAndGet()
                break
            }
            if (n < 0) break
            if (n == 0) continue
            packetsRead.incrementAndGet()
            bytesRead.addAndGet(n.toLong())
            val packet = buf.copyOf(n)
            val ts = System.currentTimeMillis()
            try {
                sink(packet, ts)
            } catch (_: RuntimeException) {
                errors.incrementAndGet()
            }
        }
        running.set(false)
    }

    private companion object {
        const val THREAD_NAME = "traffic-pump"
        const val BUFFER_SIZE = 32 * 1024 // one TUN packet fits (GSO aside)
    }
}
