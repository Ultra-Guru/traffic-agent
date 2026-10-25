// JNI surface for the Android app: the app owns a long-lived Engine handle
// created on the native heap and feeds it raw IPv4 packets from the
// VpnService TUN fd. Events are drained with nativePollEvents.
//
// The file compiles to an empty unit when <jni.h> is unavailable (plain
// Linux test builds without a JDK); the Android NDK always provides it.

#if defined(__has_include)
#if __has_include(<jni.h>)
#define TA_HAVE_JNI 1
#endif
#elif defined(__ANDROID__)
#define TA_HAVE_JNI 1
#endif

#ifdef TA_HAVE_JNI

#include <jni.h>

#include <cstdint>
#include <string>
#include <vector>

#include "traffic/body.h"
#include "traffic/engine.h"
#include "traffic/hpack.h"
#include "traffic/md5.h"
#include "traffic/stack.h"
#include "traffic/tls.h"

namespace {

traffic::Engine* asEngine(jlong handle) {
    return reinterpret_cast<traffic::Engine*>(static_cast<uintptr_t>(handle));
}

jstring toJString(JNIEnv* env, const std::string& s) {
    return env->NewStringUTF(s.c_str());
}

traffic::ForwardStack* asStack(jlong handle) {
    return reinterpret_cast<traffic::ForwardStack*>(static_cast<uintptr_t>(handle));
}

// Packs the vector of emitted packets into a Java byte[][] for the Kotlin loop.
jobjectArray toPacketArray(JNIEnv* env, const std::vector<std::vector<uint8_t>>& pkts) {
    jclass byteClass = env->FindClass("[B");
    jobjectArray arr = env->NewObjectArray(static_cast<jsize>(pkts.size()), byteClass, nullptr);
    for (jsize i = 0; i < static_cast<jsize>(pkts.size()); ++i) {
        jbyteArray elem = env->NewByteArray(static_cast<jsize>(pkts[i].size()));
        env->SetByteArrayRegion(elem, 0, static_cast<jsize>(pkts[i].size()),
                                reinterpret_cast<const jbyte*>(pkts[i].data()));
        env->SetObjectArrayElement(arr, i, elem);
        env->DeleteLocalRef(elem);
    }
    return arr;
}

void put16(std::vector<uint8_t>& b, uint16_t v) {
    b.push_back(static_cast<uint8_t>(v >> 8));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

void put32(std::vector<uint8_t>& b, uint32_t v) {
    b.push_back(static_cast<uint8_t>(v >> 24));
    b.push_back(static_cast<uint8_t>((v >> 16) & 0xFF));
    b.push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
    b.push_back(static_cast<uint8_t>(v & 0xFF));
}

traffic::FlowKey flowFrom(jint srcIp, jint srcPort, jint dstIp, jint dstPort) {
    traffic::FlowKey k;
    k.srcAddr = static_cast<uint32_t>(srcIp);
    k.srcPort = static_cast<uint16_t>(srcPort & 0xFFFF);
    k.dstAddr = static_cast<uint32_t>(dstIp);
    k.dstPort = static_cast<uint16_t>(dstPort & 0xFFFF);
    return k;
}

std::vector<uint8_t> jbyteToVector(JNIEnv* env, jbyteArray arr) {
    jsize n = env->GetArrayLength(arr);
    std::vector<uint8_t> out(static_cast<size_t>(n < 0 ? 0 : n));
    if (n > 0) {
        env->GetByteArrayRegion(arr, 0, n, reinterpret_cast<jbyte*>(out.data()));
    }
    return out;
}

jbyteArray vectorToJBytes(JNIEnv* env, const std::vector<uint8_t>& v) {
    jbyteArray arr = env->NewByteArray(static_cast<jsize>(v.size()));
    if (!v.empty()) {
        env->SetByteArrayRegion(arr, 0, static_cast<jsize>(v.size()),
                                reinterpret_cast<const jbyte*>(v.data()));
    }
    return arr;
}

}  // namespace

extern "C" {

JNIEXPORT jlong JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeInit(JNIEnv* /*env*/, jobject /*thiz*/) {
    auto* engine = new traffic::Engine();
    return static_cast<jlong>(reinterpret_cast<uintptr_t>(engine));
}

JNIEXPORT jint JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeFeedPacket(JNIEnv* env, jobject /*thiz*/,
                                                                  jlong handle, jbyteArray pkt,
                                                                  jlong timestampMs) {
    auto* engine = asEngine(handle);
    if (engine == nullptr) return -1;
    jsize n = env->GetArrayLength(pkt);
    if (n <= 0) return -1;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    env->GetByteArrayRegion(pkt, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    return static_cast<jint>(engine->feedPacket(buf.data(), buf.size(),
                                                static_cast<uint64_t>(timestampMs)));
}

JNIEXPORT jint JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeEventCount(JNIEnv* /*env*/,
                                                                   jobject /*thiz*/, jlong handle) {
    auto* engine = asEngine(handle);
    if (engine == nullptr) return -1;
    return static_cast<jint>(engine->events().size());
}

JNIEXPORT void JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeClearEvents(JNIEnv* /*env*/,
                                                                    jobject /*thiz*/, jlong handle) {
    auto* engine = asEngine(handle);
    if (engine != nullptr) engine->clearEvents();
}

JNIEXPORT void JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeDestroy(JNIEnv* /*env*/, jobject /*thiz*/,
                                                               jlong handle) {
    auto* engine = asEngine(handle);
    if (engine != nullptr) delete engine;
}

// ---- Task 2-a additions (TLS/JA3, HPACK, body decoding) ----

JNIEXPORT jobjectArray JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeParseClientHello(JNIEnv* env,
                                                                        jobject /*thiz*/,
                                                                        jbyteArray pkt) {
    jsize n = env->GetArrayLength(pkt);
    if (n <= 0) return nullptr;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    env->GetByteArrayRegion(pkt, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    traffic::ClientHelloInfo chi{};
    if (traffic::parseTlsClientHello(buf.data(), buf.size(), &chi) != traffic::TlsStatus::Ok) {
        return nullptr;
    }
    std::vector<std::string> lines;
    lines.push_back("version:" + traffic::tlsVersionName(chi.clientVersion));
    lines.push_back("recordVersion:" + traffic::tlsVersionName(chi.recordVersion));
    lines.push_back("random:" + chi.randomHex);
    lines.push_back("sessionId:" + chi.sessionIdHex);
    lines.push_back("sni:" + chi.sni);
    std::string alpn;
    for (size_t i = 0; i < chi.alpn.size(); ++i) {
        if (i > 0) alpn.push_back(',');
        alpn += chi.alpn[i];
    }
    lines.push_back("alpn:" + alpn);
    std::string ciphers;
    for (size_t i = 0; i < chi.cipherSuites.size(); ++i) {
        if (i > 0) ciphers.push_back(',');
        ciphers += traffic::tlsCipherName(chi.cipherSuites[i]);
    }
    lines.push_back("cipherCount:" + std::to_string(chi.cipherSuites.size()));
    lines.push_back("ciphers:" + ciphers);
    std::string exts;
    for (size_t i = 0; i < chi.extensions.size(); ++i) {
        if (i > 0) exts.push_back(',');
        exts += std::to_string(chi.extensions[i].type);
    }
    lines.push_back("extensions:" + exts);
    lines.push_back("ja3:" + chi.ja3);
    lines.push_back("ja3Md5:" + chi.ja3Md5);

    jclass cls = env->FindClass("java/lang/String");
    if (cls == nullptr) return nullptr;
    jobjectArray out = env->NewObjectArray(static_cast<jsize>(lines.size()), cls, nullptr);
    if (out == nullptr) return nullptr;
    for (size_t i = 0; i < lines.size(); ++i) {
        jstring s = toJString(env, lines[i]);
        if (s == nullptr) return nullptr;
        env->SetObjectArrayElement(out, static_cast<jsize>(i), s);
        env->DeleteLocalRef(s);
    }
    return out;
}

JNIEXPORT jstring JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeJa3(JNIEnv* env, jobject /*thiz*/,
                                                           jbyteArray clientHello) {
    jsize n = env->GetArrayLength(clientHello);
    if (n <= 0) return nullptr;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    env->GetByteArrayRegion(clientHello, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    traffic::ClientHelloInfo chi{};
    if (traffic::parseTlsClientHello(buf.data(), buf.size(), &chi) != traffic::TlsStatus::Ok) {
        return nullptr;
    }
    return toJString(env, chi.ja3Md5);
}

JNIEXPORT jobjectArray JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeHpackDecode(JNIEnv* env, jobject /*thiz*/,
                                                                  jbyteArray block) {
    jsize n = env->GetArrayLength(block);
    if (n < 0) return nullptr;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    if (n > 0) env->GetByteArrayRegion(block, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    std::vector<traffic::HpackHeader> headers;
    size_t consumed = 0;
    if (traffic::decodeHpack(buf.data(), buf.size(), &headers, &consumed) != traffic::HpackStatus::Ok) {
        return nullptr;
    }
    jclass cls = env->FindClass("java/lang/String");
    if (cls == nullptr) return nullptr;
    jobjectArray out = env->NewObjectArray(static_cast<jsize>(headers.size()), cls, nullptr);
    if (out == nullptr) return nullptr;
    for (size_t i = 0; i < headers.size(); ++i) {
        jstring s = toJString(env, headers[i].name + ":" + headers[i].value);
        if (s == nullptr) return nullptr;
        env->SetObjectArrayElement(out, static_cast<jsize>(i), s);
        env->DeleteLocalRef(s);
    }
    return out;
}

JNIEXPORT jbyteArray JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeDecodeChunked(JNIEnv* env,
                                                                     jobject /*thiz*/,
                                                                     jbyteArray body) {
    jsize n = env->GetArrayLength(body);
    if (n < 0) return nullptr;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    if (n > 0) env->GetByteArrayRegion(body, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    std::vector<uint8_t> out;
    size_t consumed = 0;
    if (traffic::decodeChunked(buf.data(), buf.size(), &out, &consumed, nullptr) !=
        traffic::ChunkedStatus::Complete) {
        return nullptr;
    }
    jbyteArray arr = env->NewByteArray(static_cast<jsize>(out.size()));
    if (arr == nullptr) return nullptr;
    if (!out.empty()) {
        env->SetByteArrayRegion(arr, 0, static_cast<jsize>(out.size()),
                                reinterpret_cast<const jbyte*>(out.data()));
    }
    return arr;
}

JNIEXPORT jbyteArray JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeDecompressBody(JNIEnv* env,
                                                                      jobject /*thiz*/,
                                                                      jbyteArray body,
                                                                      jstring encoding) {
    jsize n = env->GetArrayLength(body);
    if (n < 0) return nullptr;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    if (n > 0) env->GetByteArrayRegion(body, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    const char* enc = (encoding != nullptr) ? env->GetStringUTFChars(encoding, nullptr) : "";
    std::string encStr = (enc != nullptr) ? enc : "";
    if (encoding != nullptr && enc != nullptr) env->ReleaseStringUTFChars(encoding, enc);
    std::vector<uint8_t> out;
    if (!traffic::decompressBody(buf.data(), buf.size(), encStr, &out)) return nullptr;
    jbyteArray arr = env->NewByteArray(static_cast<jsize>(out.size()));
    if (arr == nullptr) return nullptr;
    if (!out.empty()) {
        env->SetByteArrayRegion(arr, 0, static_cast<jsize>(out.size()),
                                reinterpret_cast<const jbyte*>(out.data()));
    }
    return arr;
}

JNIEXPORT jstring JNICALL
Java_com_ultra_trafficagent_capture_NativeEngine_nativeSniffMime(JNIEnv* env, jobject /*thiz*/,
                                                                 jbyteArray body,
                                                                 jstring declared) {
    jsize n = env->GetArrayLength(body);
    if (n < 0) return nullptr;
    std::vector<uint8_t> buf(static_cast<size_t>(n));
    if (n > 0) env->GetByteArrayRegion(body, 0, n, reinterpret_cast<jbyte*>(buf.data()));
    const char* dec = (declared != nullptr) ? env->GetStringUTFChars(declared, nullptr) : "";
    std::string decStr = (dec != nullptr) ? dec : "";
    if (declared != nullptr && dec != nullptr) env->ReleaseStringUTFChars(declared, dec);
    return toJString(env, traffic::sniffMime(buf.data(), buf.size(), decStr));
}

// ---------------- TcpStackBridge (ForwardStack, 基建一) ----------------
// The ForwardStack natives expose the user-space forwarding stack: packets
// from the TUN fd go in, packets to write back to the TUN come out, and the
// socket layer consumes connects/sends/closes through fixed-layout binary
// frames (decoded by TcpStackBridge.kt on the Kotlin side).

JNIEXPORT jlong JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackCreate(JNIEnv* /*env*/,
                                                                     jobject /*thiz*/,
                                                                     jboolean mitmEnabled,
                                                                     jboolean blockQuic,
                                                                     jint clientMss) {
    traffic::StackConfig cfg;
    cfg.mitmEnabled = mitmEnabled == JNI_TRUE;
    cfg.blockQuic = blockQuic == JNI_TRUE;
    if (clientMss > 0) cfg.clientMss = static_cast<uint32_t>(clientMss);
    return static_cast<jlong>(reinterpret_cast<uintptr_t>(new traffic::ForwardStack(cfg)));
}

JNIEXPORT void JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackDestroy(JNIEnv* /*env*/,
                                                                      jobject /*thiz*/,
                                                                      jlong handle) {
    auto* stack = asStack(handle);
    if (stack != nullptr) delete stack;
}

JNIEXPORT jobjectArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackOnTunPacket(JNIEnv* env,
                                                                          jobject /*thiz*/,
                                                                          jlong handle,
                                                                          jbyteArray pkt,
                                                                          jlong tsMs) {
    auto* stack = asStack(handle);
    std::vector<std::vector<uint8_t>> out;
    if (stack != nullptr) {
        std::vector<uint8_t> buf = jbyteToVector(env, pkt);
        stack->onTunPacket(buf.data(), buf.size(), static_cast<uint64_t>(tsMs), &out);
    }
    return toPacketArray(env, out);
}

JNIEXPORT jobjectArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackOnUpstreamData(
    JNIEnv* env, jobject /*thiz*/, jlong handle, jint srcIp, jint srcPort, jint dstIp,
    jint dstPort, jbyteArray data, jlong tsMs) {
    auto* stack = asStack(handle);
    std::vector<std::vector<uint8_t>> out;
    if (stack != nullptr) {
        std::vector<uint8_t> buf = jbyteToVector(env, data);
        stack->onUpstreamData(flowFrom(srcIp, srcPort, dstIp, dstPort), buf.data(), buf.size(),
                              static_cast<uint64_t>(tsMs), &out);
    }
    return toPacketArray(env, out);
}

JNIEXPORT jobjectArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackOnUpstreamClosed(
    JNIEnv* env, jobject /*thiz*/, jlong handle, jint srcIp, jint srcPort, jint dstIp,
    jint dstPort, jlong tsMs) {
    auto* stack = asStack(handle);
    std::vector<std::vector<uint8_t>> out;
    if (stack != nullptr) {
        stack->onUpstreamClosed(flowFrom(srcIp, srcPort, dstIp, dstPort),
                                static_cast<uint64_t>(tsMs), &out);
    }
    return toPacketArray(env, out);
}

JNIEXPORT jobjectArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackSweep(JNIEnv* env,
                                                                   jobject /*thiz*/,
                                                                   jlong handle, jlong nowMs) {
    auto* stack = asStack(handle);
    std::vector<std::vector<uint8_t>> out;
    if (stack != nullptr) {
        stack->sweep(static_cast<uint64_t>(nowMs), &out);
    }
    return toPacketArray(env, out);
}

JNIEXPORT jbyteArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackTakeConnects(JNIEnv* env,
                                                                           jobject /*thiz*/,
                                                                           jlong handle) {
    std::vector<uint8_t> frame;
    auto* stack = asStack(handle);
    if (stack != nullptr) {
        // [1B isUdp][srcIp][srcPort][dstIp][dstPort][effDstIp][effDstPort]
        for (const auto& c : stack->takeConnects()) {
            frame.push_back(c.isUdp ? 1 : 0);
            put32(frame, c.original.srcAddr);
            put16(frame, c.original.srcPort);
            put32(frame, c.original.dstAddr);
            put16(frame, c.original.dstPort);
            put32(frame, c.effective.dstAddr);
            put16(frame, c.effective.dstPort);
        }
    }
    return vectorToJBytes(env, frame);
}

JNIEXPORT jbyteArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackTakeSends(JNIEnv* env,
                                                                        jobject /*thiz*/,
                                                                        jlong handle) {
    std::vector<uint8_t> frame;
    auto* stack = asStack(handle);
    if (stack != nullptr) {
        // [srcIp][srcPort][dstIp][dstPort][4B len][data]
        for (const auto& s : stack->takeSends()) {
            put32(frame, s.flow.srcAddr);
            put16(frame, s.flow.srcPort);
            put32(frame, s.flow.dstAddr);
            put16(frame, s.flow.dstPort);
            put32(frame, static_cast<uint32_t>(s.data.size()));
            frame.insert(frame.end(), s.data.begin(), s.data.end());
        }
    }
    return vectorToJBytes(env, frame);
}

JNIEXPORT jbyteArray JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackTakeCloses(JNIEnv* env,
                                                                         jobject /*thiz*/,
                                                                         jlong handle) {
    std::vector<uint8_t> frame;
    auto* stack = asStack(handle);
    if (stack != nullptr) {
        // [srcIp][srcPort][dstIp][dstPort]
        for (const auto& c : stack->takeCloses()) {
            put32(frame, c.flow.srcAddr);
            put16(frame, c.flow.srcPort);
            put32(frame, c.flow.dstAddr);
            put16(frame, c.flow.dstPort);
        }
    }
    return vectorToJBytes(env, frame);
}

JNIEXPORT jint JNICALL
Java_com_ultra_trafficagent_capture_TcpStackBridge_nativeStackFlowCount(JNIEnv* /*env*/,
                                                                        jobject /*thiz*/,
                                                                        jlong handle) {
    auto* stack = asStack(handle);
    if (stack == nullptr) return -1;
    return static_cast<jint>(stack->flowCount());
}

}  // extern "C"

#endif  // TA_HAVE_JNI
