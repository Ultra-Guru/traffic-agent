package com.ultra.trafficagent.mitm

import java.net.Socket
import java.util.concurrent.ConcurrentHashMap

/**
 * Keep-alive origin connection pool for [MitmProxyServer].
 *
 * Keyed by `scheme://host:port`; bounded idle queue per key with a TTL.
 * Reuse is best-effort: a borrowed socket that turns out stale simply gets
 * retried on a fresh connection by the caller (the proxy's IOException path),
 * so correctness never depends on liveness checks.
 *
 * The [connect] factory keeps the pool JVM-unit-testable: tests inject fake
 * sockets and a virtual clock; production passes the TLS-aware opener.
 */
class OriginConnectionPool(
    private val connect: (scheme: String, host: String, port: Int) -> Socket,
    private val maxIdlePerKey: Int = 4,
    private val idleTtlMs: Long = 30_000,
    private val clock: () -> Long = System::currentTimeMillis,
) {
    init {
        require(maxIdlePerKey >= 0) { "maxIdlePerKey must not be negative" }
        require(idleTtlMs > 0) { "idleTtlMs must be positive" }
    }

    /** A borrowed origin socket plus whether it came from the idle queue. */
    class Lease(val socket: Socket, val reused: Boolean)

    private class IdleEntry(val socket: Socket, val idleSince: Long)

    private val idle = ConcurrentHashMap<String, ArrayDeque<IdleEntry>>()
    private val lock = Any()

    @Volatile
    var reuseCount: Long = 0
        private set

    @Volatile
    var connectCount: Long = 0
        private set

    /**
     * Borrows a socket for [scheme]://[host]:[port]: a live idle one when
     * available (within [idleTtlMs] and [maxIdlePerKey]), otherwise a fresh
     * connection from [connect].
     */
    fun acquire(scheme: String, host: String, port: Int): Lease {
        val key = keyOf(scheme, host, port)
        synchronized(lock) {
            val queue = idle[key]
            while (queue != null && queue.isNotEmpty()) {
                val entry = queue.removeFirst()
                if (isUsable(entry.socket) && clock() - entry.idleSince <= idleTtlMs) {
                    reuseCount++
                    return Lease(entry.socket, reused = true)
                }
                closeQuietly(entry.socket)
            }
        }
        connectCount++
        return Lease(connect(scheme, host, port), reused = false)
    }

    /** Returns a socket to the idle queue for [key] (when [reusable] and
     *  still alive) or closes it. The caller always knows the origin it
     *  talked to, so the key is explicit — socket internals (layered TLS,
     *  resolved IPs) are never consulted for identity. */
    fun release(lease: Lease, key: String, reusable: Boolean) {
        if (!reusable || !isUsable(lease.socket)) {
            closeQuietly(lease.socket)
            return
        }
        synchronized(lock) {
            val queue = idle.getOrPut(key) { ArrayDeque() }
            while (queue.size >= maxIdlePerKey) {
                closeQuietly(queue.removeFirst().socket)
            }
            queue.addLast(IdleEntry(lease.socket, clock()))
        }
    }

    /** Number of sockets currently parked in the idle queues. */
    fun idleCount(): Int = synchronized(lock) { idle.values.sumOf { it.size } }

    /** Closes every pooled socket (server shutdown). */
    fun closeAll() {
        synchronized(lock) {
            for (queue in idle.values) {
                for (entry in queue) closeQuietly(entry.socket)
            }
            idle.clear()
        }
    }

    companion object {
        fun keyOf(scheme: String, host: String, port: Int): String = "$scheme://$host:$port"

        fun isUsable(socket: Socket): Boolean =
            socket.isConnected && !socket.isClosed

        fun closeQuietly(socket: Socket) {
            try {
                socket.close()
            } catch (_: Exception) {
            }
        }
    }
}
