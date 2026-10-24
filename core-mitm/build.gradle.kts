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
    implementation(project(":core-capture"))
    implementation(project(":core-transform"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}

pitest {
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(listOf("com.ultra.trafficagent.mitm.*"))
    // Socket/SSL wiring mutants are equivalent-heavy (I/O wrappers); the
    // protocol logic lives in the tested model/encoder/interceptor classes.
    excludedClasses.set(listOf(
        "com.ultra.trafficagent.mitm.MitmProxyServer*",
        "com.ultra.trafficagent.mitm.TlsContexts*",
        "com.ultra.trafficagent.mitm.DynamicSniKeyManager",
        "com.ultra.trafficagent.mitm.CaCertificateAuthority",
    ))
    mutators.set(listOf("DEFAULTS"))
    outputFormats.set(listOf("XML", "HTML"))
    threads.set(1)
}
