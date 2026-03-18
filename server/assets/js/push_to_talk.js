export default class PushToTalk {
  constructor(button, transcriptEl, statusEl, clipboard = window.navigator?.clipboard) {
    this.button = button
    this.transcriptEl = transcriptEl
    this.statusEl = statusEl
    this.clipboard = clipboard
    this.isRecording = false
    this.transcript = ""

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition()
      this.recognition.continuous = true
      this.recognition.interimResults = true
      this.recognition.lang = "en-US"

      this.recognition.onresult = (event) => {
        let text = ""
        for (let i = 0; i < event.results.length; i++) {
          text += event.results[i][0].transcript
        }
        this.transcript = text
        if (this.transcriptEl) {
          this.transcriptEl.textContent = text
        }
      }

      this.recognition.onerror = (event) => {
        if (event.error !== "aborted") {
          console.error("Speech recognition error:", event.error)
        }
      }

      this.recognition.onend = () => {
        if (this.isRecording) {
          // Restarted unexpectedly — restart if still holding
          try { this.recognition.start() } catch (_e) { /* already started */ }
        }
      }
    } else {
      this.recognition = null
    }
  }

  startRecording() {
    this.isRecording = true
    this.transcript = ""
    if (this.transcriptEl) this.transcriptEl.textContent = ""
    if (this.recognition) {
      try { this.recognition.start() } catch (_e) { /* already started */ }
    }
  }

  stopRecording() {
    this.isRecording = false
    if (this.recognition) {
      this.recognition.stop()
    }
  }

  getTranscript() {
    return this.transcript
  }

  async copyTranscript() {
    const text = this.getTranscript().trim()

    if (text === "") {
      return "empty"
    }

    if (!this.clipboard || typeof this.clipboard.writeText !== "function") {
      return "unavailable"
    }

    try {
      await this.clipboard.writeText(text)
      return "copied"
    } catch (_error) {
      return "unavailable"
    }
  }
}
