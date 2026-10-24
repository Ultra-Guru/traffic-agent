package com.ultra.trafficagent.mitm

import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File
import java.security.KeyStore
import java.security.Signature
import java.security.cert.CertificateFactory

class DerEncoderTest {
    @Test
    fun `integer zero encodes to single byte`() {
        val der = DerWriter().apply { writeInteger(0) }.toBytes()
        assertArrayEquals(byteArrayOf(0x02, 0x01, 0x00), der)
    }

    @Test
    fun `integer length forms follow the content size`() {
        assertEquals(3, DerWriter().apply { writeInteger(127) }.toBytes().size)
        // 128 still has a 2-byte content: short length form
        val der = DerWriter().apply { writeInteger(128) }.toBytes()
        assertArrayEquals(byteArrayOf(0x02, 0x02, 0x00, 0x80.toByte()), der)
        // a 128-byte magnitude forces the long length form (0x81 0x80)
        val huge = java.math.BigInteger(1, ByteArray(128) { ((it % 251) + 1).toByte() })
        val long = DerWriter().apply { writeInteger(huge) }.toBytes()
        assertEquals(0x02, long[0].toInt() and 0xFF)
        assertEquals(0x81, long[1].toInt() and 0xFF)
        assertEquals(0x80, long[2].toInt() and 0xFF)
        assertEquals(131, long.size)
    }

    @Test
    fun `integer negative uses minimal two's complement`() {
        val der = DerWriter().apply { writeInteger(-128) }.toBytes()
        assertArrayEquals(byteArrayOf(0x02, 0x01, 0x80.toByte()), der)
        val neg5 = DerWriter().apply { writeInteger(-5) }.toBytes()
        assertArrayEquals(byteArrayOf(0x02, 0x01, 0xFB.toByte()), neg5)
    }

    @Test
    fun `rsa encryption oid matches known bytes`() {
        val der = DerWriter().apply { writeObjectId("1.2.840.113549.1.1.11") }.toBytes()
        assertArrayEquals(
            byteArrayOf(0x06, 0x09, 0x2A, 0x86.toByte(), 0x48, 0x86.toByte(), 0xF7.toByte(), 0x0D, 0x01, 0x01, 0x0B),
            der,
        )
    }

    @Test
    fun `sequence wraps content`() {
        val inner = DerWriter().apply { writeInteger(5) }.toBytes()
        val outer = DerWriter().apply { writeSequence(inner) }.toBytes()
        assertArrayEquals(byteArrayOf(0x30, 0x03, 0x02, 0x01, 0x05), outer)
    }

    @Test
    fun `bit string sets unused bit count`() {
        val der = DerWriter().apply { writeBitString(byteArrayOf(0x5A)) }.toBytes()
        assertArrayEquals(byteArrayOf(0x03, 0x02, 0x00, 0x5A), der)
    }

    @Test
    fun `long content uses multi-byte length`() {
        val big = ByteArray(300) { it.toByte() }
        val der = DerWriter().apply { writeOctetString(big) }.toBytes()
        assertEquals(0x82, der[1].toInt() and 0xFF)
        assertEquals(0x01, der[2].toInt() and 0xFF)
        assertEquals(0x2C, der[3].toInt() and 0xFF) // 300 = 0x12C
        assertEquals(304, der.size)
    }
}

class CaCertificateAuthorityTest {
    @Test
    fun `ca certificate parses and flags ca=true`() {
        val ca = CaCertificateAuthority()
        val cert = ca.caCertificate()
        assertEquals("C=CN,O=Traffic Agent,CN=Traffic Agent CA", cert.subjectX500Principal.name)
        assertEquals(cert.subjectX500Principal, cert.issuerX500Principal) // self-signed
        // CA:TRUE without a pathLenConstraint reports Integer.MAX_VALUE
        assertEquals(Int.MAX_VALUE, cert.basicConstraints)
    }

    @Test
    fun `pem output has proper framing`() {
        val pem = CaCertificateAuthority().caCertificatePem()
        assertTrue(pem.startsWith("-----BEGIN CERTIFICATE-----"))
        assertTrue(pem.contains("-----END CERTIFICATE-----"))
        val base64 = pem.lines().filter { !it.startsWith("---") && it.isNotBlank() }.joinToString("")
        val decoded = java.util.Base64.getDecoder().decode(base64)
        val parsed = CertificateFactory.getInstance("X.509")
            .generateCertificate(decoded.inputStream()) as java.security.cert.X509Certificate
        assertEquals("C=CN,O=Traffic Agent,CN=Traffic Agent CA", parsed.subjectX500Principal.name)
    }

