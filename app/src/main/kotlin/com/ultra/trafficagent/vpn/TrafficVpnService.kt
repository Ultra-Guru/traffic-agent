package com.ultra.trafficagent.vpn

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import com.ultra.trafficagent.MainActivity
import com.ultra.trafficagent.R
import com.ultra.trafficagent.capture.ForwardStackApi
import com.ultra.trafficagent.capture.JdkSocketOpener
import com.ultra.trafficagent.capture.NativeEngine
import com.ultra.trafficagent.capture.OrchestratorStats
import com.ultra.trafficagent.capture.PcapNgSessionFile
import com.ultra.trafficagent.capture.PcapSessionFile
import com.ultra.trafficagent.capture.StackFlow
import com.ultra.trafficagent.capture.StackFrames
import com.ultra.trafficagent.capture.TcpStackBridge
import com.ultra.trafficagent.capture.TunIo
import com.ultra.trafficagent.capture.VpnAnalysisTap
import com.ultra.trafficagent.capture.VpnOrchestrator
import com.ultra.trafficagent.mitm.CaCertificateAuthority
import com.ultra.trafficagent.mitm.CaptureListener
import com.ultra.trafficagent.mitm.ExchangeInterceptor
import com.ultra.trafficagent.mitm.MitmConfig
import com.ultra.trafficagent.mitm.MitmProxyServer
import com.ultra.trafficagent.mitm.MitmRewriteInterceptor
import com.ultra.trafficagent.mitm.MutableProxyExchange
import com.ultra.trafficagent.mitm.ProxyDecision
import com.ultra.trafficagent.mitm.ProxyExchangeMapper
import com.ultra.trafficagent.mitm.ServeMode
import com.ultra.trafficagent.mitm.SocketProtector
import com.ultra.trafficagent.session.CaptureSession
import com.ultra.trafficagent.session.CaptureState
import com.ultra.trafficagent.session.LiveStats
import com.ultra.trafficagent.session.RuleStore
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.IOException
import java.net.DatagramSocket
import java.net.Socket
import java.util.concurrent.atomic.AtomicBoolean

/**
 * The capture data plane as a special-use foreground service:
 *
 *  1. Builder.establish() hands us the TUN fd,
 *  2. every packet is fed to the C++ ForwardStack (forwarding + user-space
 *     TCP) and, as a passive tap, to the analysis Engine (JA3/SNI/DNS),
 *  3. HTTPS flows are redirected by the stack to the local MITM proxy
 *     (transparent TLS termination, SNI-driven leaf certificates),
 *  4. everything captured flows into [CaptureSession] for the UI.
 *
 * HttpCanary-style UX: one START/STOP toggle, an ongoing notification,
 * optional PCAP recording of every TUN packet.
 */
class TrafficVpnService : VpnService() {

    companion object {
        const val ACTION_START = "com.ultra.trafficagent.action.START"
        const val ACTION_STOP = "com.ultra.trafficagent.action.STOP"
        const val EXTRA_MITM = "mitm"
        const val EXTRA_RECORD_PCAP = "record_pcap"
        const val EXTRA_PCAPNG = "pcapng"

        private const val CHANNEL_ID = "traffic_agent_capture"
        private const val NOTIFICATION_ID = 1

        /** Must match StackConfig defaults in native-engine stack.h. */
        private const val MITM_TLS_PORT = 8843
        private const val MITM_PLAIN_PORT = 8808
        private const val VPN_ADDRESS = "10.111.0.2"
        private const val VPN_ROUTE = "0.0.0.0"
        private const val VPN_MTU = 1500
        private const val FALLBACK_DNS = "223.5.5.5"

        fun start(context: Context, mitm: Boolean, recordPcap: Boolean, pcapng: Boolean = false) {
            val intent = Intent(context, TrafficVpnService::class.java).apply {
                action = ACTION_START
                putExtra(EXTRA_MITM, mitm)
                putExtra(EXTRA_RECORD_PCAP, recordPcap)
                putExtra(EXTRA_PCAPNG, pcapng)
            }
            context.startForegroundService(intent)
        }

        fun stop(context: Context) {
            val intent = Intent(context, TrafficVpnService::class.java).apply { action = ACTION_STOP }
            context.startService(intent)
        }
    }

