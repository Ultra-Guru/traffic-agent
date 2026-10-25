package com.ultra.trafficagent.analysis

import com.ultra.trafficagent.capture.CapturedRequest
import com.ultra.trafficagent.capture.SessionCodec
import java.io.File
import java.io.FileOutputStream

/**
 * 基建三「存」: the live session pipeline behind the UI.
 *
 * A thread-safe ring of captured exchanges with optional JSONL persistence:
 * every session is appended to `sessions.jsonl`, rotated when it grows past
 * [rotateBytes] (older files stay on disk as sessions.1.jsonl etc.), keeping
 * at most [maxFiles] total files (rotated history + the active one), and the
 * active file is reloaded on startup so captures survive restarts.
 * Capacity bounds memory independent of disk.
 */
class SessionStore(
    private val capacity: Int = 2000,
    persistenceDir: File? = null,
    private val rotateBytes: Long = 4 * 1024 * 1024,
    private val maxFiles: Int = 4,
) {
    companion object {
        private const val FILE_NAME = "sessions.jsonl"
    }

    private val lock = Any()
    private val sessions = LinkedHashMap<Long, CapturedRequest>()
    private val dir: File? = persistenceDir?.apply { mkdirs() }
    private val activeFile: File? get() = dir?.resolve(FILE_NAME)

    init {
        load()
    }

    /** Adds a session; evicts the oldest beyond capacity. Returns the store size. */
    fun add(session: CapturedRequest): Int = synchronized(lock) {
        sessions[session.id] = session
        while (sessions.size > capacity) {
            val eldest = sessions.keys.firstOrNull() ?: break
            sessions.remove(eldest)
        }
        persist(session)
        sessions.size
    }

    fun get(id: Long): CapturedRequest? = synchronized(lock) { sessions[id] }

    /** Newest-first snapshot for the UI. */
    fun all(): List<CapturedRequest> = synchronized(lock) {
        sessions.values.toList().asReversed()
    }

    fun count(): Int = synchronized(lock) { sessions.size }

    /** Total up/down bytes across all sessions. */
    data class StoreStats(val count: Int, val bytesUp: Long, val bytesDown: Long)

    fun stats(): StoreStats = synchronized(lock) {
        StoreStats(
            count = sessions.size,
            bytesUp = sessions.values.sumOf { it.bytesUp },
            bytesDown = sessions.values.sumOf { it.bytesDown },
        )
    }

    fun clear() = synchronized(lock) {
        sessions.clear()
        activeFile?.delete()
        for (n in 1 until maxFiles) {
            dir?.resolve(FILE_NAME.replace(".jsonl", ".$n.jsonl"))?.delete()
        }
    }

    // ---------------- persistence ----------------

    private fun persist(session: CapturedRequest) {
        val file = activeFile ?: return
        try {
            if (file.length() > rotateBytes) {
                rotate()
            }
            FileOutputStream(file, true).use { out ->
                out.write(SessionCodec.encode(session).toByteArray(Charsets.UTF_8))
                out.write('\n'.code)
            }
        } catch (_: Exception) {
            // Persistence is best-effort; capture must never crash on I/O.
        }
    }

    private fun rotate() {
        val d = dir ?: return
        if (maxFiles <= 1) {
            // No history slots: drop the oversized active file outright.
            activeFile?.let { if (it.exists()) it.delete() }
            return
        }
        // Total files stay at maxFiles: (maxFiles - 1) rotated + 1 active.
        // Order matters: drop the oldest slot BEFORE shifting, otherwise the
        // just-shifted file would be deleted instead of the stale one.
        val oldest = d.resolve(indexedName(maxFiles - 1))
        if (oldest.exists()) oldest.delete()
        for (n in (maxFiles - 2) downTo 1) {
            val src = d.resolve(indexedName(n))
            val dst = d.resolve(indexedName(n + 1))
            if (src.exists()) {
                if (!src.renameTo(dst)) src.delete()
            }
        }
        val active = activeFile ?: return
        if (active.exists()) {
            if (!active.renameTo(d.resolve(indexedName(1)))) active.delete()
        }
    }

    private fun indexedName(n: Int): String = FILE_NAME.replace(".jsonl", ".$n.jsonl")

    private fun load() {
        val file = activeFile ?: return
        if (!file.exists()) return
        try {
            file.useLines { lines ->
                for (line in lines) {
                    val decoded = SessionCodec.decode(line) ?: continue
                    sessions[decoded.id] = decoded
                }
            }
            while (sessions.size > capacity) {
                sessions.remove(sessions.keys.first())
            }
        } catch (_: Exception) {
        }
    }
}
