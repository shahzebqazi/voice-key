package com.voicekey.server

class SignalService(
    private val log: (String) -> Unit = ::println
) {
    fun record(message: String): String {
        val trimmed = message.trim().ifBlank { "Button Clicked" }
        log("[Device Signal]: $trimmed")
        return trimmed
    }
}
