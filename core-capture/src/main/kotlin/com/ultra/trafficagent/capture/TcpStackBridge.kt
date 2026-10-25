package com.ultra.trafficagent.capture

import java.nio.ByteBuffer

/**
 * Kotlin surface of ForwardStack (基建一「通」) in libtraffic_engine_jni.so.
 *
 * The VpnService loop owns this bridge:
 *  1. TUN fd bytes -> [onTunPacket] -> packets to write back to the TUN,
 *  2. upstream socket threads -> [onUpstreamData]/[onUpstreamClosed],
 *  3. drain [takeConnects]/[takeSends]/[takeCloses] and act on them.
 *
 * The lazy-load pattern keeps JVM unit tests of the capture module runnable
 * on a desktop without the .so present.
 */
object TcpStackBridge {

    @Volatile
    private var loaded = false

    fun ensureLoaded() {
        if (!loaded) {
            synchronized(this) {
                if (!loaded) {
                    System.loadLibrary("traffic_engine_jni")
                    loaded = true
                }
            }
        }
    }

    /** Creates a ForwardStack on the native heap. */
    external fun nativeStackCreate(mitmEnabled: Boolean, blockQuic: Boolean, clientMss: Int): Long

    external fun nativeStackDestroy(handle: Long)

    /** Feeds one raw IPv4 packet from the TUN fd; returns packets to write back. */
    external fun nativeStackOnTunPacket(handle: Long, packet: ByteArray, tsMs: Long): Array<ByteArray>

    /** Upstream socket produced bytes for the given client flow. */
    external fun nativeStackOnUpstreamData(
        handle: Long, srcIp: Int, srcPort: Int, dstIp: Int, dstPort: Int,
        data: ByteArray, tsMs: Long,
    ): Array<ByteArray>

    /** Upstream socket hit EOF/error for the given client flow. */
    external fun nativeStackOnUpstreamClosed(
        handle: Long, srcIp: Int, srcPort: Int, dstIp: Int, dstPort: Int, tsMs: Long,
    ): Array<ByteArray>

    /** Drops idle flows; returns RST packets for them. */
    external fun nativeStackSweep(handle: Long, nowMs: Long): Array<ByteArray>

    /** Fixed-layout connect frame (see [StackFrames.decodeConnects]). */
    external fun nativeStackTakeConnects(handle: Long): ByteArray

    /** Fixed-layout pending-send frame (see [StackFrames.decodeSends]). */
    external fun nativeStackTakeSends(handle: Long): ByteArray

    /** Fixed-layout close frame (see [StackFrames.decodeCloses]). */
    external fun nativeStackTakeCloses(handle: Long): ByteArray

    external fun nativeStackFlowCount(handle: Long): Int
}

/** A client-side 4-tuple: the app on the device talking to some peer. */
data class StackFlow(
    val srcIp: Int,
    val srcPort: Int,
    val dstIp: Int,
    val dstPort: Int,
) {
    companion object {
        /** Formats a raw network-order IPv4 value as a dotted string. */
        fun formatIp(raw: Int): String =
            "${(raw ushr 24) and 0xFF}.${(raw ushr 16) and 0xFF}.${(raw ushr 8) and 0xFF}.${raw and 0xFF}"

        fun parseIp(text: String): Int {
            val parts = text.split(".")
            require(parts.size == 4) { "expected 4 octets: $text" }
            var v = 0
            for (p in parts) {
                val o = p.toInt()
                require(o in 0..255) { "octet out of range: $p" }
                v = (v shl 8) or o
            }
            return v
        }
    }

    val dstIpText: String get() = formatIp(dstIp)
}

/** The stack asks the socket layer to open one upstream connection. */
data class StackConnect(
    val original: StackFlow,
    val effectiveDstIp: Int,
    val effectiveDstPort: Int,
    val isUdp: Boolean,
)

/** The stack has client payload that must be written upstream. */
data class StackSend(
    val flow: StackFlow,
    val data: ByteArray,
)

/** The upstream socket for this flow should be closed. */
data class StackClose(val flow: StackFlow)

/**
 * Decoders for the fixed-layout binary frames produced by the JNI layer.
 * All integers are big-endian; frame layouts must match native-engine/src/jni.cpp.
 */
object StackFrames {

    // Connect: [1B isUdp][4B srcIp][2B srcPort][4B dstIp][2B dstPort][4B effDstIp][2B effDstPort]
    fun decodeConnects(frame: ByteArray): List<StackConnect> {
        val out = ArrayList<StackConnect>()
        val b = ByteBuffer.wrap(frame)
        while (b.remaining() >= 19) {
            val isUdp = b.get().toInt() != 0
            val srcIp = b.int
            val srcPort = b.short.toInt() and 0xFFFF
            val dstIp = b.int
            val dstPort = b.short.toInt() and 0xFFFF
            val effIp = b.int
            val effPort = b.short.toInt() and 0xFFFF
            out.add(
                StackConnect(
                    original = StackFlow(srcIp, srcPort, dstIp, dstPort),
                    effectiveDstIp = effIp,
                    effectiveDstPort = effPort,
                    isUdp = isUdp,
                ),
            )
        }
        return out
    }

    // Send: [4B srcIp][2B srcPort][4B dstIp][2B dstPort][4B len][len bytes]
    fun decodeSends(frame: ByteArray): List<StackSend> {
        val out = ArrayList<StackSend>()
        val b = ByteBuffer.wrap(frame)
        while (b.remaining() >= 16) {
            val srcIp = b.int
            val srcPort = b.short.toInt() and 0xFFFF
            val dstIp = b.int
            val dstPort = b.short.toInt() and 0xFFFF
            val len = b.int
            if (len < 0 || b.remaining() < len) break
            val data = ByteArray(len)
            b.get(data)
            out.add(StackSend(StackFlow(srcIp, srcPort, dstIp, dstPort), data))
        }
        return out
    }

    // Close: [4B srcIp][2B srcPort][4B dstIp][2B dstPort]
    fun decodeCloses(frame: ByteArray): List<StackClose> {
        val out = ArrayList<StackClose>()
        val b = ByteBuffer.wrap(frame)
        while (b.remaining() >= 12) {
            val srcIp = b.int
            val srcPort = b.short.toInt() and 0xFFFF
            val dstIp = b.int
            val dstPort = b.short.toInt() and 0xFFFF
            out.add(StackClose(StackFlow(srcIp, srcPort, dstIp, dstPort)))
        }
        return out
    }
}
