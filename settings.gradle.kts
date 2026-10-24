// When developing from networks throttled by repo.maven.apache.org (429),
// export TA_USE_CN_MIRRORS=1 to resolve through the Aliyun mirrors first.
// CI keeps the official repositories (no env var set there).

pluginManagement {
    repositories {
        if (System.getenv("TA_USE_CN_MIRRORS") == "1") {
            maven { url = uri("https://maven.aliyun.com/repository/gradle-plugin") }
            maven { url = uri("https://maven.aliyun.com/repository/google") }
            maven { url = uri("https://maven.aliyun.com/repository/public") }
        }
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        if (System.getenv("TA_USE_CN_MIRRORS") == "1") {
            maven { url = uri("https://maven.aliyun.com/repository/google") }
            maven { url = uri("https://maven.aliyun.com/repository/public") }
        }
        google()
        mavenCentral()
    }
}

rootProject.name = "traffic-agent"

include(":app")
include(":core-capture")
include(":core-analysis")
include(":core-transform")
include(":core-agent")
include(":core-exports")
