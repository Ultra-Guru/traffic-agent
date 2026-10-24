package com.ultra.trafficagent.transform

/**
 * Weak-network simulation policy (HttpCanary's throttling, Reqable's
 * network simulator): per-direction latency, jitter, packet loss and
 * bandwidth caps.
 *
 * [seed] makes the loss/jitter sequence deterministic for tests and
 * reproducible debugging sessions.
 */
data class WeakNetworkPolicy(
    val upDelayMs: Long = 0,
    val downDelayMs: Long = 0,
    val jitterMs: Long = 0,
    val lossPercentUp: Int = 0,
    val lossPercentDown: Int = 0,
    /** Downlink cap in kilobits per second; 0 = unlimited. */
    val downKbps: Int = 0,
    /** Uplink cap in kilobits per second; 0 = unlimited. */
    val upKbps: Int = 0,
    val seed: Long? = null,
) {
    init {
        require(jitterMs >= 0) { "jitterMs must not be negative" }
        require(lossPercentUp in 0..100) { "lossPercentUp must be 0..100" }
        require(lossPercentDown in 0..100) { "lossPercentDown must be 0..100" }
        require(downKbps >= 0) { "downKbps must not be negative" }
        require(upKbps >= 0) { "upKbps must not be negative" }
    }
}

/** Outcome of handing a chunk to the simulated network. */
sealed class Delivery {
    /** Deliver after [afterMs] of injected waiting. */
    data class Deliver(val afterMs: Long) : Delivery()

    /** Simulated packet loss: drop silently. */
    object Drop : Delivery()
}

/**
 * Token-bucket bandwidth limiter: [reserve] answers how long [bytes] must
 * wait before they may be sent under the configured rate.
 */
class TokenBucket(
    bytesPerSecond: Long,
    capacityBytes: Long,
    private val clock: () -> Long = System::nanoTime,
) {
    init {
        require(bytesPerSecond >= 0) { "bytesPerSecond must not be negative" }
        require(capacityBytes >= 0) { "capacityBytes must not be negative" }
    }

    private val rateBytesPerSecond: Long = bytesPerSecond
    private var tokens: Double = capacityBytes.toDouble()
    private var lastRefillNs: Long = clock()
    private val nanosPerByte: Double = if (rateBytesPerSecond <= 0) 0.0 else 1_000_000_000.0 / rateBytesPerSecond

    /** Milliseconds [bytes] must wait; 0 when tokens are available now. */
    fun reserve(bytes: Long): Long {
        if (rateBytesPerSecond <= 0 || bytes <= 0) return 0
        synchronized(this) {
            refill()
            var deficit = bytes.toDouble() - tokens
            if (deficit <= 0) {
                tokens -= bytes
                return 0
            }
            // spend everything we have; the rest must wait
            tokens = 0.0
            return ((deficit * nanosPerByte) / 1_000_000.0).toLong().coerceAtLeast(0)
        }
    }

    private fun refill() {
        val now = clock()
        val elapsed = now - lastRefillNs
        if (elapsed > 0 && nanosPerByte > 0.0) {
            tokens = (tokens + elapsed / nanosPerByte).coerceAtMost(capacity.toDouble())
            lastRefillNs = now
        }
    }

    private val capacity: Double = capacityBytes.toDouble()
}

/**
 * Applies a [WeakNetworkPolicy] to exchange halves: feed the byte counts of
 * a request or response and receive the delivery verdict.
 */
class WeakNetworkSimulator(private val policy: WeakNetworkPolicy) {

    private val random = java.util.Random(policy.seed ?: DEFAULT_SEED)
    private val upBucket = TokenBucket(policy.upKbps * 1024L / 8, policy.upKbps * 1024L / 8)
    private val downBucket = TokenBucket(policy.downKbps * 1024L / 8, policy.downKbps * 1024L / 8)

    /** Verdict for an outgoing request of [bytes]. */
    fun onRequestReady(bytes: Long): Delivery = decide(
        baseDelayMs = policy.upDelayMs,
        lossPercent = policy.lossPercentUp,
        bucket = upBucket,
        bytes = bytes,
    )

    /** Verdict for an incoming response of [bytes]. */
    fun onResponseReady(bytes: Long): Delivery = decide(
        baseDelayMs = policy.downDelayMs,
        lossPercent = policy.lossPercentDown,
        bucket = downBucket,
        bytes = bytes,
    )

    private fun decide(baseDelayMs: Long, lossPercent: Int, bucket: TokenBucket, bytes: Long): Delivery {
        if (lossPercent > 0 && rollUnder(lossPercent)) return Delivery.Drop
        val jitter = nextJitter()
        val throttle = bucket.reserve(bytes)
        val total = baseDelayMs + jitter + throttle
        return Delivery.Deliver(total.coerceAtLeast(0))
    }

    private fun nextJitter(): Long = synchronized(this) {
        if (policy.jitterMs > 0) random.nextLong(policy.jitterMs + 1) else 0L
    }

    private fun rollUnder(percent: Int): Boolean = synchronized(this) {
        random.nextInt(100) < percent
    }

    private companion object {
        const val DEFAULT_SEED = 0xC0FFEEL
    }
}
