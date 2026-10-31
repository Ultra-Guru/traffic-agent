plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "2.0.20" apply false
    id("org.jetbrains.kotlin.jvm") version "2.0.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.20" apply false
    id("info.solidsoft.pitest") version "1.15.0" apply false
    id("io.gitlab.arturbosch.detekt") version "1.23.6" apply false
}

tasks.register("allUnitTests") {
    group = "verification"
    description = "Run unit tests for all JVM core modules"
    dependsOn(
        ":core-capture:test",
        ":core-analysis:test",
        ":core-transform:test",
        ":core-agent:test",
        ":core-exports:test",
        ":core-mitm:test",
    )
}

tasks.register("allPitest") {
    group = "verification"
    description = "Run PIT mutation testing for all JVM core modules"
    dependsOn(
        ":core-capture:pitest",
        ":core-analysis:pitest",
        ":core-transform:pitest",
        ":core-agent:pitest",
        ":core-exports:pitest",
        ":core-mitm:pitest",
    )
}

// Static analysis for every included module (JVM cores + the Android app).
// Production sources only (test fixtures get a pass); per-module baselines
// keep pre-existing findings from failing the gate while new ones do.
subprojects {
    apply(plugin = "io.gitlab.arturbosch.detekt")

    configure<io.gitlab.arturbosch.detekt.extensions.DetektExtension> {
        toolVersion = "1.23.6"
        source.setFrom("src/main/kotlin")
        config.setFrom(rootProject.file("config/detekt.yml"))
        baseline = rootProject.file("config/detekt-baseline-${project.name}.xml")
        buildUponDefaultConfig = true
        parallel = true
    }
}
