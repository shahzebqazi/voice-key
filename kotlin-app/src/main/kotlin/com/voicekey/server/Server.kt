package com.voicekey.server

import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.application.call
import io.ktor.server.engine.embeddedServer
import io.ktor.server.html.respondHtml
import io.ktor.server.netty.Netty
import io.ktor.server.request.receiveText
import io.ktor.server.response.respondText
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import kotlinx.html.body
import kotlinx.html.button
import kotlinx.html.div
import kotlinx.html.h1
import kotlinx.html.head
import kotlinx.html.id
import kotlinx.html.meta
import kotlinx.html.script
import kotlinx.html.style
import kotlinx.html.title
import kotlinx.html.unsafe

fun main() {
    embeddedServer(
        factory = Netty,
        host = ServerSettings.host,
        port = ServerSettings.port,
        module = Application::voiceKeyModule
    ).start(wait = true)
}

fun Application.voiceKeyModule() {
    val signalService = SignalService()

    routing {
        get("/") {
            call.respondHtml(HttpStatusCode.OK) {
                head {
                    title { +"Hello World" }
                    meta(name = "viewport", content = "width=device-width, initial-scale=1")
                    style {
                        unsafe {
                            +"""
                            body { font-family: sans-serif; margin: 2rem; background: #f5f5f5; }
                            div { max-width: 28rem; margin: 0 auto; text-align: center; }
                            button { min-width: 220px; min-height: 72px; font-size: 1.25rem; border-radius: 9999px; border: none; background: #2563eb; color: white; }
                            """.trimIndent()
                        }
                    }
                }
                body {
                    div {
                        h1 { +"Hello World" }
                        button {
                            id = "signal-button"
                            +"Action Button"
                        }
                    }
                    script {
                        unsafe {
                            +"""
                            const button = document.getElementById("signal-button");
                            if (button) {
                              button.addEventListener("click", async () => {
                                await fetch("/signal", {
                                  method: "POST",
                                  headers: {"Content-Type": "application/json"},
                                  body: JSON.stringify({message: "Button Clicked"})
                                });
                              });
                            }
                            """.trimIndent()
                        }
                    }
                }
            }
        }

        post("/signal") {
            val body = call.receiveText()
            val message = Regex("\"message\"\\s*:\\s*\"([^\"]+)\"")
                .find(body)
                ?.groupValues
                ?.get(1)
                ?: "Button Clicked"

            val recorded = signalService.record(message)
            call.respondText(
                text = """{"status":"ok","message":"$recorded"}""",
                contentType = ContentType.Application.Json
            )
        }
    }
}
