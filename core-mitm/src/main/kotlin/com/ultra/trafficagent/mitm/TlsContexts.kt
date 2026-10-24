package com.ultra.trafficagent.mitm

import java.net.Socket
import java.security.KeyStore
import java.security.Principal
import java.security.PrivateKey
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.ConcurrentHashMap
import javax.net.ssl.ExtendedSSLSession
import javax.net.ssl.KeyManager
import javax.net.ssl.SNIHostName
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLEngine
import javax.net.ssl.SSLSession
import javax.net.ssl.SSLSocket
import javax.net.ssl.TrustManager
import javax.net.ssl.TrustManagerFactory
import javax.net.ssl.X509ExtendedKeyManager
import javax.net.ssl.X509TrustManager

/**
 * X509 key manager that serves a freshly issued leaf certificate for
 * whatever hostname the client asks for via SNI, backed by the shared
 * [CaCertificateAuthority]. This is what lets one SSLContext decrypt
 * traffic for any number of upstream hosts.
 */
class DynamicSniKeyManager(private val ca: CaCertificateAuthority) : X509ExtendedKeyManager() {

    /** alias -> issued material; mirrors what is registered in [keyStore]. */
    private val issued = ConcurrentHashMap<String, CaCertificateAuthority.X509AndKey>()

    /** Shared in-memory PKCS12 store the leaf entries are also registered in (alias = host). */
    private val keyStore = KeyStore.getInstance(KEYSTORE_TYPE).apply { load(null, null) }

    /** Last host we served; used when a client omits the SNI extension. */
    @Volatile
    private var fallbackHost: String = DEFAULT_HOST

    override fun getClientAliases(keyType: String?, issuers: Array<Principal>?): Array<String>? = null

    override fun chooseClientAlias(keyType: Array<String>?, issuers: Array<Principal>?, socket: Socket?): String? = null

    override fun chooseEngineClientAlias(keyType: Array<String>?, issuers: Array<Principal>?, engine: SSLEngine?): String? = null

    override fun getServerAliases(keyType: String?, issuers: Array<Principal>?): Array<String> =
        (issued.keys + fallbackHost).toTypedArray()

    override fun chooseServerAlias(keyType: String?, issuers: Array<Principal>?, socket: Socket?): String? =
        aliasFor(requestedHost((socket as? SSLSocket)?.handshakeSession) ?: fallbackHost)

    override fun chooseEngineServerAlias(keyType: String?, issuers: Array<Principal>?, engine: SSLEngine?): String? =
        aliasFor(requestedHost(engine?.handshakeSession) ?: engine?.requestedHostFromParameters() ?: fallbackHost)

    override fun getCertificateChain(alias: String?): Array<X509Certificate>? =
        alias?.let { host -> issued[host]?.let { entry -> arrayOf(entry.cert) } }

    override fun getPrivateKey(alias: String?): PrivateKey? = alias?.let { host -> issued[host]?.keyPair?.private }

    private fun aliasFor(host: String): String {
        issued[host]?.let { return host }
        val entry = ca.issueServerCertificate(host)
        issued[host] = entry
        synchronized(keyStore) {
            keyStore.setKeyEntry(host, entry.keyPair.private, ENTRY_PASSWORD, arrayOf(entry.cert))
        }
        fallbackHost = host
        return host
    }

    private fun requestedHost(session: SSLSession?): String? =
        (session as? ExtendedSSLSession)?.requestedServerNames
            ?.filterIsInstance<SNIHostName>()
            ?.firstOrNull()
            ?.asciiName

    private fun SSLEngine.requestedHostFromParameters(): String? =
        sslParameters.serverNames.filterIsInstance<SNIHostName>().firstOrNull()?.asciiName

    private companion object {
        private const val KEYSTORE_TYPE = "PKCS12"
        private const val DEFAULT_HOST = "localhost"
        private val ENTRY_PASSWORD = "traffic-agent-mitm".toCharArray()
    }
}

/** SSLContext factories for the two sides of the interception pipe. */
object TlsContexts {

    /** Server-facing context: signs leaf certificates on demand based on the client's SNI. */
    fun serverContext(ca: CaCertificateAuthority): SSLContext {
        val context = SSLContext.getInstance("TLS")
        context.init(arrayOf<KeyManager>(DynamicSniKeyManager(ca)), null, SecureRandom())
        return context
    }

    /**
     * Origin-facing context. With [trustAll] the context accepts every
     * origin certificate: a capture tool must keep intercepting endpoints
     * that use self-signed or pinning-mismatched certificates, and the
     * operator opted into that by enabling this flag. Never use such a
     * context in a production client — it defeats TLS authentication.
     */
    fun originContext(trustAll: Boolean): SSLContext {
        val context = SSLContext.getInstance("TLS")
        if (!trustAll) {
            val factory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm())
            factory.init(null as KeyStore?)
            context.init(null, factory.trustManagers, SecureRandom())
            return context
        }
        context.init(null, arrayOf<TrustManager>(TrustAllManager), SecureRandom())
        return context
    }

    private object TrustAllManager : X509TrustManager {
        override fun checkClientTrusted(chain: Array<X509Certificate>?, authType: String?) = Unit

        override fun checkServerTrusted(chain: Array<X509Certificate>?, authType: String?) = Unit

        override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
    }
}
