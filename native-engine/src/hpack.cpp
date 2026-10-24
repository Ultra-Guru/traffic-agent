#include "traffic/hpack.h"

#include "hpack_huffman_table.inc"

namespace traffic {

namespace {

// RFC 7541 Appendix A static table (61 entries). Handwritten per the RFC;
// cross-checked against nghttp2's lib/nghttp2_hd.c static_table[] (see
// scripts/vendor/nghttp2_hd.c).
struct StaticEntry {
    const char* name;
    const char* value;
};

const StaticEntry kStaticTable[61] = {
    {":authority", ""},                  // 1
    {":method", "GET"},                  // 2
    {":method", "POST"},                 // 3
    {":path", "/"},                      // 4
    {":path", "/index.html"},            // 5
    {":scheme", "http"},                 // 6
    {":scheme", "https"},                // 7
    {":status", "200"},                  // 8
    {":status", "204"},                  // 9
    {":status", "206"},                  // 10
    {":status", "304"},                  // 11
    {":status", "400"},                  // 12
    {":status", "404"},                  // 13
    {":status", "500"},                  // 14
    {"accept-charset", ""},             // 15
    {"accept-encoding", "gzip, deflate"},  // 16
    {"accept-language", ""},            // 17
    {"accept-ranges", ""},              // 18
    {"accept", ""},                     // 19
    {"access-control-allow-origin", ""},  // 20
    {"age", ""},                        // 21
    {"allow", ""},                      // 22
    {"authorization", ""},              // 23
    {"cache-control", ""},              // 24
    {"content-disposition", ""},        // 25
    {"content-encoding", ""},          // 26
    {"content-language", ""},           // 27
    {"content-length", ""},             // 28
    {"content-location", ""},           // 29
    {"content-range", ""},              // 30
    {"content-type", ""},               // 31
    {"cookie", ""},                     // 32
    {"date", ""},                       // 33
    {"etag", ""},                       // 34
    {"expect", ""},                     // 35
    {"expires", ""},                    // 36
    {"from", ""},                       // 37
    {"host", ""},                       // 38
    {"if-match", ""},                   // 39
    {"if-modified-since", ""},          // 40
    {"if-none-match", ""},              // 41
    {"if-range", ""},                   // 42
    {"if-unmodified-since", ""},        // 43
    {"last-modified", ""},              // 44
    {"link", ""},                       // 45
    {"location", ""},                   // 46
    {"max-forwards", ""},               // 47
    {"proxy-authenticate", ""},         // 48
    {"proxy-authorization", ""},        // 49
    {"range", ""},                      // 50
    {"referer", ""},                    // 51
    {"refresh", ""},                    // 52
    {"retry-after", ""},                // 53
    {"server", ""},                     // 54
    {"set-cookie", ""},                 // 55
    {"strict-transport-security", ""},  // 56
    {"transfer-encoding", ""},          // 57
    {"user-agent", ""},                 // 58
    {"vary", ""},                       // 59
    {"via", ""},                        // 60
    {"www-authenticate", ""},           // 61
};

constexpr size_t kStaticCount = 61;
constexpr size_t kEntryOverhead = 32;        // RFC 7541 section 4.1
constexpr size_t kDefaultMaxDynSize = 4096;  // SETTINGS_HEADER_TABLE_SIZE default

// ---------------- dynamic table ----------------

class DynTable {
public:
    void add(const std::string& name, const std::string& value) {
        size_t entrySize = name.size() + value.size() + kEntryOverhead;
        if (entrySize > maxSize_) {
            // single oversized entry flushes the table (RFC 7541 4.4)
            entries_.clear();
            size_ = 0;
            return;
        }
        entries_.insert(entries_.begin(), HpackHeader{name, value});
        size_ += entrySize;
        evict();
    }

    void updateMax(size_t newMax) {
        if (newMax > kDefaultMaxDynSize) newMax = kDefaultMaxDynSize;
        maxSize_ = newMax;
        evict();
    }

    // index is the wire value (62 == most recently added).
    bool get(uint64_t index, HpackHeader* out) const {
        if (index < kStaticCount + 1) return false;  // MUT:<=
        size_t i = static_cast<size_t>(index) - (kStaticCount + 1);
        if (i >= entries_.size()) return false;
        *out = entries_[i];
        return true;
    }

    size_t size() const { return entries_.size(); }
    size_t bytes() const { return size_; }

private:
    void evict() {
        while (size_ > maxSize_ && !entries_.empty()) {  // MUT:<
            const HpackHeader& last = entries_.back();
            size_ -= last.name.size() + last.value.size() + kEntryOverhead;
            entries_.pop_back();
        }
    }

