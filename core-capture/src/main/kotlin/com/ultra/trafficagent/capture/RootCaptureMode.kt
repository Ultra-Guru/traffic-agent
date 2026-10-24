package com.ultra.trafficagent.capture

/**
 * Builds the shell commands backing the ROOT_IPTABLES and ROOT_PCAP_FILE
 * capture modes (SPEC v2.1 "Root increment"). Every command is returned as a
 * plain string so tests can assert exact invocations before anything is run
 * through su(1) on a device.
 */
object RootCommandBuilder {

    /** Wraps a command for execution via the su shell. */
    fun suWrap(command: String): String = "su -c '$command'"

    /** Redirects all outbound TCP traffic to the local transparent proxy port. */
    fun redirectTcpToPort(port: Int): String =
        "iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-port $port"

    /** Removes the redirect installed by [redirectTcpToPort]. */
    fun removeRedirectTcpToPort(port: Int): String =
        "iptables -t nat -D OUTPUT -p tcp -j REDIRECT --to-port $port"

    fun redirectUdpToPort(port: Int): String =
        "iptables -t nat -A OUTPUT -p udp -j REDIRECT --to-port $port"

    fun removeRedirectUdpToPort(port: Int): String =
        "iptables -t nat -D OUTPUT -p udp -j REDIRECT --to-port $port"

    /** Captures all interfaces into a pcap file with the given snap length. */
    fun tcpdumpToFile(path: String, snaplen: Int = 65535): String =
        "tcpdump -i any -s $snaplen -w $path"

    /** Full setup sequence for the ROOT_IPTABLES mode. */
    fun rootIptablesSetup(port: Int): List<String> = listOf(
        suWrap(redirectTcpToPort(port)),
        suWrap(redirectUdpToPort(port)),
    )

    /** Teardown sequence for the ROOT_IPTABLES mode. */
    fun rootIptablesTeardown(port: Int): List<String> = listOf(
        suWrap(removeRedirectTcpToPort(port)),
        suWrap(removeRedirectUdpToPort(port)),
    )

    /** Start capture for the ROOT_PCAP_FILE mode. */
    fun rootPcapStart(path: String): String = suWrap(tcpdumpToFile(path))
}
