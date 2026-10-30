package com.ultra.trafficagent.capture

/**
 * Kotlin surface of PcapWriter in libtraffic_engine_jni.so (基建四「存」).
 *
 * The VpnService records every raw IPv4 packet it reads from the TUN fd
 * into a classic pcap file that Wireshark/tcpdump open directly — the
 * export format HttpCanary popularized on Android.
 *
 * Lazy-load keeps JVM unit tests of the capture module runnable without
 * the .so present.
 */
object PcapWriterBridge {

    /** LINKTYPE_RAW: one record = one raw IPv4 datagram (TUN output). */
    const val LINK_TYPE_RAW = 101

    /** LINKTYPE_ETHERNET: one record = one full Ethernet frame. */
    const val LINK_TYPE_ETHERNET = 1

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

    /** Opens (truncating) [path]; returns 0 on failure. */
    external fun nativeOpen(path: String, snaplen: Int, linkType: Int): Long

    /** Appends one packet record; 0 = ok, 1 = not open, 2 = write error, -1 = bad handle. */
    external fun nativeWritePacket(handle: Long, packet: ByteArray, timestampMs: Long): Int

    /** Flushes buffered output; same status codes as [nativeWritePacket]. */
    external fun nativeFlush(handle: Long): Int

    /** Frees the writer; idempotent. */
    external fun nativeClose(handle: Long)
}

/**
 * Session-scoped PCAP file. Feeds every TUN packet through the JNI writer
 * and closes cleanly on capture stop. Pure Kotlin wrapper — safe to
 * construct without the native library (writes become no-ops) so the UI
 * layer can offer "record to PCAP" as a plain toggle.
 */
class PcapSessionFile(private val path: String) : AutoCloseable {

    @Volatile
    private var handle: Long = 0

    @Volatile
    var packetsWritten: Long = 0
        private set

    @Synchronized
    fun start(snaplen: Int = 0xFFFF, linkType: Int = PcapWriterBridge.LINK_TYPE_RAW): Boolean {
        if (handle != 0L) return true
        return try {
            PcapWriterBridge.ensureLoaded()
            handle = PcapWriterBridge.nativeOpen(path, snaplen, linkType)
            handle != 0L
        } catch (_: UnsatisfiedLinkError) {
            false
        }
    }

    /** Records one raw packet; failures are swallowed (capture continuity wins). */
    @Synchronized
    fun record(packet: ByteArray, timestampMs: Long) {
        val h = handle
        if (h == 0L) return
        try {
            if (PcapWriterBridge.nativeWritePacket(h, packet, timestampMs) == 0) {
                packetsWritten++
            }
        } catch (_: UnsatisfiedLinkError) {
        }
    }

    @Synchronized
    fun flush() {
        val h = handle
        if (h == 0L) return
        try {
            PcapWriterBridge.nativeFlush(h)
        } catch (_: UnsatisfiedLinkError) {
        }
    }

    override fun close() {
        val h = handle
        handle = 0
        if (h == 0L) return
        try {
            PcapWriterBridge.nativeClose(h)
        } catch (_: UnsatisfiedLinkError) {
        }
    }
}
