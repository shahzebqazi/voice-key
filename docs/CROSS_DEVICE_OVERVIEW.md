# Cross-Device Communication Overview

## Goal

Build a lightweight portfolio-ready proof of concept that lets this repository
talk to a local Android device over the LAN.

## Current scope

- Detect Android presence on the local network
- Run a Kotlin Ktor server on `0.0.0.0:8080`
- Serve a minimal browser UI with a large action button
- Accept a browser signal and log server-side receipt

## Current milestones

1. Android discovery via `adb devices` and `_kdeconnect._udp`
2. Minimal Ktor Netty server with `GET /` and `POST /signal`
3. Android-friendly interaction flow with LAN URL output and readiness checks
