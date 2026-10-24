package com.ultra.trafficagent.mitm

import java.io.ByteArrayOutputStream
import java.math.BigInteger
import java.nio.charset.StandardCharsets
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.Date

/**
 * Minimal DER (Distinguished Encoding Rules) writer used to hand-build
 * X.509 certificates without any third-party ASN.1 library.
 *
 * Every `write*` method appends one complete TLV (tag, length, value) to
 * an internal buffer; [toBytes] returns the concatenation, which doubles
 * as the DER *content* of an enclosing SEQUENCE/SET.
 */
class DerWriter {

    private val out = ByteArrayOutputStream()

    /** Concatenation of every TLV written so far. */
    fun toBytes(): ByteArray = out.toByteArray()

    /**
     * Writes a DER length chain: short form below 0x80, otherwise the
     * minimal number of big-endian length octets prefixed with 0x80|n.
     */
    fun writeLength(length: Int) {
        require(length >= 0) { "length must be non-negative, got $length" }
        if (length < SHORT_FORM_LIMIT) {
            out.write(length)
            return
        }
        var octets = 0
        var remaining = length
        while (remaining != 0) {
            octets++
            remaining = remaining ushr 8
        }
        out.write(LONG_FORM_FLAG or octets)
        for (shift in (octets - 1) * 8 downTo 0 step 8) {
            out.write((length ushr shift) and 0xFF)
        }
    }

    /**
     * INTEGER. [BigInteger.toByteArray] already produces the minimal
     * two's-complement form DER requires (zero is the single byte 0x00).
     */
    fun writeInteger(value: BigInteger) = writeTlv(TAG_INTEGER, value.toByteArray())

    fun writeInteger(value: Long) = writeInteger(BigInteger.valueOf(value))

    fun writeSequence(content: ByteArray) = writeTlv(TAG_SEQUENCE, content)

    fun writeSet(content: ByteArray) = writeTlv(TAG_SET, content)

    /**
     * BIT STRING. [bits] is the raw bit content; the unused-bit count
     * octet DER mandates in front of it is added here.
     */
    fun writeBitString(bits: ByteArray, unusedBits: Int = 0) {
        require(unusedBits in 0..7) { "unusedBits must be within 0..7, got $unusedBits" }
        writeTlv(TAG_BIT_STRING, byteArrayOf(unusedBits.toByte()) + bits)
    }

    fun writeOctetString(content: ByteArray) = writeTlv(TAG_OCTET_STRING, content)

    /**
     * OBJECT IDENTIFIER from dotted-decimal form such as
     * "1.2.840.113549.1.1.11" (base-128 sub-identifiers).
     */
    fun writeObjectId(dotted: String) {
        val arcs = dotted.split('.').map { part ->
            part.toLongOrNull() ?: throw IllegalArgumentException("non-numeric OID component in \"$dotted\"")
        }
        require(arcs.size >= 2) { "OID needs at least two arcs: \"$dotted\"" }
        require(arcs[0] in 0..2) { "first OID arc must be within 0..2: \"$dotted\"" }
        require(arcs[0] < 2 && arcs[1] < SECOND_ARC_LIMIT || arcs[0] == 2L) { "illegal second OID arc: \"$dotted\"" }
        val body = ByteArrayOutputStream()
        writeBase128(body, arcs[0] * FIRST_ARC_MULTIPLIER + arcs[1])
        for (i in 2 until arcs.size) {
            writeBase128(body, arcs[i])
        }
        writeTlv(TAG_OID, body.toByteArray())
    }

    fun writeUtf8String(value: String) = writeTlv(TAG_UTF8_STRING, value.toByteArray(StandardCharsets.UTF_8))

    /** PrintableString is restricted to a small ASCII subset (RFC 5280). */
    fun writePrintableString(value: String) {
        require(value.all { it in PRINTABLE_CHARS }) { "character outside PrintableString set: \"$value\"" }
        writeTlv(TAG_PRINTABLE_STRING, value.toByteArray(StandardCharsets.US_ASCII))
    }

