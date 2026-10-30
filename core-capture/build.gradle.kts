plugins {
    kotlin("jvm")
    id("info.solidsoft.pitest")
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}

pitest {
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(listOf("com.ultra.trafficagent.capture.*"))
    // Socket/HttpClient I/O engines: mutants are equivalent-heavy wrappers.
    // TcpStackBridge/PcapWriterBridge are System.loadLibrary JNI shells;
    // VpnOrchestrator drives real threads: untestable as pure JVM logic.
    excludedClasses.set(listOf(
        "com.ultra.trafficagent.capture.ReplayEngine",
        "com.ultra.trafficagent.capture.PacketPump",
        "com.ultra.trafficagent.capture.TunFileSource",
        "com.ultra.trafficagent.capture.TcpStackBridge",
        "com.ultra.trafficagent.capture.PcapWriterBridge",
        "com.ultra.trafficagent.capture.PcapSessionFile",
        "com.ultra.trafficagent.capture.JdkSocketOpener",
        "com.ultra.trafficagent.capture.VpnOrchestrator*",
    ))
    mutators.set(listOf("DEFAULTS"))
    outputFormats.set(listOf("XML", "HTML"))
    threads.set(1)
}
