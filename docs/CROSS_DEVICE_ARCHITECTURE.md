# Cross-Device Communication Architecture

## Communication flow

1. The Kotlin discovery utility checks for a reachable Android phone.
2. The Ktor server starts on `0.0.0.0:8080`.
3. The server prints the localhost URL and first LAN IPv4 URL to the CLI.
4. The Android browser opens the LAN URL.
5. The browser UI loads a simple Hello World page with a large action button.
6. Button press triggers `POST /signal` with a JSON message.
7. The server logs `[Device Signal]: Message Received from Android Client`.

## Components

- `kotlin-app/src/main/kotlin/com/voicekey/discovery/`
  Android detection and CLI logging
- `kotlin-app/src/main/kotlin/com/voicekey/server/`
  Ktor server, LAN configuration, and signal handling
- `docs/`
  Portfolio overview, architecture notes, and mock-ups

## Transport notes

- Discovery uses `adb` when available
- Fallback discovery uses mDNS service browsing for `_kdeconnect._udp`
- Client-to-server communication uses plain HTTP on the local network
