plugins {
    kotlin("jvm") version "1.9.24"
    application
}

repositories {
    mavenCentral()
}

val ktorVersion = "2.3.12"

dependencies {
    implementation("io.ktor:ktor-server-core-jvm:$ktorVersion")
    implementation("io.ktor:ktor-server-netty-jvm:$ktorVersion")
    implementation("io.ktor:ktor-server-html-builder-jvm:$ktorVersion")
    implementation("io.ktor:ktor-server-content-negotiation-jvm:$ktorVersion")
    implementation("ch.qos.logback:logback-classic:1.5.8")

    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
    testImplementation("io.ktor:ktor-server-test-host-jvm:$ktorVersion")
}

application {
    mainClass.set("com.voicekey.server.ServerKt")
}

tasks.test {
    useJUnitPlatform()
}

tasks.register<JavaExec>("detectAndroid") {
    group = "application"
    description = "Detects Android devices on the local network."
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.voicekey.discovery.DetectAndroidDeviceKt")
}
