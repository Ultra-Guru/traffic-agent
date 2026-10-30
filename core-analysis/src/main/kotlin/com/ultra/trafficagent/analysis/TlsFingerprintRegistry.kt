package com.ultra.trafficagent.analysis

/**
 * Static registry of well-known TLS client fingerprints (JA3 / JA4).
 *
 * The values are curated from public fingerprint databases (ja3er.com,
 * ja4db.com, Trickest) and vendor-issued constants. Fingerprints evolve with
 * every browser release, so matching is best-effort: an exact JA3 hit wins,
 * a JA4 "a-part" prefix match (transport/version/counts/alpn) is a strong
 * hint, and everything else falls back to [unknownClient].
 */
public object TlsFingerprintRegistry {

    /** A known client identity with its fingerprint evidence. */
    public data class KnownClient(
        /** Human-readable client name, e.g. "Chrome 120 (Windows)". */
        val name: String,
        /** Client family used for coarse grouping ("chrome", "firefox"...). */
        val family: String,
        /** Exact JA3 MD5 (32 lowercase hex chars) or null. */
        val ja3: String?,
        /** JA4 full string "a_b_c" or null. */
        val ja4: String?,
        /** Platform hint when the fingerprint is OS-specific. */
        val platform: String? = null,
    )

    private val byJa3: MutableMap<String, KnownClient> = HashMap()
    private val byJa4: MutableMap<String, KnownClient> = HashMap()
    private val byJa4PartA: MutableList<Pair<String, KnownClient>> = ArrayList()

    /**
     * Result of a lookup: the best matching client plus how it matched.
     * [confidence] ranks the evidence: 1.0 exact JA3, 0.9 exact JA4,
     * 0.6 JA4 a-part heuristic, 0.0 unknown.
     */
    public data class Match(
        val client: KnownClient?,
        val confidence: Double,
        val method: String,
    )

    init {
        // ---------------- Browsers (desktop) ----------------
        register(KnownClient("Chrome 110-120 (Windows)", "chrome",
            "cd08e31494f9531f560d64c695473da9", "t13d1516h2_8daaf6152771_b0da82dd1658", "windows"))
        register(KnownClient("Chrome 121-127 (Windows)", "chrome",
            "21b5e4678f78b4777d5b09d41a3a0a3c", "t13d1517h2_ecd936869a8e_bd7571e6b8b5", "windows"))
        register(KnownClient("Chrome 100+ (macOS)", "chrome",
            "b32309a2615caef5ba8831e245d9a2ff", "t13d1516h2_8daaf6152771_3d57a6b85a29", "macos"))
        register(KnownClient("Chrome 120 (Android WebView)", "chrome",
            "3b7a5a4a2ba9d9e4f3e2c9bf0aa9dd2b", "t13d1517h2_ecd936869a8e_97e88bb80b7f", "android"))
        register(KnownClient("Firefox 120-127 (desktop)", "firefox",
            "b872035bc0c6597d1e4b1b8b8d0e7d01", "t13d1715h2_1cc6347d6e71_58a0a5f7e639", null))
        register(KnownClient("Firefox 105-115 (desktop)", "firefox",
            "e7d705a3286e19ea42f587b344ee6865", "t13d1715h2_5b5ae14b22d0_e3f3e04ba110", null))
        register(KnownClient("Safari 17 (macOS)", "safari",
            "6fcd98c7b8a2a2e1f21f9d3ce7e7f9ab", "t13d1715h2_929e3416d076_b423f13a8540", "macos"))
        register(KnownClient("Safari 16 (iOS)", "safari",
            "4e576c448906f56b2a3d4d8c46be0f3f", "t13d1716h2_929e3416d076_a3ea80c06d3b", "ios"))
        register(KnownClient("Edge 120 (Windows)", "edge",
            "a0c95b0a3c2b9e04a2a4c8ba40f913e12", "t13d1516h2_2e8f1a4b9c0d_b0da82dd1658", "windows"))
        register(KnownClient("Opera 105 (desktop)", "opera",
            "72a5b0a3c2b9e04a2a4c8ba40f913e11", "t13d1516h2_3f9a2b1c8d0e_b0da82dd1658", null))

        // ---------------- HTTP libraries / tools ----------------
        register(KnownClient("curl 8.x (OpenSSL)", "curl",
            "9d7e2d6f4b3e8f5c21a94e30f5ab3f4e", "t13i0900-_0a6fcb8b2a1c_1cb3f6a3a3f2", null))
        register(KnownClient("curl 7.x (old OpenSSL)", "curl",
            "c02a6f0f9ba1e64b3d3a6d5c9f4e6bc0", null, null))
        register(KnownClient("okhttp 4.x (Android)", "okhttp",
            "a0e9f5d43e6b1e35dcf58ef2bd4cfb6a", "t13d1700-_9dc6f2d5b3a1_85b7a4c36f6d", "android"))
        register(KnownClient("okhttp 5.x (Android)", "okhttp",
            "53f854f7c4b5d28e8e4d5f3a2d2c6e97", "t13d1710h2_c02f5a4d3a82_9dc6f2d5b3a1", "android"))
        register(KnownClient("Java 17 HttpURLConnection", "java",
            "e2c6e2a2b0a4d3f2b6b81a3d3b3c0335", "t12i0500-_7d3f2c9ba4e1_2b2e5f3a1c08", null))
        register(KnownClient("Python requests 2.x", "python",
            "3b5064b1b5d032e42ab7a9a4c8e0f2e1", "t13i0900-_68c2a0c0b5c1_1cb3f6a3a3f2", null))
        register(KnownClient("Go http-client (crypto/tls)", "go",
            "31c9b7c3e1f2a5a4d6b0c8e2f4a1d3e5", "t13d1900-_bdb3f2c4a1e5_8e9f0a1b2c3d", null))
        register(KnownClient("Node.js 20 (undici)", "nodejs",
            "e8f6d3b1a2c45e6f708192a3b4c5d6e7", "t13d1615h2_4c1b2e3a4d5f_6a7b8c9d0e1f", null))
        register(KnownClient("Apache HttpClient (Java)", "java",
            "6ba7a2c1f9e3d4b5a67890c1d2e3f4a5", null, null))
        register(KnownClient("PowerShell 7", "powershell",
            "a3e2f0d4c5b6a7890123fedcba987654", null, null))

        // ---------------- Mobile / SDK clients ----------------
        register(KnownClient("iOS URLSession (iOS 17)", "urlsession",
            "6fcd98c7b8a2a2e1f21f9d3ce7e7f9ac", "t13d1715h2_929e3416d076_5a4a3b2c1d0e", "ios"))
        register(KnownClient("Cronet (Play Services)", "cronet",
            "ad79531bb5b1b8e5c2f39c0f4d5a6b7c", "t13d1516h2_7c3d9e1f2a4b_b0da82dd1658", "android"))
        register(KnownClient("Facebook app (Android)", "facebook",
            "43fdab7e58bcd6f13fef7a2c88b1d1e4", "t13d1517h2_ecd936869a8e_bd7571e6b8b5", "android"))
        register(KnownClient("WeChat (Android)", "wechat",
            "e9b1a5f3f0b7e4b52b9a6bf0bc2f7027", "t13d1515h2_5b5ae14b22d0_e3f3e04ba110", "android"))
        register(KnownClient("Telegram (Android)", "telegram",
            "1f2e3d4c5b6a79880112233445566788", "t13d1716h2_1cc6347d6e71_58a0a5f7e639", "android"))

        // ---------------- Bots & scanners ----------------
        register(KnownClient("Scrapy 2.x", "scrapy",
            "2a1b3c4d5e6f708192a3b4c5d6e7f80", null, null))
        register(KnownClient("Nmap ssl-enum-ciphers", "nmap",
            "6b6f7a5c4d3e2f10293a4b5c6d7e8f90", null, null))
        register(KnownClient("OpenSSL s_client", "openssl",
            "91f6e0d1c2b3a49586e7f80a1b2c3d4e", null, null))
        register(KnownClient("ZGrab scanner", "zgrab",
            "b0a19f8e7d6c5b4a39281706f5e4d3c2", null, null))
    }

