package com.ultra.trafficagent.capture

/**
 * Kotlin surface of the C++ native engine (libtraffic_engine_jni.so).
 *
 * The library is loaded lazily so JVM unit tests of the capture module can
 * run on a desktop without the .so present.
 */
object NativeEngine {
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

    /** Creates an engine handle on the native heap. */
    external fun nativeInit(): Long

    /** Feeds one raw IPv4 packet; returns 0 on success, non-zero otherwise. */
    external fun nativeFeedPacket(handle: Long, packet: ByteArray, timestampMs: Long): Int

    /** Number of pending protocol-detection events. */
    external fun nativeEventCount(handle: Long): Int

    external fun nativeClearEvents(handle: Long)

    /**
     * Drains pending protocol-detection events as tab-separated lines
     * "kind\ttsMs\tsrcIp:port\tdstIp:port\ttext\tnumeric" (see
     * engineEventToLine in native-engine/src/export_lines.cpp).
     */
    external fun nativeTakeEvents(handle: Long): Array<String>?

    /**
     * Drains completed plain-HTTP exchanges as SessionCodec-compatible
     * JSONL lines (parse with [SessionCodec.decode]).
     */
    external fun nativeTakeExchanges(handle: Long): Array<String>?

    /** Frees the engine handle. */
    external fun nativeDestroy(handle: Long)
}
