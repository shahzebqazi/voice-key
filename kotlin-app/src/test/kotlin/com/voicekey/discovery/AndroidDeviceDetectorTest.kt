package com.voicekey.discovery

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class AndroidDeviceDetectorTest {
    @Test
    fun `parses adb devices output for connected Android device`() {
        val adbOutput = """
            List of devices attached
            192.168.5.14:40139	device
        """.trimIndent()

        val devices = AndroidDeviceDetector.parseAdbDevices(adbOutput)

        assertEquals(1, devices.size)
        assertEquals("192.168.5.14:40139", devices.first().address)
        assertEquals(DeviceSource.ADB, devices.first().source)
    }

    @Test
    fun `parses avahi kdeconnect output for Android phone`() {
        val avahiOutput = """
            =   eth0 IPv4 2b97a94200144dbf8e959b79cf36f327              _kdeconnect._udp     local
               hostname = [Android_KUIXOQV7.local]
               address = [192.168.5.14]
               port = [1716]
               txt = ["type=phone" "name=Q25" "id=2b97a94200144dbf8e959b79cf36f327" "protocol=8"]
        """.trimIndent()

        val devices = AndroidDeviceDetector.parseAvahiBrowse(avahiOutput)

        assertEquals(1, devices.size)
        assertEquals("192.168.5.14", devices.first().address)
        assertEquals("Q25", devices.first().name)
        assertEquals(DeviceSource.MDNS, devices.first().source)
    }

    @Test
    fun `prefers adb results when both adb and mdns find the same phone`() {
        val detector = AndroidDeviceDetector(
            commandRunner = object : CommandRunner {
                override fun run(command: List<String>): String =
                    when (command.first()) {
                        "adb" -> """
                            List of devices attached
                            192.168.5.14:40139	device
                        """.trimIndent()

                        "avahi-browse" -> """
                            =   eth0 IPv4 2b97a94200144dbf8e959b79cf36f327              _kdeconnect._udp     local
                               hostname = [Android_KUIXOQV7.local]
                               address = [192.168.5.14]
                               port = [1716]
                               txt = ["type=phone" "name=Q25" "id=2b97a94200144dbf8e959b79cf36f327" "protocol=8"]
                        """.trimIndent()

                        else -> ""
                    }
            }
        )

        val result = detector.discover()

        assertTrue(result.present)
        assertEquals(1, result.devices.size)
        assertEquals(DeviceSource.ADB, result.devices.first().source)
    }

    @Test
    fun `treats unresolved kdeconnect broadcasts as android presence`() {
        val detector = AndroidDeviceDetector(
            commandRunner = object : CommandRunner {
                override fun run(command: List<String>): String =
                    when (command.first()) {
                        "adb" -> "List of devices attached"
                        "avahi-browse" -> """
                            +   eth0 IPv4 2b97a94200144dbf8e959b79cf36f327              _kdeconnect._udp     local
                            Failed to resolve service '2b97a94200144dbf8e959b79cf36f327' of type '_kdeconnect._udp' in domain 'local': Timeout reached
                        """.trimIndent()

                        else -> ""
                    }
            }
        )

        val result = detector.discover()

        assertTrue(result.present)
        assertEquals(1, result.devices.size)
        assertEquals("2b97a94200144dbf8e959b79cf36f327.local", result.devices.first().address)
        assertEquals(DeviceSource.MDNS, result.devices.first().source)
    }

    @Test
    fun `returns not present when no android device is found`() {
        val detector = AndroidDeviceDetector(
            commandRunner = object : CommandRunner {
                override fun run(command: List<String>): String = "List of devices attached"
            }
        )

        val result = detector.discover()

        assertFalse(result.present)
        assertTrue(result.devices.isEmpty())
    }
}