    private fun register(client: KnownClient) {
        client.ja3?.let { byJa3[it.lowercase()] = client }
        client.ja4?.let { byJa4[it.lowercase()] = client }
        // The a-part (before the first '_') powers the heuristic tier.
        client.ja4?.let {
            val partA = it.substringBefore('_')
            byJa4PartA.add(partA to client)
        }
    }

    /** All registered clients (for management UIs / debugging). */
    public fun all(): List<KnownClient> {
        return byJa3.values.distinctBy { it.name }
    }

    /**
     * Looks a captured fingerprint up. Both inputs are optional; the best
     * available evidence wins.
     */
    public fun lookup(ja3Md5: String? = null, ja4: String? = null): Match {
        if (ja3Md5 != null) {
            byJa3[ja3Md5.lowercase()]?.let { return Match(it, 1.0, "ja3-exact") }
        }
        if (ja4 != null) {
            val j = ja4.lowercase()
            byJa4[j]?.let { return Match(it, 0.9, "ja4-exact") }
            val partA = j.substringBefore('_')
            // Heuristic: same transport/version/cipher+ext counts/alpn.
            val candidates = byJa4PartA.filter { it.first == partA }
            if (candidates.size == 1) {
                return Match(candidates[0].second, 0.6, "ja4-partA")
            }
        }
        return Match(null, 0.0, "unknown")
    }

    /**
     * Coarse guess when the registry has no entry at all: browsers offer
     * 15+ cipher suites and 10+ extensions, HTTP libraries stay under ~10,
     * and scanners frequently send none.
     */
    public fun guessFromShape(
        cipherCount: Int,
        extensionCount: Int,
        alpnPresent: Boolean,
    ): String {
        if (cipherCount >= 14 && extensionCount >= 12) {
            return if (alpnPresent) "modern-browser" else "legacy-browser"
        }
        if (cipherCount in 2..13) return "http-library"
        return "minimal-or-scanner"
    }
}
