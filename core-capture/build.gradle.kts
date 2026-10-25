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
    // TcpStackBridge is the System.loadLibrary JNI shell: untestable on JVM.
    excludedClasses.set(listOf(
        "com.ultra.trafficagent.capture.ReplayEngine",
        "com.ultra.trafficagent.capture.PacketPump",
        "com.ultra.trafficagent.capture.TunFileSource",
        "com.ultra.trafficagent.capture.TcpStackBridge",
    ))
    mutators.set(listOf("DEFAULTS"))
    outputFormats.set(listOf("XML", "HTML"))
    threads.set(1)
}