    private val running = AtomicBoolean(false)
    private var tun: ParcelFileDescriptor? = null
    private var orchestrator: VpnOrchestrator? = null
    private var mitmTls: MitmProxyServer? = null
    private var mitmPlain: MitmProxyServer? = null
    private var pcapFile: PacketRecorder? = null
    private var stackHandle = 0L
    private var engineHandle = 0L
    private var pcapPath: String? = null
    private var tapThread: Thread? = null
    private var mitmEnabled = false

    // ------------------------------------------------------------ lifecycle

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> {
                stopSelf()
                return START_NOT_STICKY
            }
            ACTION_START -> Unit
            else -> return START_NOT_STICKY
        }

        if (running.get()) return START_STICKY

        mitmEnabled = intent.getBooleanExtra(EXTRA_MITM, false)
        val recordPcap = intent.getBooleanExtra(EXTRA_RECORD_PCAP, false)
        val pcapng = intent.getBooleanExtra(EXTRA_PCAPNG, false)

        startForeground(NOTIFICATION_ID, buildNotification("Starting capture…"))
        CaptureSession.updateState(CaptureState.PREPARING)

        val started = try {
            startCapture(mitmEnabled, recordPcap, pcapng)
        } catch (e: Exception) {
            CaptureSession.stopped("Failed to start: ${e.message ?: e.javaClass.simpleName}")
            stopSelf()
            return START_NOT_STICKY
        }

        if (!started) {
            // establish() refused (VPN permission revoked or no TUN).
            CaptureSession.stopped("VPN permission denied")
            stopSelf()
            return START_NOT_STICKY
        }

        running.set(true)
        CaptureSession.updateState(CaptureState.ACTIVE)
        updateNotification("Capturing traffic")
        return START_STICKY
    }

    override fun onDestroy() {
        running.set(false)
        stopCapture()
        CaptureSession.updateState(CaptureState.IDLE)
        super.onDestroy()
    }

    override fun onRevoke() {
        // Android revoked the VPN (user dismissed from system settings).
        CaptureSession.stopped("VPN revoked by system")
        stopSelf()
    }

    // ------------------------------------------------------------- capture

    private fun startCapture(mitm: Boolean, recordPcap: Boolean, pcapng: Boolean): Boolean {
        val dns = resolveDns()

        // ---- native handles ----
        TcpStackBridge.ensureLoaded()
        NativeEngine.ensureLoaded()
        stackHandle = TcpStackBridge.nativeStackCreate(mitmEnabled = mitm, blockQuic = true, clientMss = 1300)
        engineHandle = NativeEngine.nativeInit()

        // ---- CA + MITM proxies ----
        if (mitm) {
            val ca = CaManager.loadOrCreate(filesDir)
            val protector = SocketProtector { socket -> protectSocket(socket) }
            val captureListener = CaptureListener { exchange ->
                CaptureSession.add(
                    ProxyExchangeMapper.toCapturedRequest(exchange, id = CaptureSession.nextId()),
                )
            }
            // Live rules: every request consults the newest published
            // registry snapshot, so Rules-screen edits apply immediately.
            val interceptors = listOf<ExchangeInterceptor>(LiveRuleInterceptor())
            mitmTls = MitmProxyServer(
                MITM_TLS_PORT, ca,
                config = MitmConfig(trustOriginAll = true, interceptors = interceptors),
                listener = captureListener,
                socketProtector = protector,
                mode = ServeMode.TRANSPARENT_TLS,
            ).also { it.start() }
            mitmPlain = MitmProxyServer(
                MITM_PLAIN_PORT, ca,
                config = MitmConfig(trustOriginAll = true, interceptors = interceptors),
                listener = captureListener,
                socketProtector = protector,
                mode = ServeMode.AUTO,
            ).also { it.start() }
        }

        // ---- PCAP / PCAPNG recording ----
        var pcap: PacketRecorder? = null
        if (recordPcap) {
            val dir = File(filesDir, "captures").apply { mkdirs() }
            val ext = if (pcapng) "pcapng" else "pcap"
            val target = File(dir, "capture-${System.currentTimeMillis()}.$ext")
            val file = if (pcapng) {
                PcapNgRecorder(PcapNgSessionFile(target.absolutePath), target.absolutePath)
            } else {
                ClassicPcapRecorder(PcapSessionFile(target.absolutePath), target.absolutePath)
            }
            if (file.start()) {
                pcap = file
                pcapPath = target.absolutePath
            }
        }
        pcapFile = pcap

        // ---- TUN ----
        val pfd = establishVpn(dns) ?: run {
            pcap?.close()
            return false
        }
        tun = pfd
        val tunIo = ParcelTunIo(pfd)

        // ---- analysis tap + pcap hook ----
        val tap = VpnAnalysisTap.fromEngineHandle(engineHandle)
        val observer: (ByteArray, Long) -> Unit = { packet, ts ->
            tap.feed(packet, ts)
            pcap?.record(packet, ts)
        }

        // ---- orchestrator ----
        val stack = StackBridgeAdapter(stackHandle)
        val opener = JdkSocketOpener(protect = { socket -> protectSocket(socket) })
        orchestrator = VpnOrchestrator(
            tun = tunIo,
            stack = stack,
            opener = opener,
            config = VpnOrchestrator.Config(
                dnsForward = dns,
                sweepIntervalMs = 5_000,
                onTunPacket = observer,
            ),
        )
        orchestrator?.start()

        // ---- tap drain loop: events + plain-HTTP exchanges -> session ----
        tapThread = Thread {
            while (running.get()) {
                try {
                    val drained = tap.drain()
                    CaptureSession.publishEvents(drained.events)
                    for (exchange in drained.exchanges) {
                        CaptureSession.add(exchange.copy(id = CaptureSession.nextId()))
                    }
                    pushStats(orchestrator?.stats, mitm, pcap)
                    Thread.sleep(500)
                } catch (_: InterruptedException) {
                    break
                } catch (_: RuntimeException) {
                    Thread.sleep(1_000)
                }
            }
        }.apply {
            isDaemon = true
            name = "vpn-tap-drain"
            start()
        }
        return true
    }

    private fun stopCapture() {
        try {
            tapThread?.interrupt()
        } catch (_: SecurityException) {
        }
        tapThread = null
        orchestrator?.stop()
        orchestrator = null
        mitmTls?.stop()
        mitmTls = null
        mitmPlain?.stop()
        mitmPlain = null
        pcapFile?.close()
        pcapFile = null
        pcapPath = null
        if (stackHandle != 0L) {
            try {
                TcpStackBridge.nativeStackDestroy(stackHandle)
            } catch (_: UnsatisfiedLinkError) {
            }
            stackHandle = 0L
        }
        if (engineHandle != 0L) {
            try {
                NativeEngine.nativeDestroy(engineHandle)
            } catch (_: UnsatisfiedLinkError) {
            }
            engineHandle = 0L
        }
        try {
            tun?.close()
        } catch (_: IOException) {
        }
        tun = null
    }

    // -------------------------------------------------------------- helpers

    private fun establishVpn(dns: String): ParcelFileDescriptor? {
        val builder = Builder()
            .setSession("Traffic Agent")
            .setMtu(VPN_MTU)
            .addAddress(VPN_ADDRESS, 32)
            .addDnsServer(dns)
            .addRoute(VPN_ROUTE, 0)
        return builder.establish()
    }

    /** The device's current resolver; falls back to a public one. */
    private fun resolveDns(): String {
        return try {
            val cm = getSystemService(CONNECTIVITY_SERVICE) as? ConnectivityManager
            val link = cm?.activeNetwork?.let { cm.getLinkProperties(it) }
            link?.dnsServers?.firstOrNull()?.hostAddress ?: FALLBACK_DNS
        } catch (_: Exception) {
            FALLBACK_DNS
        }
    }

    private fun protectSocket(socket: Any) {
        try {
            when (socket) {
                is Socket -> protect(socket)
                is DatagramSocket -> protect(socket)
            }
        } catch (_: Exception) {
        }
    }

    private fun pushStats(stats: OrchestratorStats?, mitm: Boolean, pcap: PacketRecorder?) {
        val repoStats = CaptureSession.repository.stats()
        CaptureSession.updateStats(
            LiveStats(
                requests = repoStats.requests,
                bytesUp = repoStats.bytesUp,
                bytesDown = repoStats.bytesDown,
                flowsActive = stats?.flowsActive ?: 0,
                packetsFromTun = stats?.packetsFromTun ?: 0,
                packetsToTun = stats?.packetsToTun ?: 0,
                mitmEnabled = mitm,
                recordingPcap = pcap != null,
                pcapPath = pcapPath,
            ),
        )
    }

    // -------------------------------------------------------- notification

    private fun createNotificationChannel() {
        val manager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Traffic capture",
            NotificationManager.IMPORTANCE_LOW,
        ).apply {
            description = "Ongoing VPN capture status"
            setShowBadge(false)
        }
        manager.createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification {
        val open = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val stop = PendingIntent.getService(
            this, 1,
            Intent(this, TrafficVpnService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        return Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_stat_capture)
            .setContentTitle("Traffic Agent")
            .setContentText(text)
            .setContentIntent(open)
            .setOngoing(true)
            .addAction(Notification.Action.Builder(null, "Stop", stop).build())
            .build()
    }

    private fun updateNotification(text: String) {
        val manager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, buildNotification(text))
    }
}

