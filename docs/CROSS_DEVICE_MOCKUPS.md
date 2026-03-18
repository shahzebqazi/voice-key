# Cross-Device Communication Mock-ups

## Client interaction

```mermaid
flowchart TD
    A[Android browser opens LAN URL] --> B[Hello World page loads]
    B --> C[User taps large action button]
    C --> D[POST /signal]
    D --> E[Server logs device signal]
```

## Layout sketch

```mermaid
flowchart TD
    Screen[Android Browser Viewport]
    Screen --> Header[Hello World Header]
    Screen --> Button[Large Action Button]
    Screen --> Status[Ready / Signal Status]
```

## Server-side sequence

```mermaid
sequenceDiagram
    participant CLI as Kotlin CLI
    participant Server as Ktor Server
    participant Phone as Android Browser

    CLI->>Server: Start on 0.0.0.0:8080
    Server-->>CLI: Print localhost + LAN URL
    Phone->>Server: GET /
    Server-->>Phone: Hello World + action button
    Phone->>Server: POST /signal
    Server-->>CLI: [Device Signal]: Message Received from Android Client
```
