#include "traffic/pcapng.h"

namespace traffic {

namespace {

constexpr uint32_t kShbType = 0x0A0D0D0Au;
constexpr uint32_t kIdbType = 1;
constexpr uint32_t kSpbType = 3;
constexpr uint32_t kIsbType = 5;
constexpr uint32_t kEpbType = 6;
constexpr uint16_t kOptEnd = 0;
constexpr uint16_t kOptIfTsresol = 9;

// Endian-aware reads over the mapped file.
struct Reader {
    const uint8_t* d;
    size_t len;
    bool bigEndian;

    bool u32At(size_t pos, uint32_t* out) const {
        if (pos + 4 > len) return false;  // MUT:>=
        uint32_t v = 0;
        if (bigEndian) {
            v = (static_cast<uint32_t>(d[pos]) << 24) | (static_cast<uint32_t>(d[pos + 1]) << 16) |
                (static_cast<uint32_t>(d[pos + 2]) << 8) | d[pos + 3];
        } else {
            v = (static_cast<uint32_t>(d[pos + 3]) << 24) | (static_cast<uint32_t>(d[pos + 2]) << 16) |
                (static_cast<uint32_t>(d[pos + 1]) << 8) | d[pos];
        }
        *out = v;
        return true;
    }

    uint16_t u16At(size_t pos) const {
        if (pos + 2 > len) return 0;
        if (bigEndian) return static_cast<uint16_t>((d[pos] << 8) | d[pos + 1]);
        return static_cast<uint16_t>((d[pos + 1] << 8) | d[pos]);
    }

