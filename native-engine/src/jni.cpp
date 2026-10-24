#include <jni.h>

#include <cstdint>
#include <vector>

#include "traffic/engine.h"

// JNI surface for the Android app: the app owns a long-lived Engine handle
// created on the native heap and feeds it raw IPv4 packets from the
// VpnService TUN fd. Events are drained with nativePollEvents.

namespace {

traffic::Engine* asEngine(jlong handle) {
    return reinterpret_cast<traffic::Engine*>(static_cast<uintptr_t>(handle));
}

jstring toJString(JNIEnv* env, const std::string& s) {
    return env->NewStringUTF(s.c_str());
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

}  // extern "C"