    /**
     * UTCTime ("YYMMDDHHMMSSZ"). RFC 5280 mandates UTCTime for dates
     * through 2049 and forbids it afterwards.
     */
    fun writeUTCTime(date: Date) {
        val year = ZonedDateTime.ofInstant(date.toInstant(), ZoneOffset.UTC).year
        require(year in UTC_MIN_YEAR..UTC_MAX_YEAR) { "UTCTime covers 1950..2049, got year $year" }
        writeTime(TAG_UTC_TIME, UTC_TIME_TWO_DIGIT_YEAR, date)
    }

    fun writeGeneralizedTime(date: Date) = writeTime(TAG_GENERALIZED_TIME, UTC_TIME_FOUR_DIGIT_YEAR, date)

    /** Context-specific tag; X.509 uses explicit `[n]` (constructed) wrappers and implicit `[n]` (primitive) choices. */
    fun writeContextSpecific(tag: Int, content: ByteArray, constructed: Boolean = true) {
        require(tag in 0..MAX_CONTEXT_TAG) { "context tag must be within 0..30, got $tag" }
        val tagOctet = if (constructed) CONTEXT_CONSTRUCTED or tag else CONTEXT_PRIMITIVE or tag
        writeTlv(tagOctet, content)
    }

    /** DER encodes booleans as 0x00 / 0xFF only. */
    fun writeBoolean(value: Boolean) = writeTlv(TAG_BOOLEAN, if (value) byteArrayOf(0xFF.toByte()) else byteArrayOf(0x00))

    fun writeNull() = writeTlv(TAG_NULL, ByteArray(0))

    private fun writeTlv(tag: Int, content: ByteArray) {
        out.write(tag)
        writeLength(content.size)
        out.write(content)
    }

    private fun writeTime(tag: Int, format: DateTimeFormatter, date: Date) {
        val content = (format.format(date.toInstant()) + "Z").toByteArray(StandardCharsets.US_ASCII)
        writeTlv(tag, content)
    }

    private fun writeBase128(target: ByteArrayOutputStream, value: Long) {
        require(value >= 0) { "base-128 value must be non-negative" }
        if (value == 0L) {
            target.write(0)
            return
        }
        var groups = 1
        var remaining = value ushr 7
        while (remaining != 0L) {
            groups++
            remaining = remaining ushr 7
        }
        for (index in groups - 1 downTo 0) {
            val group = ((value ushr (index * 7)) and 0x7F).toInt()
            target.write(if (index == 0) group else group or CONTINUATION_FLAG)
        }
    }

    private companion object {
        const val SHORT_FORM_LIMIT = 0x80
        const val LONG_FORM_FLAG = 0x80
        const val CONTINUATION_FLAG = 0x80
        const val FIRST_ARC_MULTIPLIER = 40
        const val SECOND_ARC_LIMIT = 40L
        const val MAX_CONTEXT_TAG = 30
        const val UTC_MIN_YEAR = 1950
        const val UTC_MAX_YEAR = 2049

        const val TAG_BOOLEAN = 0x01
        const val TAG_INTEGER = 0x02
        const val TAG_BIT_STRING = 0x03
        const val TAG_OCTET_STRING = 0x04
        const val TAG_NULL = 0x05
        const val TAG_OID = 0x06
        const val TAG_UTF8_STRING = 0x0C
        const val TAG_PRINTABLE_STRING = 0x13
        const val TAG_UTC_TIME = 0x17
        const val TAG_GENERALIZED_TIME = 0x18
        const val TAG_SEQUENCE = 0x30
        const val TAG_SET = 0x31
        const val CONTEXT_PRIMITIVE = 0x80
        const val CONTEXT_CONSTRUCTED = 0xA0

        val UTC_TIME_TWO_DIGIT_YEAR: DateTimeFormatter = DateTimeFormatter.ofPattern("yyMMddHHmmss").withZone(ZoneOffset.UTC)
        val UTC_TIME_FOUR_DIGIT_YEAR: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyyMMddHHmmss").withZone(ZoneOffset.UTC)

        val PRINTABLE_CHARS: Set<Char> =
            ('A'..'Z').toSet() + ('a'..'z').toSet() + ('0'..'9').toSet() +
                listOf(' ', '\'', '(', ')', '+', ',', '-', '.', '/', ':', '=', '?')
    }
}
