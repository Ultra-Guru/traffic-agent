plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "2.0.20" apply false
    id("org.jetbrains.kotlin.jvm") version "2.0.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.20" apply false
    id("info.solidsoft.pitest") version "1.15.0" apply false
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
    )
}
