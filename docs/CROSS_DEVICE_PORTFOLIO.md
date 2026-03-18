# Cross-Device Communication Portfolio

## Phase 1 Status

- Milestone: Android presence detection
- Branch: `gh-pages`
- Backend stack in progress: Kotlin + Ktor
- Discovery status: local Android phone detected via `_kdeconnect._udp`

## Current Proof Of Concept

The Kotlin discovery utility in the main application branch checks for Android
presence using:

- `adb devices` when wireless debugging is available
- `avahi-browse -rt _kdeconnect._udp` as a LAN-friendly fallback

This portfolio branch will be expanded with architecture notes, UI mock-ups,
and milestone summaries as the Kotlin server proof of concept grows.
