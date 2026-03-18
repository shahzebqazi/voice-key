import PushToTalk from "../push_to_talk"

const PushToTalkHook = {
  mounted() {
    const btn = this.el
    const transcriptEl = document.getElementById("transcript")
    const statusEl = document.getElementById("status-text")

    this.ptt = new PushToTalk(btn, null, statusEl)

    const startRecording = (e) => {
      e.preventDefault()
      this.ptt.startRecording()
      this.pushEvent("start_recording", {})
    }

    const stopRecording = (e) => {
      e.preventDefault()
      this.ptt.stopRecording()
      // Brief delay for final results from the speech API
      setTimeout(async () => {
        const transcript = this.ptt.getTranscript()
        const clipboard_status = await this.ptt.copyTranscript()
        this.pushEvent("stop_recording", { transcript, clipboard_status })
      }, 300)
    }

    btn.addEventListener("mousedown", startRecording)
    btn.addEventListener("mouseup", stopRecording)
    btn.addEventListener("mouseleave", (e) => {
      if (this.ptt.isRecording) stopRecording(e)
    })

    btn.addEventListener("touchstart", startRecording, { passive: false })
    btn.addEventListener("touchend", stopRecording, { passive: false })
    btn.addEventListener("touchcancel", stopRecording, { passive: false })
  },

  destroyed() {
    if (this.ptt && this.ptt.isRecording) {
      this.ptt.stopRecording()
    }
  }
}

export default PushToTalkHook
