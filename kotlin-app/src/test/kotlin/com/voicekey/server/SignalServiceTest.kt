package com.voicekey.server

import kotlin.test.Test
import kotlin.test.assertEquals

class SignalServiceTest {
    @Test
    fun `records exact Android client log message`() {
        val logMessages = mutableListOf<String>()
        val service = SignalService(logMessages::add)

        val echoed = service.record("Button Clicked")

        assertEquals("Button Clicked", echoed)
        assertEquals(
            listOf("[Device Signal]: Message Received from Android Client"),
            logMessages
        )
    }
}