    @Test
    fun `leaf certificate carries san and verifies against ca`() {
        val ca = CaCertificateAuthority()
        val leaf = ca.issueServerCertificate("api.example.com")
        val names = leaf.cert.subjectAlternativeNames
        assertNotNull(names)
        assertEquals("api.example.com", names.first()[1])
        // signature check: CA public key verifies the leaf signature
        val sig = Signature.getInstance("SHA256withRSA")
        sig.initVerify(ca.caCertificate().publicKey)
        sig.update(leaf.cert.encoded.dropLast(256).toByteArray())
        // TBSCertificate is the first SEQUENCE inside the cert; simpler check:
        // chain building via CertPath validation equals same verification.
        val factory = java.security.cert.CertPathValidator.getInstance("PKIX")
        // (PKIX needs anchors; manual path below keeps the test dependency-free)
        val anchor = java.security.cert.TrustAnchor(ca.caCertificate(), null)
        val params = java.security.cert.PKIXParameters(setOf(anchor))
        params.isRevocationEnabled = false
        val path = CertificateFactory.getInstance("X.509").generateCertPath(listOf(leaf.cert))
        factory.validate(path, params) // throws when the leaf is not signed by the CA
    }

    @Test
    fun `keystore save and load roundtrips`() {
        val ca = CaCertificateAuthority()
        val f = File.createTempFile("ta-ca", ".p12")
        try {
            ca.saveKeyStore(f, "changeit".toCharArray())
            val loaded = CaCertificateAuthority.loadKeyStore(f, "changeit".toCharArray())
            assertEquals(ca.caCertificate(), loaded.caCertificate())
            // the loaded CA must keep issuing working leafs
            val leaf = loaded.issueServerCertificate("round.trip.io")
            assertEquals("CN=round.trip.io", leaf.cert.subjectX500Principal.name)
        } finally {
            f.delete()
        }
    }

    @Test
    fun `leaf cache returns same instance per host`() {
        val ca = CaCertificateAuthority()
        val a = ca.issueServerCertificate("same.host.io")
        val b = ca.issueServerCertificate("same.host.io")
        assertTrue(a === b)
        val c = ca.issueServerCertificate("other.host.io")
        assertFalse(a === c)
    }
}

class DerWriterStringMethodsTest {
    @Test
    fun `utf8, printable, null, times round trip`() {
        val utf8 = DerWriter().apply { writeUtf8String("中文") }.toBytes()
        // 0x0C tag, UTF8 payload
        assertEquals(0x0C, utf8[0].toInt() and 0xFF)
        assertEquals("中文".toByteArray(Charsets.UTF_8).size + 2, utf8.size)

        val printable = DerWriter().apply { writePrintableString("abc-XYZ") }.toBytes()
        assertEquals(0x13, printable[0].toInt() and 0xFF)
        assertEquals("abc-XYZ".length + 2, printable.size)

        val nul = DerWriter().apply { writeNull() }.toBytes()
        assertEquals(0x05, nul[0].toInt() and 0xFF)
        assertEquals(0x00, nul[1].toInt() and 0xFF)
        assertEquals(2, nul.size)

        val t = DerWriter().apply { writeUTCTime(java.util.Date(0)) }.toBytes()
        assertEquals(0x17, t[0].toInt() and 0xFF)
        // YYMMDDHHMMSSZ = 13 bytes payload
        assertEquals(15, t.size)

        val gt = DerWriter().apply { writeGeneralizedTime(java.util.Date(0)) }.toBytes()
        assertEquals(0x18, gt[0].toInt() and 0xFF)
        assertEquals(17, gt.size) // YYYYMMDDHHMMSSZ
    }

    @Test
    fun `oid accepts single component and rejects garbage`() {
        val two = DerWriter().apply { writeObjectId("2.5") }.toBytes()
        assertEquals(0x06, two[0].toInt() and 0xFF)
        assertEquals(1, two[1].toInt() and 0xFF) // one content byte
        // 2.5 encodes as 0x55 (2*40+5)
        assertEquals(0x55, two[2].toInt() and 0xFF)
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            DerWriter().apply { writeObjectId("") }
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            DerWriter().apply { writeObjectId("2") }
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            DerWriter().apply { writeObjectId("3.1") }
        }
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            DerWriter().apply { writeObjectId("1.2.x") }
        }
    }

    @Test
    fun `context specific tag limits are enforced`() {
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException::class.java) {
            DerWriter().apply { writeContextSpecific(31, byteArrayOf()) }
        }
        val ok = DerWriter().apply { writeContextSpecific(3, byteArrayOf(1)) }.toBytes()
        // constructed context tag 3 = 0xA3
        assertEquals(0xA3, ok[0].toInt() and 0xFF)
        // primitive variant
        val prim = DerWriter().apply { writeContextSpecific(2, byteArrayOf(7), constructed = false) }.toBytes()
        assertEquals(0x82, prim[0].toInt() and 0xFF)
    }
}
