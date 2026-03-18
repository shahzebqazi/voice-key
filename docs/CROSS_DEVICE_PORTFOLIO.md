# Cross-Device Communication Portfolio

## Phase 1 Status

- Milestone: Android presence detection
- Branch: `gh-pages`
- Backend stack in progress: Kotlin + Ktor
- Discovery status: local Android phone detected via `_kdeconnect._udp`

## Phase 2 Status

- Milestone: Kotlin server bootstrap
- Bind address: `0.0.0.0:8080`
- Endpoint 1: `GET /` returns a Hello World page
- Endpoint 2: `POST /signal` accepts a client message and returns JSON
- Manual verification: local GET and POST requests passed against the running Ktor app

## Phase 3 Status

- Milestone: Android browser interaction flow
- CLI output: startup now prints both localhost and LAN URLs
- UI state: root page includes a large action button for the Android browser
- Server signal log: `[Device Signal]: Message Received from Android Client`
- Endpoint status: `GET /signal` reports readiness for client checks

## Current Proof Of Concept

The Kotlin discovery utility in the main application branch checks for Android
presence using:

- `adb devices` when wireless debugging is available
- `avahi-browse -rt _kdeconnect._udp` as a LAN-friendly fallback

This portfolio branch will be expanded with architecture notes, UI mock-ups,
and milestone summaries as the Kotlin server proof of concept grows.

## Included artifacts

- `CROSS_DEVICE_OVERVIEW.md`
- `CROSS_DEVICE_ARCHITECTURE.md`
- `CROSS_DEVICE_MOCKUPS.md`