    std::vector<HpackHeader> entries_;  // front == newest
    size_t size_ = 0;
    size_t maxSize_ = kDefaultMaxDynSize;
};

// ---------------- primitive decoders ----------------

// Integer with an N-bit prefix (RFC 7541 section 5.1).
HpackStatus decodeInt(const uint8_t* data, size_t len, size_t* pos, uint8_t prefixBits,
                      uint64_t* out) {
    if (pos == nullptr || *pos >= len) return HpackStatus::TooShort;
    uint8_t mask = static_cast<uint8_t>((1u << prefixBits) - 1u);
    uint64_t value = static_cast<uint64_t>(data[*pos] & mask);
    *pos += 1;
    if (value < mask) {  // MUT:<=
        *out = value;
        return HpackStatus::Ok;
    }
    uint64_t m = 0;
    while (true) {
        if (*pos >= len) return HpackStatus::MalformedInteger;
        uint8_t b = data[*pos];
        *pos += 1;
        if (m >= 57) return HpackStatus::MalformedInteger;  // >2^56, overflow guard
        value += static_cast<uint64_t>(b & 0x7Fu) << m;
        m += 7;
        if ((b & 0x80u) == 0) break;  // MUT:!=
    }
    if (value > 0x00FFFFFFull) return HpackStatus::MalformedInteger;  // sanity cap
    *out = value;
    return HpackStatus::Ok;
}

// Canonical Huffman decode using the generated first-code/index tables.
bool huffmanDecode(const uint8_t* data, size_t len, std::string* out) {
    uint32_t code = 0;
    uint32_t nbits = 0;
    for (size_t i = 0; i < len; ++i) {
        uint8_t b = data[i];
        for (int bit = 7; bit >= 0; --bit) {
            code = (code << 1) | static_cast<uint32_t>((b >> bit) & 1u);
            ++nbits;
            if (nbits > hpack_detail::kHuffMaxLength) return false;
            if (nbits >= 5) {  // shortest code is 5 bits
                uint32_t fc = hpack_detail::kHuffFirstCode[nbits];
                uint32_t cnt = hpack_detail::kHuffLengthCount[nbits];
                if (code >= fc && code < fc + cnt) {  // MUT:>=
                    uint16_t sym =
                        hpack_detail::kHuffSymByCode[hpack_detail::kHuffFirstIndex[nbits] +
                                                    (code - fc)];
                    if (sym == 256) return false;  // EOS symbol is invalid in data
                    out->push_back(static_cast<char>(static_cast<uint8_t>(sym)));
                    code = 0;
                    nbits = 0;
                }
            }
        }
    }
    // Trailing bits must be a valid EOS prefix: at most 7 bits, all ones.
    if (nbits > 7) return false;  // MUT:>=
    if (nbits > 0 && code != ((1u << nbits) - 1u)) return false;
    return true;
}

// String literal (RFC 7541 section 5.2), Huffman-aware.
HpackStatus decodeString(const uint8_t* data, size_t len, size_t* pos, std::string* out) {
    if (pos == nullptr || *pos >= len) return HpackStatus::TooShort;
    bool huff = (data[*pos] & 0x80u) != 0;
    uint64_t slen = 0;
    HpackStatus s = decodeInt(data, len, pos, 7, &slen);
    if (s != HpackStatus::Ok) return s;
    if (slen > len - *pos) return HpackStatus::TooShort;  // MUT:>=
    if (huff) {
        out->clear();
        if (!huffmanDecode(data + *pos, static_cast<size_t>(slen), out)) {
            return HpackStatus::MalformedString;
        }
    } else {
        out->assign(reinterpret_cast<const char*>(data + *pos), static_cast<size_t>(slen));
    }
    *pos += static_cast<size_t>(slen);
    return HpackStatus::Ok;
}

// Resolves a name index shared by the literal instructions.
HpackStatus lookupName(const DynTable& dyn, uint64_t index, std::string* name) {
    if (index == 0 || index > kStaticCount) {
        HpackHeader h{};
        if (!dyn.get(index, &h)) return HpackStatus::BadIndex;
        *name = h.name;
        return HpackStatus::Ok;
    }
    *name = kStaticTable[static_cast<size_t>(index) - 1].name;
    return HpackStatus::Ok;
}

}  // namespace

HpackStatus decodeHpack(const uint8_t* data, size_t len, std::vector<HpackHeader>* out,
                        size_t* consumed) {
    if (data == nullptr || out == nullptr) return HpackStatus::TooShort;
    if (len == 0) {
        if (consumed != nullptr) *consumed = 0;
        return HpackStatus::Ok;
    }
    DynTable dyn;
    size_t pos = 0;
    while (pos < len) {  // MUT:>=
        uint8_t b = data[pos];
        if ((b & 0x80u) != 0) {
            // 1xxxxxxx: indexed header field
            uint64_t index = 0;
            HpackStatus s = decodeInt(data, len, &pos, 7, &index);
            if (s != HpackStatus::Ok) return s;
            HpackHeader h{};
            if (index == 0) return HpackStatus::BadIndex;  // MUT:!=
            if (index <= kStaticCount) {
                h.name = kStaticTable[static_cast<size_t>(index) - 1].name;
                h.value = kStaticTable[static_cast<size_t>(index) - 1].value;
            } else if (!dyn.get(index, &h)) {
                return HpackStatus::BadIndex;
            }
            out->push_back(h);
        } else if ((b & 0xC0u) == 0x40u) {
            // 01xxxxxx: literal with incremental indexing
            uint64_t index = 0;
            HpackStatus s = decodeInt(data, len, &pos, 6, &index);
            if (s != HpackStatus::Ok) return s;
            HpackHeader h{};
            if (index == 0) {
                s = decodeString(data, len, &pos, &h.name);
            } else {
                s = lookupName(dyn, index, &h.name);
            }
            if (s != HpackStatus::Ok) return s;
            s = decodeString(data, len, &pos, &h.value);
            if (s != HpackStatus::Ok) return s;
            dyn.add(h.name, h.value);
            out->push_back(h);
        } else if ((b & 0xE0u) == 0x20u) {
            // 001xxxxx: dynamic table size update
            uint64_t sz = 0;
            HpackStatus s = decodeInt(data, len, &pos, 5, &sz);
            if (s != HpackStatus::Ok) return s;
            if (sz > kDefaultMaxDynSize) return HpackStatus::MalformedInteger;  // MUT:<
            dyn.updateMax(static_cast<size_t>(sz));
        } else {
            // 0000xxxx: literal without indexing, 0001xxxx: never indexed
            uint64_t index = 0;
            HpackStatus s = decodeInt(data, len, &pos, 4, &index);
            if (s != HpackStatus::Ok) return s;
            HpackHeader h{};
            if (index == 0) {
                s = decodeString(data, len, &pos, &h.name);
            } else {
                s = lookupName(dyn, index, &h.name);
            }
            if (s != HpackStatus::Ok) return s;
            s = decodeString(data, len, &pos, &h.value);
            if (s != HpackStatus::Ok) return s;
            out->push_back(h);
        }
    }
    if (consumed != nullptr) *consumed = pos;
    return HpackStatus::Ok;
}

std::vector<uint8_t> huffmanEncode(const std::string& s) {
    std::vector<uint8_t> out;
    uint64_t acc = 0;
    uint32_t nbits = 0;
    for (char c : s) {
        const hpack_detail::HuffSym& sym = hpack_detail::kHuffSym[static_cast<uint8_t>(c)];
        acc = (acc << sym.nbits) | sym.code;
        nbits += sym.nbits;
        while (nbits >= 8) {
            nbits -= 8;
            out.push_back(static_cast<uint8_t>((acc >> nbits) & 0xFFu));
        }
    }
    if (nbits > 0) {
        uint64_t pad = (1u << (8 - nbits)) - 1u;
        out.push_back(static_cast<uint8_t>(((acc << (8 - nbits)) | pad) & 0xFFu));
    }
    return out;
}

std::vector<uint8_t> encodeHpack(const std::vector<HpackHeader>& headers) {
    std::vector<uint8_t> out;
    for (const HpackHeader& h : headers) {
        out.push_back(0x00);  // literal without indexing, new name
        // plain string: H=0, 7-bit prefix length
        auto putString = [&out](const std::string& v) {
            size_t len = v.size();
            if (len < 127) {
                out.push_back(static_cast<uint8_t>(len));
            } else {
                out.push_back(127);
                size_t rem = len - 127;
                while (rem >= 128) {
                    out.push_back(static_cast<uint8_t>((rem & 0x7Fu) | 0x80u));
                    rem >>= 7;
                }
                out.push_back(static_cast<uint8_t>(rem));
            }
            out.insert(out.end(), v.begin(), v.end());
        };
        putString(h.name);
        putString(h.value);
    }
    return out;
}

size_t hpackStaticTableSize() { return kStaticCount; }

const char* hpackStaticName(size_t index) {
    if (index < 1 || index > kStaticCount) return nullptr;  // MUT:>=
    return kStaticTable[index - 1].name;
}

const char* hpackStaticValue(size_t index) {
    if (index < 1 || index > kStaticCount) return nullptr;  // MUT:>=
    return kStaticTable[index - 1].value;
}

}  // namespace traffic
