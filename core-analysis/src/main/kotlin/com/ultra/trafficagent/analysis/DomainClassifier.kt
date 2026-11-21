package com.ultra.trafficagent.analysis

/**
 * Domain classification: public-suffix extraction, ad/tracker blocklist
 * matching and a lightweight risk score used by the session dashboard.
 *
 * The embedded lists mirror common filter-list suffixes (AdGuard/hosts-style)
 * and are intentionally compact: on-device matching favours a small curated
 * set over shipping a full EasyList download.
 */
public object DomainClassifier {

    /** Coarse category for a hostname. */
    public enum class Category { NORMAL, ADS, TRACKER, CDN, METRICS, SOCIAL }

    /** Classification result with evidence. */
    public data class Result(
        val category: Category,
        val registrableDomain: String,
        val riskScore: Int,          // 0..100
        val matchedRule: String?,    // blocklist entry that fired
        val punycode: Boolean,       // hostname contains xn-- labels
        val suspiciousTld: Boolean,  // TLD on the high-abuse list
    )

    /** Ad-serving domains (suffix match on registrable domain or subdomain). */
    private val adDomains = hashSetOf(
        "doubleclick.net", "adnxs.com", "adservice.google.com", "googlesyndication.com",
        "googleadservices.com", "adcolony.com", "admob.com", "applovin.com",
        "unityads.unity3d.com", "vungle.com", "chartboost.com", "ironsource.com",
        "mopub.com", "inmobi.com", "facebookads.com", "ads-twitter.com",
        "advertising.com", "pubmatic.com", "rubiconproject.com", "criteo.com",
        "adform.net", "smartadserver.com", "adroll.com", "bidswitch.net",
        "openx.net", "casalemedia.com", "yieldmo.com", "sharethrough.com",
        "spotxchange.com", "teads.tv", "media.net", "taboola.com",
        "outbrain.com", "revcontent.com", "mgid.com", "zergnet.com",
    )

    /** Analytics / tracking endpoints. */
    private val trackerDomains = hashSetOf(
        "google-analytics.com", "analytics.google.com", "segment.io", "segment.com",
        "mixpanel.com", "amplitude.com", "heap.io", "heapanalytics.com",
        "branch.io", "appsflyer.com", "adjust.com", "kochava.com",
        "sentry.io", "bugsnag.com", "crashlytics.com", "firebase-settings.crashlytics.com",
        "newrelic.com", "nr-data.net", "dynatrace.com", "datadoghq.com",
        "statsig.com", "launchdarkly.com", "optimizely.com", "crazyegg.com",
        "hotjar.com", "fullstory.com", "quantserve.com", "scorecardresearch.com",
        "chartbeat.com", "moat.com", "doubleverify.com", "adsafeprotected.com",
    )

    /** CDN / cloud infrastructure fronts (informational, not risky). */
    private val cdnDomains = hashSetOf(
        "cloudflare.com", "cdn.cloudflare.net", "fastly.net", "akamaized.net",
        "akamaihd.net", "cloudfront.net", "amazonaws.com", "azureedge.net",
        "googleapis.com", "gstatic.com", "googleusercontent.com", "googlevideo.com",
        "jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com", "bing.net",
        "wpenginepowered.com", "edgekey.net", "edgesuite.net", "llnwd.net",
    )

    /** Metrics/telemetry endpoints distinct from product analytics. */
    private val metricsDomains = hashSetOf(
        "metrics.icloud.com", "ocsp.digicert.com", "ocsp.apple.com",
        "settings-win.data.microsoft.com", "v10.events.data.microsoft.com",
        "browser.pipe.aria.microsoft.com", "play.googleapis.com",
        "android.clients.google.com", "time.android.com", "time1.google.com",
    )

    /** Social platform API endpoints (grouping aid for the UI). */
    private val socialDomains = hashSetOf(
        "facebook.com", "fbcdn.net", "instagram.com", "threads.net",
        "twitter.com", "x.com", "twimg.com", "t.co",
        "tiktokcdn.com", "tiktokv.com", "snapchat.com", "pinterest.com",
        "linkedin.com", "reddit.com", "redd.it", "discord.com",
        "discordapp.net", "telegram.org", "whatsapp.com", "youtube.com",
    )

