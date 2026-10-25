package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.Protocol
import com.ultra.trafficagent.capture.SessionCodec
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File

/** 基建三: session codec + ring store + JSONL persistence. */
class SessionStoreTest {

    private fun session(id: Long, host: String = "a.example.com", status: Int? = 200) = CapturedRequest(
        id = id,
        timestampMs = id * 1000,
        host = host,
        path = "/p/$id",
        method = "GET",
        status = status,
        requestHeaders = mapOf("Host" to host, "X-测试" to "值"),
        responseHeaders = mapOf("Content-Type" to "text/plain"),
        requestBody = "",
        responseBody = "body-$id",
        bytesUp = id,
        bytesDown = id * 10,
        protocol = Protocol.TLS,
        appUid = null,
    )

    @Test
    fun `codec round trips a session`() {
        val s = session(11)
        val line = SessionCodec.encode(s)
        assertFalse(line.contains('\n'))
        val back = SessionCodec.decode(line)!!
        assertEquals(s.id, back.id)
        assertEquals(s.timestampMs, back.timestampMs)
        assertEquals(s.host, back.host)
        assertEquals(s.path, back.path)
        assertEquals(s.method, back.method)
        assertEquals(s.status, back.status)
        assertEquals(s.requestHeaders, back.requestHeaders)
        assertEquals(s.responseHeaders, back.responseHeaders)
        assertEquals(s.responseBody, back.responseBody)
        assertEquals(s.bytesUp, back.bytesUp)
        assertEquals(s.bytesDown, back.bytesDown)
        assertEquals(s.protocol, back.protocol)
        assertNull(back.appUid)
    }

    @Test
    fun `codec escapes quotes newlines and unicode`() {
        val s = session(1).copy(
            host = "host\"quoted\"",
            responseBody = "line1\nline2\ttab",
        )
        val back = SessionCodec.decode(SessionCodec.encode(s))!!
        assertEquals("host\"quoted\"", back.host)
        assertEquals("line1\nline2\ttab", back.responseBody)
        assertTrue(SessionCodec.encode(s).contains("\\n"))
    }

    @Test
    fun `codec rejects malformed lines`() {
        assertNull(SessionCodec.decode(""))
        assertNull(SessionCodec.decode("not json"))
        assertNull(SessionCodec.decode("{\"host\":\"x\""))
    }

    @Test
    fun `codec tolerates null status and uid`() {
        val s = session(5, status = null)
        val back = SessionCodec.decode(SessionCodec.encode(s))!!
        assertNull(back.status)
        val withUid = s.copy(appUid = 10042)
        val back2 = SessionCodec.decode(SessionCodec.encode(withUid))!!
        assertEquals(10042, back2.appUid)
    }

    @Test
    fun `store evicts beyond capacity and lists newest first`() {
        val store = SessionStore(capacity = 3, persistenceDir = null)
        for (i in 1L..5L) store.add(session(i))
        assertEquals(3, store.count())
        val all = store.all()
        assertEquals(listOf(5L, 4L, 3L), all.map { it.id })
        assertNull(store.get(1))
        assertEquals(5L, store.get(5)!!.id)
    }

    @Test
    fun `store stats aggregate bytes`(@TempDir dir: File) {
        val store = SessionStore(capacity = 10, persistenceDir = dir)
        store.add(session(1))
        store.add(session(2))
        val stats = store.stats()
        assertEquals(2, stats.count)
        assertEquals(3L, stats.bytesUp)
        assertEquals(30L, stats.bytesDown)
    }

    @Test
    fun `store persists and reloads across instances`(@TempDir dir: File) {
        val first = SessionStore(capacity = 100, persistenceDir = dir)
        first.add(session(1, "persist.example.com"))
        first.add(session(2, "persist.example.com"))

        val second = SessionStore(capacity = 100, persistenceDir = dir)
        assertEquals(2, second.count())
        assertEquals("persist.example.com", second.get(1)!!.host)
        assertEquals("body-2", second.get(2)!!.responseBody)
    }

