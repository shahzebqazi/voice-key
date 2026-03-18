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

## Current Proof Of Concept

The Kotlin discovery utility in the main application branch checks for Android
presence using:

- `adb devices` when wireless debugging is available
- `avahi-browse -rt _kdeconnect._udp` as a LAN-friendly fallback

This portfolio branch will be expanded with architecture notes, UI mock-ups,
and milestone summaries as the Kotlin server proof of concept grows.
