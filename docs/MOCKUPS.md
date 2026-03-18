# Mockup flow diagrams — Voice Hotkey

Mermaid diagrams for the voice-hotkey recording flow and application architecture.

---

## 1. Recording flow

```mermaid
flowchart TD
    A[Idle — Listening] -->|Double-tap Right Ctrl| B[Recording]
    B -->|Double-tap Right Ctrl| C[Stop Recording]
    B -->|Timeout 30s| C
    C --> D[Transcribe with Whisper]
    D --> E{Speech detected?}
    E -->|Yes| F[Copy to Clipboard]
    E -->|No| G[Print 'No speech detected']
    F --> A
    G --> A
```

---

## 2. Application architecture

```mermaid
graph LR
    subgraph Input
        K[Keyboard] --> HL[pynput Listener]
        M[Microphone] --> SD[sounddevice]
    end

    subgraph Processing
        HL -->|double-tap event| CTRL[Controller]
        CTRL -->|start/stop| SD
        SD -->|audio buffer| W[Whisper]
        W -->|text| CB[Clipboard]
    end

    subgraph Output
        CB --> OS[System Clipboard]
    end

    subgraph Config
        CFG[config.toml] -.->|settings| CTRL
        CFG -.->|model, language| W
        CFG -.->|key, interval| HL
    end
```

---

## 3. Double-tap detection

```mermaid
sequenceDiagram
    participant U as User
    participant L as Listener
    participant R as Recorder

    U->>L: Release Right Ctrl
    L->>L: Record timestamp t1
    U->>L: Release Right Ctrl
    L->>L: Record timestamp t2
    L->>L: Check (t2 - t1) ≤ 400ms?
    alt Valid double-tap
        L->>R: Toggle recording
    else Too slow
        L->>L: Reset, wait for next
    end
```

---

## 4. State machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Recording : double_tap
    Recording --> Transcribing : double_tap / timeout
    Transcribing --> Copying : text_ready
    Transcribing --> Idle : no_speech
    Copying --> Idle : done
```
