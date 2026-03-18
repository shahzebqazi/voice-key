package com.voicekey.discovery

class AndroidDeviceDetector(
    private val commandRunner: CommandRunner = SystemCommandRunner
) {
    fun discover(): DiscoveryResult {
        val adbDevices = parseAdbDevices(commandRunner.run(listOf("adb", "devices")))
        val mdnsDevices =
            parseAvahiBrowse(
                commandRunner.run(listOf("avahi-browse", "-rt", "_kdeconnect._udp"))
            )

        val merged = LinkedHashMap<String, AndroidDevice>()

        adbDevices.forEach { merged[it.address.substringBefore(":")] = it }
        mdnsDevices.forEach { device ->
            merged.putIfAbsent(device.address, device)
        }

        return DiscoveryResult(merged.values.toList())
    }

    companion object {
        fun parseAdbDevices(output: String): List<AndroidDevice> {
            return output.lineSequence()
                .map(String::trim)
                .filter { it.isNotBlank() && !it.startsWith("List of devices attached") }
                .mapNotNull { line ->
                    val parts = line.split(Regex("\\s+"))
                    if (parts.size >= 2 && parts[1] == "device") {
                        AndroidDevice(
                            address = parts[0],
                            source = DeviceSource.ADB
                        )
                    } else {
                        null
                    }
                }
                .toList()
        }

        fun parseAvahiBrowse(output: String): List<AndroidDevice> {
            val results = mutableListOf<AndroidDevice>()
            var address: String? = null
            var name: String? = null
            var type: String? = null
            val unresolvedServices = mutableListOf<String>()

            output.lineSequence().forEach { rawLine ->
                val line = rawLine.trim()

                when {
                    line.startsWith("+") && line.contains("_kdeconnect._udp") -> {
                        unresolvedServices += line.split(Regex("\\s+"))[3]
                    }

                    line.startsWith("address = [") -> {
                        address = line.removePrefix("address = [").removeSuffix("]")
                    }

                    line.startsWith("txt = [") -> {
                        val txt = line.removePrefix("txt = [").removeSuffix("]")
                        name = Regex("\"name=([^\"]+)\"").find(txt)?.groupValues?.get(1)
                        type = Regex("\"type=([^\"]+)\"").find(txt)?.groupValues?.get(1)

                        if (type == "phone" && address != null) {
                            results += AndroidDevice(
                                address = address!!,
                                name = name,
                                source = DeviceSource.MDNS
                            )
                        }

                        address = null
                        name = null
                        type = null
                    }
                }
            }

            val resolved = results.distinctBy { it.address }

            if (resolved.isNotEmpty()) {
                return resolved
            }

            return unresolvedServices.distinct().map { serviceId ->
                AndroidDevice(
                    address = "$serviceId.local",
                    name = null,
                    source = DeviceSource.MDNS
                )
            }
        }
    }
}
