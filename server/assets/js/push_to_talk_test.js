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

function test(name, fn) {
  results.push(`\n${name}`)
  try {
    fn()
  } catch (e) {
    failed++
    results.push(`  \u2717 Error: ${e.message}`)
  }
}

test("PushToTalk initializes with SpeechRecognition", () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  assert(ptt !== null, "creates PushToTalk instance")
  assert(ptt.isRecording === false, "starts in non-recording state")
  delete window.SpeechRecognition
})

test("PushToTalk falls back to webkitSpeechRecognition", () => {
  const { btn, display, status } = setup()
  window.webkitSpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  assert(ptt.recognition !== null, "uses webkitSpeechRecognition fallback")
  delete window.webkitSpeechRecognition
})

test("PushToTalk handles missing SpeechRecognition gracefully", () => {
  const { btn, display, status } = setup()
  delete window.SpeechRecognition
  delete window.webkitSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  assert(ptt.recognition === null, "recognition is null when API unavailable")
  assert(ptt.isRecording === false, "still initializes without error")
})

test("startRecording sets recording state", () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.startRecording()
  assert(ptt.isRecording === true, "isRecording becomes true")
  assert(ptt.recognition.started === true, "recognition.start() was called")
  delete window.SpeechRecognition
})

test("stopRecording clears recording state", () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.startRecording()
  ptt.stopRecording()
  assert(ptt.isRecording === false, "isRecording becomes false")
  assert(ptt.recognition.stopped === true, "recognition.stop() was called")
  delete window.SpeechRecognition
})

test("onresult handler updates transcript", () => {
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

test("onresult handler updates DOM element", () => {
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

test("getTranscript returns accumulated text", () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.transcript = "test transcript"
  assert(ptt.getTranscript() === "test transcript", "returns current transcript text")
  delete window.SpeechRecognition
})

test("startRecording clears previous transcript", () => {
  const { btn, display, status } = setup()
  window.SpeechRecognition = MockSpeechRecognition
  const ptt = new PushToTalk(btn, display, status)
  ptt.transcript = "old text"
  ptt.startRecording()
  assert(ptt.transcript === "", "transcript is cleared on new recording")
  assert(display.textContent === "", "DOM transcript element is cleared")
  delete window.SpeechRecognition
})

console.log("\n=== Push-to-Talk JS Tests ===")
results.forEach(r => console.log(r))
console.log(`\n${passed} passed, ${failed} failed, ${passed + failed} total`)

if (failed > 0) {
  process.exit(1)
}
