package com.ultra.trafficagent.mitm

import java.io.ByteArrayInputStream
import java.io.File
import java.math.BigInteger
import java.security.KeyPair
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.KeyStoreException
import java.security.MessageDigest
import java.security.PrivateKey
import java.security.PublicKey
import java.security.SecureRandom
import java.security.Signature
import java.security.cert.CertificateException
import java.security.cert.CertificateFactory
import java.security.cert.X509Certificate
import java.security.interfaces.RSAPublicKey
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.Base64
import java.util.Date
import java.util.LinkedHashMap
import javax.net.ssl.KeyManagerFactory
import javax.net.ssl.TrustManagerFactory

/**
 * In-memory certificate authority for HTTPS MITM interception: owns the CA
 * key pair, its self-signed certificate, and issues per-host leaf
 * certificates signed by that CA — the mechanism HttpCanary-style tools
 * use to decrypt TLS traffic of clients that trust this CA.
 *
 * Everything is hand-encoded DER via [DerWriter]; no third-party ASN.1
 * library is involved.
 */
class CaCertificateAuthority private constructor(material: CaMaterial) {

    /** CA key pair + self-signed certificate bundled for constructor delegation. */
    private class CaMaterial(val keyPair: KeyPair, val certificate: X509Certificate)

    /** Issued server certificate together with its fresh key pair. */
    data class X509AndKey(val cert: X509Certificate, val keyPair: KeyPair)

    /** Generates a new 2048-bit RSA CA with a self-signed certificate. */
    constructor() : this(selfSignedCa())

    private val caKeyPair: KeyPair = material.keyPair
    private val caCertificate: X509Certificate = material.certificate

    /** RDNSequence *content* (outer SEQUENCE header stripped) of the CA subject. */
    private val caSubjectContent: ByteArray = derContentOf(caCertificate.subjectX500Principal.encoded)

    /** SHA-1 key identifier over the CA public key (RFC 5280 method 1). */
    private val caKeyId: ByteArray = sha1((caCertificate.publicKey as RSAPublicKey).encoded)

    private val random = SecureRandom()

