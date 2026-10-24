package com.ultra.trafficagent.agent

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RiskGateTest {

    @Test
    fun `risk levels are ordered`() {
        assertTrue(RiskLevel.SAFE.rank < RiskLevel.CAUTION.rank)
        assertTrue(RiskLevel.CAUTION.rank < RiskLevel.DANGEROUS.rank)
        assertTrue(RiskLevel.DANGEROUS.rank < RiskLevel.CRITICAL.rank)
    }

    @Test
    fun `tool risk table mirrors python side`() {
        assertEquals(RiskLevel.SAFE, ToolRisk.of("list_requests"))
        assertEquals(RiskLevel.CAUTION, ToolRisk.of("modify_header"))
        assertEquals(RiskLevel.DANGEROUS, ToolRisk.of("modify_body"))
        assertEquals(RiskLevel.CRITICAL, ToolRisk.of("install_cert"))
        assertNull(ToolRisk.of("missing_tool"))
        assertEquals(15, ToolRisk.map.size)
    }

    @Test
    fun `unknown tool is denied without risk`() {
        val d = RiskGate().evaluate("explode")
        assertFalse(d.allowed)
        assertNull(d.risk)
        assertTrue(d.reason!!.contains("unknown tool"))
    }

    @Test
    fun `default policy allows safe and caution`() {
        val gate = RiskGate()
        assertTrue(gate.evaluate("read_request").allowed)
        assertTrue(gate.evaluate("remove_header").allowed)
    }

    @Test
    fun `default policy denies dangerous`() {
        val d = RiskGate().evaluate("replay_request")
        assertFalse(d.allowed)
        assertEquals(RiskLevel.DANGEROUS, d.risk)
        assertFalse(d.requiresApproval)
    }

    @Test
    fun `critical requires approval`() {
        val policy = RiskPolicy(maxLevel = RiskLevel.CRITICAL, requireApprovalFrom = RiskLevel.CRITICAL)
        val gate = RiskGate(policy)
        val denied = gate.evaluate("install_cert")
        assertFalse(denied.allowed)
        assertTrue(denied.requiresApproval)
        assertEquals(RiskLevel.CRITICAL, denied.risk)
        assertTrue(gate.evaluate("install_cert", approved = true).allowed)
    }

    @Test
    fun `read-only policy blocks caution tools`() {
        val gate = RiskGate(RiskPolicy(maxLevel = RiskLevel.SAFE))
        assertFalse(gate.evaluate("modify_header").allowed)
        assertTrue(gate.evaluate("stats_summary").allowed)
    }
}

class FakeAgentProcess(private val responses: MutableList<String>) : AgentProcess {
    val written = mutableListOf<String>()
    override fun writeLine(line: String) {
        written += line
    }

    override fun readLine(): String? = if (responses.isEmpty()) null else responses.removeAt(0)

    override val isAlive: Boolean get() = responses.isNotEmpty()

    override fun close() {}
}

class AgentBridgeTest {

    private fun bridge(vararg scripted: String): Pair<AgentBridge, FakeAgentProcess> {
        val fake = FakeAgentProcess(scripted.toMutableList())
        return AgentBridge({ fake }) to fake
    }

    @Test
    fun `encode escapes values`() {
        val line = AgentBridge.encode(mapOf("method" to "read", "q" to "a b&c"))
        assertEquals("method=read&q=a+b%26c", line)
    }

    @Test
    fun `decode splits pairs`() {
        val map = AgentBridge.decode("ok=1&count=3&payload=%7B%22a%22%3A1%7D")
        assertEquals("1", map["ok"])
        assertEquals("3", map["count"])
        assertEquals("""{"a":1}""", AgentBridge.decodeUrl(map["payload"]!!))
        assertTrue(AgentBridge.decode("").isEmpty())
    }

    @Test
    fun `successful call round trips`() {
        val (bridge, fake) = bridge("ok=1&payload=%5B%5D")
        val response = bridge.call("list_requests", mapOf("limit" to "2"))
        assertTrue(response.ok)
        assertEquals("[]", response.payload)
        assertEquals("method=list_requests&limit=2", fake.written.single())
    }

    @Test
    fun `approval flag is forwarded`() {
        val policy = RiskPolicy(maxLevel = RiskLevel.CRITICAL, requireApprovalFrom = RiskLevel.CRITICAL)
        val fake = FakeAgentProcess(mutableListOf("ok=1&result=done"))
        val bridge = AgentBridge({ fake }, RiskGate(policy))
        val response = bridge.call("install_cert", approved = true)
        assertTrue(response.ok)
        assertTrue(fake.written.single().endsWith("__approve=1"))
    }

    @Test
    fun `gate blocks dangerous tools before the wire`() {
        val (bridge, fake) = bridge("ok=1")
        val response = bridge.call("block_host", mapOf("host" to "ads.io"))
        assertFalse(response.ok)
        assertEquals("gate_denied", response.errorCode)
        assertEquals(RiskLevel.DANGEROUS, response.risk)
        // nothing reached the process
        assertTrue(fake.written.isEmpty())
    }

    @Test
    fun `unknown tool never reaches the process`() {
        val (bridge, fake) = bridge("ok=1")
        val response = bridge.call("nope_tool")
        assertFalse(response.ok)
        assertEquals("unknown_tool", response.errorCode)
        assertTrue(fake.written.isEmpty())
    }

    @Test
    fun `critical tool surfaces approval_required`() {
        val policy = RiskPolicy(maxLevel = RiskLevel.CRITICAL, requireApprovalFrom = RiskLevel.CRITICAL)
        val fake = FakeAgentProcess(mutableListOf())
        val bridge = AgentBridge({ fake }, RiskGate(policy))
        val response = bridge.call("install_cert")
        assertFalse(response.ok)
        assertEquals("approval_required", response.errorCode)
        assertEquals("critical", response.risk?.name?.lowercase())
    }

    @Test
    fun `agent exit is reported as process error`() {
        val (bridge, _) = bridge() // no scripted response -> readLine null
        val response = bridge.call("list_requests")
        assertFalse(response.ok)
        assertEquals("process_error", response.errorCode)
    }

    @Test
    fun `bridge error responses decode`() {
        val (bridge, _) = bridge("ok=0&error_code=unknown_tool&error=no+such+tool%3A+x")
        val response = bridge.call("list_requests")
        assertFalse(response.ok)
        assertEquals("unknown_tool", response.errorCode)
        assertEquals("no such tool: x", response.error) // auto-decoded
    }

    @Test
    fun `shutdown closes and exhausted process reports error`() {
        val fake = FakeAgentProcess(mutableListOf("ok=1"))
        val bridge = AgentBridge({ fake })
        assertTrue(bridge.call("list_requests").ok)
        bridge.shutdown()
        // factory would hand out a fresh process in production; this fake is
        // exhausted, so the next call surfaces a process error
        val response = bridge.call("list_requests")
        assertFalse(response.ok)
        assertEquals("process_error", response.errorCode)
    }
}
