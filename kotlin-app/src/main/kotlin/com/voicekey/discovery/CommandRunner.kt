package com.voicekey.discovery

fun interface CommandRunner {
    fun run(command: List<String>): String
}

object SystemCommandRunner : CommandRunner {
    override fun run(command: List<String>): String {
        return runCatching {
            val process = ProcessBuilder(command)
                .redirectErrorStream(true)
                .start()

            process.inputStream.bufferedReader().use { it.readText() }.also {
                process.waitFor()
            }
        }.getOrDefault("")
    }
}
