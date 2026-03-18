package com.voicekey.server

import java.net.NetworkInterface

object LanAddressResolver {
    fun firstIpv4Address(): String? {
        return NetworkInterface.getNetworkInterfaces()
            .toList()
            .asSequence()
            .filter { it.isUp && !it.isLoopback && !it.isVirtual }
            .flatMap { it.inetAddresses.toList().asSequence() }
            .filter { address ->
                !address.isLoopbackAddress &&
                    !address.isLinkLocalAddress &&
                    address.hostAddress.contains(".")
            }
            .map { it.hostAddress }
            .firstOrNull()
    }
}
