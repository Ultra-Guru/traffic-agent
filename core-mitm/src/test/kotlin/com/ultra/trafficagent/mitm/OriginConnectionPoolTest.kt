package com.ultra.trafficagent.mitm

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.net.Socket

/** Fake socket for pool semantics: connection state is hand-driven. */
private class FakeSocket : Socket() {
    var fakeClosed = false

    override fun isConnected(): Boolean = true

    override fun isClosed(): Boolean = fakeClosed

    override fun close() {
        fakeClosed = true
    }
}

class OriginConnectionPoolTest {

    @Test
    fun `acquire connects when the queue is empty`() {
        var connects = 0
        val pool = OriginConnectionPool(
            connect = { _, _, _ -> connects++; FakeSocket() },
            clock = { 0L },
        )
        val lease = pool.acquire("https", "a.com", 443)
        assertFalse(lease.reused)
        assertEquals(1, connects)
        assertEquals(1L, pool.connectCount)
        assertEquals(0L, pool.reuseCount)
    }

    @Test
    fun `release then acquire reuses the same socket`() {
        val sockets = mutableListOf<FakeSocket>()
        val pool = OriginConnectionPool(
            connect = { _, _, _ -> FakeSocket().also { sockets.add(it) } },
            clock = { 0L },
        )
        val first = pool.acquire("https", "a.com", 443)
        pool.release(first, "https://a.com:443", reusable = true)
        assertEquals(1, pool.idleCount())

        val second = pool.acquire("https", "a.com", 443)
        assertTrue(second.reused)
        assertEquals(1L, pool.reuseCount)
        assertEquals(1L, pool.connectCount)
        assertEquals(0, pool.idleCount())
        // Same underlying socket instance.
        assertEquals(sockets[0], second.socket)
    }

    @Test
    fun `non-reusable release closes the socket`() {
        val pool = OriginConnectionPool(connect = { _, _, _ -> FakeSocket() }, clock = { 0L })
        val lease = pool.acquire("http", "a.com", 80)
        val socket = lease.socket as FakeSocket
        pool.release(lease, "http://a.com:80", reusable = false)
        assertTrue(socket.fakeClosed)
        assertEquals(0, pool.idleCount())
    }

    @Test
    fun `idle entries expire after the ttl`() {
        var now = 0L
        val pool = OriginConnectionPool(
            connect = { _, _, _ -> FakeSocket() },
            idleTtlMs = 10_000,
            clock = { now },
        )
        val lease = pool.acquire("https", "a.com", 443)
        pool.release(lease, "https://a.com:443", reusable = true)

        now = 5_000
        assertTrue(pool.acquire("https", "a.com", 443).reused)

        now = 20_000
        val expired = pool.acquire("https", "a.com", 443)
        assertFalse(expired.reused)
        assertEquals(2L, pool.connectCount)
    }

    @Test
    fun `closed sockets parked in the queue are discarded`() {
        val pool = OriginConnectionPool(connect = { _, _, _ -> FakeSocket() }, clock = { 0L })
        val lease = pool.acquire("https", "a.com", 443)
        val socket = lease.socket as FakeSocket
        pool.release(lease, "https://a.com:443", reusable = true)
        socket.fakeClosed = true  // dies while idle

        val next = pool.acquire("https", "a.com", 443)
        assertFalse(next.reused)
    }

    @Test
    fun `max idle per key is enforced`() {
        val pool = OriginConnectionPool(
            connect = { _, _, _ -> FakeSocket() },
            maxIdlePerKey = 1,
            clock = { 0L },
        )
        val a = pool.acquire("https", "a.com", 443)
        val b = pool.acquire("https", "a.com", 443)
        val socketA = a.socket as FakeSocket
        pool.release(a, "https://a.com:443", reusable = true)
        pool.release(b, "https://a.com:443", reusable = true)
        assertEquals(1, pool.idleCount())
        assertTrue(socketA.fakeClosed)  // oldest evicted
    }

    @Test
    fun `keys are isolated per scheme host and port`() {
        val pool = OriginConnectionPool(connect = { _, _, _ -> FakeSocket() }, clock = { 0L })
        pool.release(pool.acquire("https", "a.com", 443), "https://a.com:443", true)
        val other = pool.acquire("http", "a.com", 80)
        assertFalse(other.reused)
        val same = pool.acquire("https", "a.com", 443)
        assertTrue(same.reused)
    }

    @Test
    fun `closeAll drains the queue`() {
        val pool = OriginConnectionPool(connect = { _, _, _ -> FakeSocket() }, clock = { 0L })
        pool.release(pool.acquire("https", "a.com", 443), "https://a.com:443", true)
        pool.release(pool.acquire("https", "b.com", 443), "https://b.com:443", true)
        assertEquals(2, pool.idleCount())
        pool.closeAll()
        assertEquals(0, pool.idleCount())
    }
}