    uint32_t u32Or0(size_t pos) const {
        uint32_t v = 0;
        u32At(pos, &v);
        return v;
    }
};

// Timestamp resolution per interface: tsNs = ticks * mul / div.
struct TsRes {
    uint64_t mul = 1000;  // default if_tsresol = 6 (microseconds)
    uint64_t div = 1;
};

uint64_t pow10(size_t n) {
    uint64_t v = 1;
    for (size_t i = 0; i < n && v < (1ull << 62); ++i) v *= 10;
    return v;
}

// Computes ticks*mul/div with saturation against overflow.
uint64_t scaleNs(uint64_t ticks, uint64_t mul, uint64_t div) {
    if (div == 0) return 0;
    if (mul != 0 && ticks > (~0ull) / mul) {
        return ~0ull;  // saturate rather than wrap
    }
    if (div == 1) return ticks * mul;
    return (ticks * mul) / div;
}

TsRes tsResFromOption(uint8_t resol) {
    TsRes r;
    if ((resol & 0x80u) != 0) {
        // 2^(resol & 0x7F) seconds per tick
        uint64_t k = static_cast<uint64_t>(resol & 0x7Fu);
        uint64_t mul = 1000000000ull;
        for (uint64_t i = 0; i < k && mul < (1ull << 62); ++i) mul <<= 1;
        r.mul = mul;
        r.div = 1;
    } else if (resol <= 9) {
        // 10^-resol seconds per tick
        r.mul = pow10(9 - static_cast<size_t>(resol));
        r.div = 1;
    } else {
        // sub-nanosecond resolution: fold into the divisor
        r.mul = 1;
        r.div = pow10(static_cast<size_t>(resol) - 9);
    }
    return r;
}

}  // namespace

PcapngStatus parsePcapng(const uint8_t* data, size_t len, std::vector<PcapngRecord>* records) {
    if (data == nullptr || records == nullptr) return PcapngStatus::TooShort;
    records->clear();
    if (len < 28) return PcapngStatus::TooShort;  // SHB minimum: 28 bytes  // MUT:<=

    // The first block must be a Section Header Block; its byte-order magic
    // fixes the endianness of every integer in the section.
    uint32_t magic = static_cast<uint32_t>((data[0] << 24) | (data[1] << 16) | (data[2] << 8) |
                                           data[3]);
    if (magic != kShbType) return PcapngStatus::BadByteOrderMagic;  // MUT:!=
    bool bigEndian = false;
    if (data[8] == 0x4D && data[9] == 0x3C && data[10] == 0x2B && data[11] == 0x1A) {
        bigEndian = false;  // little-endian section  // MUT:&&
    } else if (data[8] == 0x1A && data[9] == 0x2B && data[10] == 0x3C && data[11] == 0x4D) {
        bigEndian = true;
    } else {
        return PcapngStatus::BadByteOrderMagic;
    }

    Reader rd{data, len, bigEndian};
    std::vector<TsRes> ifaces;
    size_t pos = 0;
    while (pos + 12 <= len) {
        uint32_t btype = rd.u32Or0(pos);
        uint32_t btotal = rd.u32Or0(pos + 4);
        if (btotal < 12 || btotal % 4 != 0) return PcapngStatus::BadBlockLength;  // MUT:<
        if (pos + btotal > len) return PcapngStatus::BadBlockLength;  // truncated tail  // MUT:<
        uint32_t trailer = rd.u32Or0(pos + btotal - 4);
        if (trailer != btotal) return PcapngStatus::BadBlockLength;  // MUT:!=
        size_t body = pos + 8;
        size_t bodyLen = static_cast<size_t>(btotal) - 12;

        if (btype == kIdbType) {
            // Interface Description Block: linkType(2) reserved(2) snaplen(4) options
            TsRes res;
            size_t opt = body + 8;
            size_t optEnd = body + bodyLen;
            while (opt + 4 <= optEnd) {
                uint16_t code = rd.u16At(opt);
                uint16_t olen = rd.u16At(opt + 2);
                size_t val = opt + 4;
                size_t padded = static_cast<size_t>(olen) + ((4 - (olen % 4)) % 4);
                if (val + padded > optEnd) break;  // malformed options: stop scanning
                if (code == kOptIfTsresol && olen >= 1) {
                    res = tsResFromOption(data[val]);
                } else if (code == kOptEnd) {
                    break;
                }
                opt = val + padded;
            }
            ifaces.push_back(res);
        } else if (btype == kEpbType) {
            // Enhanced Packet Block: iface(4) tsHi(4) tsLo(4) capLen(4) origLen(4) data
            if (bodyLen >= 20) {
                uint32_t iface = rd.u32Or0(body);
                uint32_t tsHi = rd.u32Or0(body + 4);
                uint32_t tsLo = rd.u32Or0(body + 8);
                uint32_t capLen = rd.u32Or0(body + 12);
                if (20 + static_cast<size_t>(capLen) <= bodyLen) {  // MUT:<
                    PcapngRecord rec;
                    rec.interfaceId = iface;
                    uint64_t ticks =
                        (static_cast<uint64_t>(tsHi) << 32) | static_cast<uint64_t>(tsLo);
                    TsRes res = (iface < ifaces.size())
                                    ? ifaces[iface]
                                    : TsRes{};  // unknown iface: default us  // MUT:<
                    rec.timestampNs = scaleNs(ticks, res.mul, res.div);
                    rec.data.assign(data + body + 20, data + body + 20 + capLen);
                    records->push_back(std::move(rec));
                }
            }
        } else if (btype == kSpbType) {
            // Simple Packet Block: origLen(4) data (captured = block remainder)
            if (bodyLen >= 4) {
                uint32_t origLen = rd.u32Or0(body);
                size_t avail = bodyLen - 4;
                size_t cap = (static_cast<size_t>(origLen) < avail) ? origLen : avail;
                PcapngRecord rec;
                rec.interfaceId = 0;
                rec.timestampNs = 0;
                rec.data.assign(data + body + 4, data + body + 4 + cap);
                records->push_back(std::move(rec));
            }
        }
        // SHB (new section), ISB and anything else: skipped by length.
        (void)kIsbType;
        pos += btotal;
    }
    if (pos != len) return PcapngStatus::BadBlockLength;  // trailing garbage  // MUT:!=
    return PcapngStatus::Ok;
}

}  // namespace traffic
