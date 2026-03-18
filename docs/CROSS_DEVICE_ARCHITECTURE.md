# Cross-Device Communication Architecture

## Communication flow

1. The Kotlin discovery utility checks for a reachable Android phone.
2. The Ktor server starts on `0.0.0.0:8080`.
3. The server prints localhost and LAN URLs to the CLI.
4. The Android browser opens the LAN URL.
5. The browser UI loads a Hello World page with a large action button.
6. Button press triggers `POST /signal`.
7. The server logs `[Device Signal]: Message Received from Android Client`.

## Components

- `kotlin-app/src/main/kotlin/com/voicekey/discovery/`
- `kotlin-app/src/main/kotlin/com/voicekey/server/`
- `docs/`