/**
 * Applies the newest published [RuleStore] snapshot to every exchange:
 * [MitmRewriteInterceptor] is stateless, so consulting a fresh instance
 * per phase lets Rules-screen edits apply to live traffic instantly.
 */
private class LiveRuleInterceptor : ExchangeInterceptor {
    override fun onRequest(ctx: MutableProxyExchange): ProxyDecision =
        MitmRewriteInterceptor(RuleStore.current()).onRequest(ctx)

    override fun onResponse(ctx: MutableProxyExchange) {
        MitmRewriteInterceptor(RuleStore.current()).onResponse(ctx)
    }
}

/** TunIo over a ParcelFileDescriptor: one read = one TUN packet. */
private class ParcelTunIo(private val pfd: ParcelFileDescriptor) : TunIo {
    private val input = FileInputStream(pfd.fileDescriptor)
    private val output = FileOutputStream(pfd.fileDescriptor)

    override fun readPacket(dst: ByteArray): Int = input.read(dst)

    @Synchronized
    override fun writePacket(packet: ByteArray): Boolean = try {
        output.write(packet)
        true
    } catch (_: IOException) {
        false
    }

    override fun close() {
        try {
            input.close()
        } catch (_: IOException) {
        }
        try {
            output.close()
        } catch (_: IOException) {
        }
    }
}