    /** TLDs with a statistically high abuse rate (phishing/spam). */
    private val suspiciousTlds = hashSetOf(
        "zip", "mov", "top", "xyz", "gq", "tk", "cf", "ml", "work",
        "click", "link", "country", "kim", "loan", "men", "party", "review",
        "stream", "surf", "quest", "cam", "bar", "rest", "cyou", "icu",
    )

    /** Common two-level public suffixes where the registrable part is deeper. */
    private val multiPartSuffixes = hashSetOf(
        "co.uk", "org.uk", "ac.uk", "gov.uk", "co.jp", "or.jp", "ne.jp",
        "com.au", "net.au", "org.au", "com.br", "com.cn", "com.tw",
        "co.nz", "co.in", "co.kr", "com.sg", "com.hk", "com.ar",
        "com.mx", "com.tr", "co.za", "com.ru", "net.cn", "org.cn",
    )

    /**
     * Extracts the registrable domain: the public suffix plus one label.
     * "a.b.example.co.uk" -> "example.co.uk"; "x.example.com" -> "example.com".
     */
    public fun registrableDomain(host: String): String {
        val normalized = host.trimEnd('.').lowercase()
        if (normalized.isEmpty()) return normalized
        if (isIpAddress(normalized)) return normalized
        val labels = normalized.split('.')
        if (labels.size <= 2) return normalized
        val lastTwo = labels.takeLast(2).joinToString(".")
        if (lastTwo in multiPartSuffixes && labels.size >= 3) {
            return labels.takeLast(3).joinToString(".")
        }
        return lastTwo
    }

    /** True when the string looks like an IPv4/IPv6 literal. */
    public fun isIpAddress(host: String): Boolean {
        val v4 = Regex("""^\d{1,3}(\.\d{1,3}){3}$""")
        if (v4.matches(host)) {
            return host.split('.').all { it.toInt() in 0..255 }
        }
        return host.contains(':') && Regex("""^[0-9a-f:]+$""").matches(host)
    }

    /** Classifies a hostname against the embedded lists. */
    public fun classify(host: String): Result {
        val normalized = host.trimEnd('.').lowercase()
        val registrable = registrableDomain(normalized)
        val punycode = normalized.split('.').any { it.startsWith("xn--") }
        val tld = normalized.substringAfterLast('.', "")
        val suspicious = tld in suspiciousTlds

        val (category, rule) = when {
            matchesList(normalized, registrable, adDomains) -> Category.ADS to
                firstMatch(normalized, registrable, adDomains)
            matchesList(normalized, registrable, trackerDomains) -> Category.TRACKER to
                firstMatch(normalized, registrable, trackerDomains)
            matchesList(normalized, registrable, metricsDomains) -> Category.METRICS to
                firstMatch(normalized, registrable, metricsDomains)
            matchesList(normalized, registrable, socialDomains) -> Category.SOCIAL to
                firstMatch(normalized, registrable, socialDomains)
            matchesList(normalized, registrable, cdnDomains) -> Category.CDN to
                firstMatch(normalized, registrable, cdnDomains)
            else -> Category.NORMAL to null
        }

        var risk = 0
        if (category == Category.ADS) risk += 50
        if (category == Category.TRACKER) risk += 40
        if (punycode) risk += 25
        if (suspicious) risk += 20
        // Long hostnames with deep subdomain chains are occasionally C2 fronts.
        val labelCount = normalized.split('.').size
        if (labelCount >= 6) risk += 10
        if (labelCount >= 9) risk += 15
        if (category == Category.CDN || category == Category.SOCIAL) risk = risk.coerceAtMost(20)

        return Result(
            category = category,
            registrableDomain = registrable,
            riskScore = risk.coerceIn(0, 100),
            matchedRule = rule,
            punycode = punycode,
            suspiciousTld = suspicious,
        )
    }

    private fun matchesList(host: String, registrable: String, list: Set<String>): Boolean {
        if (host in list) return true
        if (registrable in list) return true
        // Suffix match: "cdn.doubleclick.net" ends with ".doubleclick.net".
        return list.any { host.endsWith(".$it") }
    }

    private fun firstMatch(host: String, registrable: String, list: Set<String>): String? {
        if (host in list) return host
        if (registrable in list) return registrable
        return list.firstOrNull { host.endsWith(".$it") }
    }
}
