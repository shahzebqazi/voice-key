# Voice Key Phoenix Server

LAN-accessible Phoenix LiveView server for the Voice Hotkey push-to-talk web UI.

## Features

- Mobile-first push-to-talk screen at `/`
- Browser speech recognition while the button is held
- Transcript shown on release
- Browser clipboard copy on release, with a visible success/unavailable status

## Development

To start your Phoenix server:

- Run `mix setup` to install and set up dependencies
- Start the endpoint with `mix phx.server` or `iex -S mix phx.server`

By default the app runs on [`http://localhost:4000`](http://localhost:4000).

For LAN access in development, start it with:

```bash
PHX_SERVER=true mix phx.server
```

## Client-side tests

Run the push-to-talk JavaScript tests with:

```bash
node assets/js/push_to_talk_test.js
```
