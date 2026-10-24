package com.ultra.trafficagent.analysis

/**
 * Thread-safe topic-based event bus connecting the capture pipeline to
 * analyzers, the UI and the agent control plane (SPEC v2.1 L2/L3).
 */
class Subscription internal constructor(val id: Long, val topic: String, private val bus: EventBus) {
    /** Cancels this subscription; safe to call twice. */
    fun cancel() = bus.unsubscribe(this)
}

class EventBus {

    private val lock = Any()
    private val subscribers = LinkedHashMap<String, MutableList<Pair<Subscription, (Any) -> Unit>>>()
    private var nextId = 0L

    @Volatile var publishedCount: Long = 0
        private set

    @Volatile var deadEventCount: Long = 0
        private set

    /** Subscribes [handler] to [topic]; returns a cancellable subscription. */
    fun subscribe(topic: String, handler: (Any) -> Unit): Subscription {
        require(topic.isNotEmpty()) { "topic must not be empty" }
        synchronized(lock) {
            val sub = Subscription(nextId++, topic, this)
            subscribers.getOrPut(topic) { mutableListOf() }.add(sub to handler)
            return sub
        }
    }

    /** Removes a subscription; unknown subscriptions are ignored. */
    fun unsubscribe(sub: Subscription) {
        synchronized(lock) {
            val list = subscribers[sub.topic] ?: return
            val index = list.indexOfFirst { it.first === sub }
            if (index >= 0) list.removeAt(index)
        }
    }

    /** Publishes [event] to every subscriber of [topic]. */
    fun publish(topic: String, event: Any) {
        val handlers: List<(Any) -> Unit>
        synchronized(lock) {
            publishedCount++
            handlers = subscribers[topic]?.map { it.second } ?: emptyList()
        }
        if (handlers.isEmpty()) {
            deadEventCount++
            return
        }
        for (h in handlers) h(event)
    }

    fun subscriberCount(topic: String): Int = synchronized(lock) {
        subscribers[topic]?.size ?: 0
    }

    fun topicCount(): Int = synchronized(lock) { subscribers.size }
}

/** Canonical topics used across the app. */
object Topics {
    const val CAPTURED = "capture.captured"
    const val REWRITE_APPLIED = "transform.rewrite-applied"
    const val BREAKPOINT_HIT = "transform.breakpoint-hit"
    const val AGENT_TOOL_CALL = "agent.tool-call"
    const val AGENT_AUDIT = "agent.audit"
}
