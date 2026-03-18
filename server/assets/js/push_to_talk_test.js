import { JSDOM } from "jsdom"

const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>")
global.window = dom.window
global.document = dom.window.document

class MockSpeechRecognition {
  constructor() {
    this.continuous = false
    this.interimResults = false
    this.lang = ""
    this.onresult = null
    this.onend = null
    this.onerror = null
    this.started = false
    this.stopped = false
  }
  start() { this.started = true }
  stop() { this.stopped = true }
  abort() { this.stopped = true }
}

const { default: PushToTalk } = await import("./push_to_talk.js")

function setup() {
  document.body.innerHTML = ""
  const btn = document.createElement("button")
  btn.id = "push-to-talk-btn"
  document.body.appendChild(btn)

  const display = document.createElement("div")
  display.id = "transcript"
  document.body.appendChild(display)

  const status = document.createElement("div")
  status.id = "status-text"
  document.body.appendChild(status)

  return { btn, display, status }
}

let passed = 0
let failed = 0
const results = []

function assert(condition, message) {
  if (condition) {
    passed++
    results.push(`  \u2713 ${message}`)
  } else {
    failed++
    results.push(`  \u2717 ${message}`)
  }
}

async function test(name, fn) {
  results.push(`\n${name}`)
  try {
    await fn()
  } catch (e) {
    failed++
    results.push(`  \u2717 Error: ${e.message}`)
  }
}

await test("PushToTalk initializes with SpeechRecognition", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  assert(ptt !== null, "creates PushToTalk instance")
  assert(ptt.isRecording === false, "starts in non-recording state")
  delete window.SpeechRecognition
})

await test("PushToTalk falls back to webkitSpeechRecognition", async () => {
  const { btn, display, status } = setup()
  window.webkitSpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  assert(ptt.recognition !== null, "uses webkitSpeechRecognition fallback")
  delete window.webkitSpeechRecognition
})

await test("PushToTalk handles missing SpeechRecognition gracefully", async () => {
  const { btn, display, status } = setup()
  delete window.SpeechRecognition
  delete window.webkitSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  assert(ptt.recognition === null, "recognition is null when API unavailable")
  assert(ptt.isRecording === false, "still initializes without error")
})

await test("startRecording sets recording state", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.startRecording()
  assert(ptt.isRecording === true, "isRecording becomes true")
  assert(ptt.recognition.started === true, "recognition.start() was called")
  delete window.SpeechRecognition
})

await test("stopRecording clears recording state", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.startRecording()
  ptt.stopRecording()
  assert(ptt.isRecording === false, "isRecording becomes false")
  assert(ptt.recognition.stopped === true, "recognition.stop() was called")
  delete window.SpeechRecognition
})

await test("onresult handler updates transcript", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.startRecording()

  const mockEvent = {
    results: [[{ transcript: "hello world" }]],
    resultIndex: 0
  }
  ptt.recognition.onresult(mockEvent)
  assert(ptt.transcript === "hello world", "transcript is updated from speech result")
  delete window.SpeechRecognition
})

await test("onresult handler updates DOM element", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.startRecording()

  const mockEvent = {
    results: [[{ transcript: "test dom update" }]],
    resultIndex: 0
  }
  ptt.recognition.onresult(mockEvent)
  assert(display.textContent === "test dom update", "DOM transcript element is updated")
  delete window.SpeechRecognition
})

await test("getTranscript returns accumulated text", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.transcript = "test transcript"
  assert(ptt.getTranscript() === "test transcript", "returns current transcript text")
  delete window.SpeechRecognition
})

await test("startRecording clears previous transcript", async () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.transcript = "old text"
  ptt.startRecording()
  assert(ptt.transcript === "", "transcript is cleared on new recording")
  assert(display.textContent === "", "DOM transcript element is cleared")
  delete window.SpeechRecognition
})

await test("copyTranscript writes to navigator clipboard when available", async () => {
  const { btn, display, status } = setup()
  const clipboard = { writeText: async (text) => { clipboard.last = text } }
  const ptt = new PushToTalk(btn, display, status, clipboard)
  ptt.transcript = "copy me"

  const result = await ptt.copyTranscript()

  assert(result === "copied", "returns copied when clipboard write succeeds")
  assert(clipboard.last === "copy me", "writes transcript to clipboard")
})

await test("copyTranscript reports unavailable when clipboard is missing", async () => {
  const { btn, display, status } = setup()
  const ptt = new PushToTalk(btn, display, status, null)
  ptt.transcript = "copy me"

  const result = await ptt.copyTranscript()

  assert(result === "unavailable", "returns unavailable without clipboard support")
})

await test("copyTranscript reports empty when transcript is blank", async () => {
  const { btn, display, status } = setup()
  const clipboard = { writeText: async () => {} }
  const ptt = new PushToTalk(btn, display, status, clipboard)
  ptt.transcript = "   "

  const result = await ptt.copyTranscript()

  assert(result === "empty", "returns empty when there is no transcript to copy")
})

console.log("\n=== Push-to-Talk JS Tests ===")
results.forEach(r => console.log(r))
console.log(`\n${passed} passed, ${failed} failed, ${passed + failed} total`)

if (failed > 0) {
  process.exit(1)
}
