package com.voicekey.discovery

fun main() {
    val result = AndroidDeviceDetector().discover()

    if (!result.present) {
        println("[Android Discovery] No Android device detected on the local network.")
        return
    }

    println("[Android Discovery] ${result.devices.size} Android device(s) detected.")
    result.devices.forEach { device ->
        val label = device.name ?: "Unknown"
        println("[Android Discovery] $label @ ${device.address} via ${device.source}")
    }
}