/** ForwardStackApi backed by the JNI bridge handle. */
private class StackBridgeAdapter(private val handle: Long) : ForwardStackApi {

    override fun onTunPacket(packet: ByteArray, tsMs: Long): List<ByteArray> =
        TcpStackBridge.nativeStackOnTunPacket(handle, packet, tsMs).toList()

    override fun onUpstreamData(flow: StackFlow, data: ByteArray, tsMs: Long): List<ByteArray> =
        TcpStackBridge.nativeStackOnUpstreamData(
            handle, flow.srcIp, flow.srcPort, flow.dstIp, flow.dstPort, data, tsMs,
        ).toList()

    override fun onUpstreamClosed(flow: StackFlow, tsMs: Long): List<ByteArray> =
        TcpStackBridge.nativeStackOnUpstreamClosed(
            handle, flow.srcIp, flow.srcPort, flow.dstIp, flow.dstPort, tsMs,
        ).toList()

    override fun sweep(nowMs: Long): List<ByteArray> =
        TcpStackBridge.nativeStackSweep(handle, nowMs).toList()

    override fun takeConnects() =
        TcpStackBridge.nativeStackTakeConnects(handle)?.let { StackFrames.decodeConnects(it) }
            ?: emptyList()

    override fun takeSends() =
        TcpStackBridge.nativeStackTakeSends(handle)?.let { StackFrames.decodeSends(it) }
            ?: emptyList()

    override fun takeCloses() =
        TcpStackBridge.nativeStackTakeCloses(handle)?.let { StackFrames.decodeCloses(it) }
            ?: emptyList()
}

/** CA persistence: one PKCS12 in filesDir, reused across restarts. */
object CaManager {
    private const val FILE_NAME = "traffic-agent-ca.p12"
    private const val PASSWORD = "traffic-agent-local-ca"

    fun loadOrCreate(filesDir: File): CaCertificateAuthority {
        val file = File(filesDir, FILE_NAME)
        if (file.exists()) {
            try {
                return CaCertificateAuthority.fromKeyStore(file, PASSWORD.toCharArray())
            } catch (_: Exception) {
                // Corrupt store: regenerate (user must reinstall the cert).
                file.delete()
            }
        }
        val ca = CaCertificateAuthority()
        ca.saveKeyStore(file, PASSWORD.toCharArray())
        return ca
    }

    /** Writes the CA certificate as a shareable .pem under filesDir/exports. */
    fun exportPem(filesDir: File): File {
        val dir = File(filesDir, "exports").apply { mkdirs() }
        val file = File(dir, "traffic-agent-ca.pem")
        file.writeText(loadOrCreate(filesDir).caCertificatePem())
        return file
    }
}
