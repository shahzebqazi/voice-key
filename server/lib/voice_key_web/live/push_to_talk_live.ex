defmodule VoiceKeyWeb.PushToTalkLive do
  use VoiceKeyWeb, :live_view

  @impl true
  def mount(_params, _session, socket) do
    {:ok,
     assign(socket,
       state: :idle,
       transcript: "",
       clipboard_status: nil
     )}
  end

  @impl true
  def handle_event("start_recording", _params, socket) do
    {:noreply, assign(socket, state: :recording, transcript: "", clipboard_status: nil)}
  end

  @impl true
  def handle_event("stop_recording", params, socket) do
    transcript = Map.get(params, "transcript", "")
    clipboard_status = Map.get(params, "clipboard_status")
    new_state = if transcript == "", do: :idle, else: :done

    {:noreply,
     assign(socket,
       state: new_state,
       transcript: transcript,
       clipboard_status: clipboard_status
     )}
  end

  @impl true
  def render(assigns) do
    ~H"""
    <div id="push-to-talk" class="ptt-container">
      <div class="ptt-header">
        <h1>Voice Key</h1>
      </div>

      <div id="transcript" class="ptt-transcript">
        <p :if={@transcript != ""} class="transcript-text">{@transcript}</p>
        <p :if={@transcript == "" && @state == :idle} class="transcript-placeholder">
          Tap and hold to speak
        </p>
      </div>

      <p :if={@clipboard_status == "copied"} id="clipboard-status" class="ptt-copy-status success">
        Copied to clipboard
      </p>
      <p
        :if={@clipboard_status == "unavailable" && @transcript != ""}
        id="clipboard-status"
        class="ptt-copy-status warning"
      >
        Clipboard unavailable on this browser
      </p>

      <div class="ptt-button-area">
        <div id="status-text" class="ptt-status">
          <%= case @state do %>
            <% :idle -> %>Hold to Talk
            <% :recording -> %>Listening...
            <% :done -> %>Done
          <% end %>
        </div>

        <button
          id="push-to-talk-btn"
          class={"ptt-btn #{@state}"}
          phx-hook="PushToTalk"
          aria-label="Push to talk"
        >
          <span class="ptt-btn-icon">
            <%= case @state do %>
              <% :recording -> %>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              <% _ -> %>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
            <% end %>
          </span>
        </button>
      </div>
    </div>
    """
  end
end
