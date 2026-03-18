package com.voicekey.discovery

enum class DeviceSource {
    ADB,
    MDNS
}

data class AndroidDevice(
    val address: String,
    val name: String? = null,
    val source: DeviceSource
)

data class DiscoveryResult(
    val devices: List<AndroidDevice>
) {
    val present: Boolean
        get() = devices.isNotEmpty()
}