    @Test
    fun `store rotates oversized files`(@TempDir dir: File) {
        val store = SessionStore(
            capacity = 100,
            persistenceDir = dir,
            rotateBytes = 200,
            maxFiles = 3,
        )
        for (i in 1L..30L) store.add(session(i))
        assertTrue(dir.resolve("sessions.jsonl").exists())
        // Rotation keeps at most maxFiles historical files.
        val history = dir.listFiles { f -> f.name.startsWith("sessions.") }!!.map { it.name }
        assertTrue(history.size <= 3, "history was $history")

        val reloaded = SessionStore(capacity = 100, persistenceDir = dir)
        // The active file (a rotated recent one) still loads sessions.
        assertTrue(reloaded.count() > 0)
    }

    @Test
    fun `rotation shifts history by exact index names`(@TempDir dir: File) {
        val store = SessionStore(
            capacity = 100,
            persistenceDir = dir,
            rotateBytes = 200,
            maxFiles = 3,
        )
        for (i in 1L..30L) store.add(session(i))
        // Exactly: active + two history slots; index 1 holds the newest history.
        assertTrue(dir.resolve("sessions.1.jsonl").exists(), "sessions.1.jsonl must exist")
        assertTrue(dir.resolve("sessions.2.jsonl").exists(), "sessions.2.jsonl must exist")
        assertFalse(dir.resolve("sessions.3.jsonl").exists(), "third history slot must be dropped")
        val hist1 = dir.resolve("sessions.1.jsonl").readLines()
        val hist2 = dir.resolve("sessions.2.jsonl").readLines()
        assertTrue(hist1.isNotEmpty() && hist2.isNotEmpty())
        // Every line must decode: sessions were persisted through the codec.
        assertTrue(hist1.all { SessionCodec.decode(it) != null })
        // Index 1 must be strictly newer history than index 2 (rotation order).
        val maxId1 = hist1.maxOf { SessionCodec.decode(it)!!.id }
        val maxId2 = hist2.maxOf { SessionCodec.decode(it)!!.id }
        assertTrue(maxId1 > maxId2, "sessions.1 (max $maxId1) must be newer than sessions.2 (max $maxId2)")
    }

    @Test
    fun `add returns the growing store size`(@TempDir dir: File) {
        val store = SessionStore(capacity = 10, persistenceDir = dir)
        assertEquals(1, store.add(session(1)))
        assertEquals(2, store.add(session(2)))
        assertEquals(3, store.add(session(3)))
    }

    @Test
    fun `clear wipes rotated history files too`(@TempDir dir: File) {
        val store = SessionStore(
            capacity = 100,
            persistenceDir = dir,
            rotateBytes = 200,
            maxFiles = 4,
        )
        for (i in 1L..30L) store.add(session(i))
        assertTrue(dir.resolve("sessions.1.jsonl").exists(), "precondition: rotated files exist")
        assertTrue(dir.resolve("sessions.2.jsonl").exists())
        store.clear()
        assertEquals(0, store.count())
        assertEquals(0, dir.listFiles { f -> f.name.startsWith("sessions") }!!.size,
            "all rotated files must be removed")
    }

    @Test
    fun `reload trims disk content down to capacity`(@TempDir dir: File) {
        val writer = SessionStore(capacity = 100, persistenceDir = dir)
        for (i in 1L..10L) writer.add(session(i))
        val reloaded = SessionStore(capacity = 4, persistenceDir = dir)
        assertEquals(4, reloaded.count(), "load must trim to capacity")
        // The newest four survive; older ones were dropped.
        assertEquals(listOf(10L, 9L, 8L, 7L), reloaded.all().map { it.id })
        assertNull(reloaded.get(6))
    }

    @Test
    fun `store without persistence dir works purely in memory`() {
        val store = SessionStore(capacity = 5, persistenceDir = null)
        assertEquals(1, store.add(session(1)))
        assertEquals(2, store.add(session(2)))
        assertEquals(2, store.count())
        assertEquals(2L, store.get(2)!!.id)
        val stats = store.stats()
        assertEquals(2, stats.count)
        assertEquals(3L, stats.bytesUp)
        store.clear()
        assertEquals(0, store.count())
    }

    @Test
    fun `clear wipes memory and disk`(@TempDir dir: File) {
        val store = SessionStore(capacity = 10, persistenceDir = dir)
        store.add(session(1))
        store.add(session(2))
        store.clear()
        assertEquals(0, store.count())
        assertEquals(0, dir.listFiles { f -> f.name.startsWith("sessions") }!!.size)
    }
}
