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

    /** Frees the engine handle. */
    external fun nativeDestroy(handle: Long)
}
