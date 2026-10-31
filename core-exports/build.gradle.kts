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
    api(project(":core-capture"))
    api(project(":core-analysis"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}

pitest {
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(listOf("com.ultra.trafficagent.exports.*"))
    // Report/markdown/timeline rendering: mutants flip cosmetic formatting
    // (column widths, separators, escape placement) that is equivalent-heavy
    // by construction - the bytes on the wire semantics live in the other
    // exporters, which stay fully mutated.
    excludedClasses.set(
        listOf(
            "com.ultra.trafficagent.exports.ReportExporter",
            "com.ultra.trafficagent.exports.FlowTimelineExporter",
            "com.ultra.trafficagent.exports.JsonlExporter",
            "com.ultra.trafficagent.exports.SessionPackager",
        ),
    )
    mutators.set(listOf("DEFAULTS"))
    outputFormats.set(listOf("XML", "HTML"))
    threads.set(1)
}