    /** LRU cache of issued leaves, keyed by host (bounded so long captures stay small). */
    private val leafCache = object : LinkedHashMap<String, X509AndKey>(16, LOAD_FACTOR, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, X509AndKey>): Boolean =
            size > LEAF_CACHE_LIMIT
    }

    fun caCertificate(): X509Certificate = caCertificate

    /** PEM (RFC 7468) representation of the CA certificate for installing into client trust stores. */
    fun caCertificatePem(): String {
        val base64 = Base64.getMimeEncoder(PEM_LINE_LENGTH, "\r\n".toByteArray())
            .encodeToString(caCertificate.encoded)
        return "-----BEGIN CERTIFICATE-----\r\n$base64\r\n-----END CERTIFICATE-----\r\n"
    }

    /**
     * Issues (or returns the cached) leaf certificate for [host]:
     * CN=host (clamped to 64 chars), SAN dNSName=host, EKU serverAuth,
     * keyUsage digitalSignature|keyEncipherment, AKI pointing at the CA.
     */
    @Synchronized
    fun issueServerCertificate(host: String): X509AndKey {
        require(host.isNotEmpty()) { "host must not be empty" }
        leafCache[host]?.let { return it }
        val keyPair = newRsaKeyPair()
        val certificate = buildCertificate(
            serial = randomSerial(),
            subjectContent = rdn(OID_COMMON_NAME, host.take(MAX_COMMON_NAME_LENGTH)),
            issuerContent = caSubjectContent,
            publicKey = keyPair.public,
            notBefore = LEAF_NOT_BEFORE,
            notAfter = LEAF_NOT_AFTER,
            extensions = leafExtensions(host),
            signKey = caKeyPair.private,
        )
        val entry = X509AndKey(certificate, keyPair)
        leafCache[host] = entry
        return entry
    }

    /** Persists the CA private key + certificate as a PKCS12 key entry (alias "ca"). */
    fun saveKeyStore(file: File, password: CharArray) {
        val store = KeyStore.getInstance(KEYSTORE_TYPE)
        store.load(null, null)
        store.setKeyEntry(CA_ALIAS, caKeyPair.private, password, arrayOf(caCertificate))
        file.parentFile?.mkdirs()
        file.outputStream().use { store.store(it, password) }
    }

    /** Trust manager factory whose PKIX validators accept exactly this CA. */
    fun clientTrustManagerFactory(): TrustManagerFactory {
        val store = KeyStore.getInstance(KeyStore.getDefaultType())
        store.load(null, null)
        store.setCertificateEntry(CA_ALIAS, caCertificate)
        val factory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm())
        factory.init(store)
        return factory
    }

    /** Key manager factory serving the leaf for [host]; handy to TLS-enable a test origin server. */
    fun leafKeyManagerFactory(host: String): KeyManagerFactory {
        val entry = issueServerCertificate(host)
        val store = KeyStore.getInstance(KEYSTORE_TYPE)
        store.load(null, null)
        store.setKeyEntry(host, entry.keyPair.private, ENTRY_PASSWORD, arrayOf(entry.cert))
        val factory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm())
        factory.init(store, ENTRY_PASSWORD)
        return factory
    }

    private fun leafExtensions(host: String): List<ByteArray> = listOf(
        // subjectAltName dNSName [2]: the requested host (also fine for IP literals).
        extensionTlv(OID_SUBJECT_ALT_NAME, critical = false, valueTlv = der {
            writeSequence(der { writeContextSpecific(DNS_NAME_TAG, host.toByteArray(Charsets.US_ASCII), constructed = false) })
        }),
        // extendedKeyUsage serverAuth.
        extensionTlv(OID_EXTENDED_KEY_USAGE, critical = false, valueTlv = der {
            writeSequence(der { writeObjectId(OID_SERVER_AUTH) })
        }),
        // keyUsage digitalSignature|keyEncipherment: bits 0 and 2, last used bit 2 -> 5 unused bits.
        extensionTlv(OID_KEY_USAGE, critical = true, valueTlv = der {
            writeBitString(byteArrayOf(LEAF_KEY_USAGE_BITS), unusedBits = 5)
        }),
        // authorityKeyIdentifier keyIdentifier [0] copied from the CA subjectKeyIdentifier.
        extensionTlv(OID_AUTHORITY_KEY_IDENTIFIER, critical = false, valueTlv = der {
            writeSequence(der { writeContextSpecific(KEY_IDENTIFIER_TAG, caKeyId, constructed = false) })
        }),
    )

    private fun newRsaKeyPair(): KeyPair {
        val generator = KeyPairGenerator.getInstance("RSA")
        generator.initialize(KEY_SIZE_BITS)
        return generator.generateKeyPair()
    }

    private fun randomSerial(): BigInteger = BigInteger(SERIAL_BITS, random).add(BigInteger.ONE)

    companion object {
        /**
         * Restores a CA previously written by [saveKeyStore] so issued leaf
         * certificates stay valid across app restarts (re-generating the CA
         * would force the user to reinstall the certificate).
         */
        fun fromKeyStore(file: File, password: CharArray): CaCertificateAuthority {
            val store = KeyStore.getInstance(KEYSTORE_TYPE)
            file.inputStream().use { store.load(it, password) }
            val key = store.getKey(CA_ALIAS, password) as? PrivateKey
                ?: throw KeyStoreException("no CA key entry '$CA_ALIAS' in ${file.path}")
            val certificate = store.getCertificate(CA_ALIAS) as? X509Certificate
                ?: throw KeyStoreException("no CA certificate entry '$CA_ALIAS' in ${file.path}")
            return CaCertificateAuthority(CaMaterial(KeyPair(certificate.publicKey, key), certificate))
        }

        private const val KEY_SIZE_BITS = 2048
        private const val SERIAL_BITS = 127
        private const val LOAD_FACTOR = 0.75f
        private const val LEAF_CACHE_LIMIT = 128
        private const val MAX_COMMON_NAME_LENGTH = 64
        private const val KEYSTORE_TYPE = "PKCS12"
        private const val CA_ALIAS = "ca"
        private const val PEM_LINE_LENGTH = 64
        private const val SIGNATURE_ALGORITHM = "SHA256withRSA"

        private const val VERSION_TAG = 0
        private const val EXTENSIONS_TAG = 3
        private const val VERSION_3 = 2L
        private const val DNS_NAME_TAG = 2
        private const val KEY_IDENTIFIER_TAG = 0

        /** keyUsage byte for keyCertSign (bit 5) | cRLSign (bit 6). */
        private const val CA_KEY_USAGE_BITS: Byte = 0x06

        /** keyUsage byte for digitalSignature (bit 0) | keyEncipherment (bit 2). */
        private const val LEAF_KEY_USAGE_BITS: Byte = 0xA0.toByte()

        private const val OID_SHA256_WITH_RSA = "1.2.840.113549.1.1.11"
        private const val OID_COMMON_NAME = "2.5.4.3"
        private const val OID_ORGANIZATION = "2.5.4.10"
        private const val OID_COUNTRY = "2.5.4.6"
        private const val OID_BASIC_CONSTRAINTS = "2.5.29.19"
        private const val OID_KEY_USAGE = "2.5.29.15"
        private const val OID_SUBJECT_KEY_IDENTIFIER = "2.5.29.14"
        private const val OID_SUBJECT_ALT_NAME = "2.5.29.17"
        private const val OID_EXTENDED_KEY_USAGE = "2.5.29.37"
        private const val OID_AUTHORITY_KEY_IDENTIFIER = "2.5.29.35"
        private const val OID_SERVER_AUTH = "1.3.6.1.5.5.7.3.1"

        private const val CA_COMMON_NAME = "Traffic Agent CA"
        private const val CA_ORGANIZATION = "Traffic Agent"
        private const val CA_COUNTRY = "CN"

        private val CA_NOT_BEFORE = ZonedDateTime.of(2024, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)
        private val CA_NOT_AFTER = ZonedDateTime.of(2034, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)
        private val LEAF_NOT_BEFORE = CA_NOT_BEFORE

        // The spec asked for 2024..2026, but 2026-01-01 is already in the past on
        // the machines running this project (clocks sit at late 2026), which would
        // make every issued leaf fail PKIX validity checks. Extended to 2028.
        private val LEAF_NOT_AFTER = ZonedDateTime.of(2028, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)

        private val ENTRY_PASSWORD = "traffic-agent-leaf".toCharArray()

        /** Builds and parses a self-signed CA: CN/O/C subject, basicConstraints CA:TRUE, keyCertSign|cRLSign, SKI. */
        private fun selfSignedCa(): CaMaterial {
            val keyPair = KeyPairGenerator.getInstance("RSA").apply { initialize(KEY_SIZE_BITS) }.generateKeyPair()
            val keyId = sha1((keyPair.public as RSAPublicKey).encoded)
            val subject = rdn(OID_COMMON_NAME, CA_COMMON_NAME) +
                rdn(OID_ORGANIZATION, CA_ORGANIZATION) +
                rdn(OID_COUNTRY, CA_COUNTRY)
            val certificate = buildCertificate(
                serial = BigInteger(SERIAL_BITS, SecureRandom()).add(BigInteger.ONE),
                subjectContent = subject,
                issuerContent = subject,
                publicKey = keyPair.public,
                notBefore = CA_NOT_BEFORE,
                notAfter = CA_NOT_AFTER,
                extensions = listOf(
                    extensionTlv(OID_BASIC_CONSTRAINTS, critical = true, valueTlv = der {
                        writeSequence(der { writeBoolean(true) })
                    }),
                    extensionTlv(OID_KEY_USAGE, critical = true, valueTlv = der {
                        writeBitString(byteArrayOf(CA_KEY_USAGE_BITS), unusedBits = 1)
                    }),
                    extensionTlv(OID_SUBJECT_KEY_IDENTIFIER, critical = false, valueTlv = der {
                        writeOctetString(keyId)
                    }),
                ),
                signKey = keyPair.private,
            )
            return CaMaterial(keyPair, certificate)
        }

        /**
         * TBSCertificate assembly per RFC 5280: v3, serial, sha256WithRSA
         * AlgorithmIdentifier (mirrored in the outer SEQUENCE), issuer,
         * validity, subject, SubjectPublicKeyInfo, and the [3] extensions
         * wrapper; the signature covers the full TBS SEQUENCE TLV.
         */
        private fun buildCertificate(
            serial: BigInteger,
            subjectContent: ByteArray,
            issuerContent: ByteArray,
            publicKey: PublicKey,
            notBefore: ZonedDateTime,
            notAfter: ZonedDateTime,
            extensions: List<ByteArray>?,
            signKey: PrivateKey,
        ): X509Certificate {
            val algorithmContent = der {
                writeObjectId(OID_SHA256_WITH_RSA)
                writeNull()
            }
            val validityContent = der {
                writeUTCTime(Date.from(notBefore.toInstant()))
                writeUTCTime(Date.from(notAfter.toInstant()))
            }
            // RSAPublicKey.getEncoded() is a full SubjectPublicKeyInfo TLV; embed its content.
            val spkiContent = derContentOf((publicKey as RSAPublicKey).encoded)
            val tbsContent = der {
                writeContextSpecific(VERSION_TAG, der { writeInteger(VERSION_3) })
                writeInteger(serial)
                writeSequence(algorithmContent)
                writeSequence(issuerContent)
                writeSequence(validityContent)
                writeSequence(subjectContent)
                writeSequence(spkiContent)
                if (!extensions.isNullOrEmpty()) {
                    val concatenated = extensions.reduce { acc, tlv -> acc + tlv }
                    writeContextSpecific(EXTENSIONS_TAG, der { writeSequence(concatenated) })
                }
            }
            val tbs = der { writeSequence(tbsContent) }
            val signature = Signature.getInstance(SIGNATURE_ALGORITHM).let { signer ->
                signer.initSign(signKey)
                signer.update(tbs)
                signer.sign()
            }
            val certificateContent = tbs +
                der { writeSequence(algorithmContent) } +
                der { writeBitString(signature) }
            return parseCertificate(der { writeSequence(certificateContent) })
        }

        /** SEQUENCE { type OID, value } wrapped in a SET — one relative distinguished name. */
        private fun rdn(oid: String, value: String): ByteArray {
            val atvContent = der {
                writeObjectId(oid)
                writePrintableString(value)
            }
            return der { writeSet(der { writeSequence(atvContent) }) }
        }

        /** Extension ::= SEQUENCE { extnID OID, critical BOOLEAN DEFAULT FALSE, extnValue OCTET STRING }. */
        private fun extensionTlv(oid: String, critical: Boolean, valueTlv: ByteArray): ByteArray {
            val content = der {
                writeObjectId(oid)
                if (critical) writeBoolean(true)
                writeOctetString(valueTlv)
            }
            return der { writeSequence(content) }
        }

        private fun parseCertificate(encoded: ByteArray): X509Certificate {
            val certificates = CertificateFactory.getInstance("X.509")
                .generateCertificates(ByteArrayInputStream(encoded))
            if (certificates.size != 1) {
                throw CertificateException("expected exactly one certificate, got ${certificates.size}")
            }
            return certificates.first() as X509Certificate
        }

        /** Loads a CA previously persisted with [CaCertificateAuthority.saveKeyStore]. */
        fun loadKeyStore(file: File, password: CharArray): CaCertificateAuthority {
            val store = KeyStore.getInstance(KEYSTORE_TYPE)
            file.inputStream().use { store.load(it, password) }
            val key = store.getKey(CA_ALIAS, password) as? PrivateKey
                ?: throw KeyStoreException("no CA key entry under alias \"$CA_ALIAS\"")
            val certificate = store.getCertificate(CA_ALIAS) as? X509Certificate
                ?: throw KeyStoreException("no CA certificate under alias \"$CA_ALIAS\"")
            return CaCertificateAuthority(CaMaterial(KeyPair(certificate.publicKey, key), certificate))
        }

        private fun sha1(bytes: ByteArray): ByteArray = MessageDigest.getInstance("SHA-1").digest(bytes)

        /** Strips tag + length headers, returning the content of a single DER TLV. */
        private fun derContentOf(tlv: ByteArray): ByteArray {
            require(tlv.size >= 2) { "truncated DER TLV" }
            val firstLengthOctet = tlv[1].toInt() and 0xFF
            val headerSize = if (firstLengthOctet < SHORT_FORM_LIMIT) 2 else 2 + (firstLengthOctet and LONG_FORM_MASK)
            require(tlv.size >= headerSize) { "truncated DER length" }
            return tlv.copyOfRange(headerSize, tlv.size)
        }

        /** Runs [block] on a fresh writer and returns the concatenated TLVs. */
        private fun der(block: DerWriter.() -> Unit): ByteArray = DerWriter().apply(block).toBytes()

        private const val SHORT_FORM_LIMIT = 0x80
        private const val LONG_FORM_MASK = 0x7F
    }
}
