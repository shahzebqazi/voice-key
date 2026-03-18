# Menu inventory — Voice Hotkey

Shell header structure and mockup inventory for the GitHub Pages site.

---

## Header menu (`index.html`)

| Folder | Control | Content |
|--------|---------|---------|
| `viewport/` | `data-menu-target="panel-viewport"` | Viewport size controls (Phone, Desktop) |
| `mockups/` | `data-menu-target="panel-mockups"` | Settings, Recording Flow, Future Features |
| `documents/` | `data-menu-target="panel-documents"` | Executive overview, Software requirements, Design guide |

The header uses a horizontal file-structure bar. Clicking a folder expands its panel below the bar, and clicking it again contracts the panel.

---

## Mockup inventory

| Mockup | File | Description | Status |
|--------|------|-------------|--------|
| Settings | `mockups/settings.html` | Key binding selector, Whisper model, output target | Done |
| Recording Flow | `mockups/recording-flow.html` | Double-click → record → transcribe → clipboard | Done |
| Future Features | `mockups/future.html` | TTS, autocomplete, autocorrect, multi-platform | Done |

---

## Document inventory

| Document | File | Audience |
|----------|------|----------|
| Executive overview | `documents/executive-overview.html` | Leadership, sponsors |
| Software requirements | `documents/software-requirements.html` | Engineering leadership |
| Design guide | `documents/design-guide.html` | Product, design, engineering |

---

## Viewport sizes

| Size | Dimensions | CSS class |
|------|-----------|-----------|
| Phone | 390×844 | `phone-frame--phone` |
| Desktop | 960×600 | `phone-frame--desktop` |
