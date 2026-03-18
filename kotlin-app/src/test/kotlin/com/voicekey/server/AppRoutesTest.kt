package com.voicekey.server

import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import io.ktor.server.testing.testApplication
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class AppRoutesTest {
    @Test
    fun `root serves hello world page`() = testApplication {
        application {
            voiceKeyModule()
        }

        val response = client.get("/")

        assertEquals(HttpStatusCode.OK, response.status)
        assertTrue(response.bodyAsText().contains("Hello World"))
    }

    @Test
    fun `signal endpoint accepts button clicked message`() = testApplication {
        application {
            voiceKeyModule()
        }

        val response = client.post("/signal") {
            contentType(ContentType.Application.Json)
            setBody("""{"message":"Button Clicked"}""")
        }

        assertEquals(HttpStatusCode.OK, response.status)
        assertTrue(response.bodyAsText().contains("Button Clicked"))
    }

    @Test
    fun `server settings bind to all interfaces`() {
        assertEquals("0.0.0.0", ServerSettings.host)
        assertEquals(8080, ServerSettings.port)
    }
}
