defmodule VoiceKeyWeb.PushToTalkLive do
  use VoiceKeyWeb, :live_view
  require Logger

  @transcript_preview_limit 80

  @impl true
  def mount(_params, _session, socket) do
    Logger.info("[push_to_talk] mount phase=#{mount_phase(socket)}")

    {:ok,
     assign(socket,
       state: :idle,
       transcript: "",
       clipboard_status: nil
     )}
  end

  @impl true
  def handle_event("start_recording", _params, socket) do
    Logger.info("[push_to_talk] start_recording previous_state=#{socket.assigns.state}")

    {:noreply, assign(socket, state: :recording, transcript: "", clipboard_status: nil)}
  end

  @impl true
  def handle_event("stop_recording", params, socket) do
    transcript = Map.get(params, "transcript", "")
    clipboard_status = Map.get(params, "clipboard_status")
    new_state = if transcript == "", do: :idle, else: :done
    transcript_chars = String.length(transcript)

    Logger.info(
      "[push_to_talk] stop_recording transcript_chars=#{transcript_chars} clipboard_status=#{clipboard_status || "nil"} next_state=#{new_state}"
    )

    if transcript != "" do
      Logger.debug("[push_to_talk] transcript_preview=#{inspect(transcript_preview(transcript))}")
    end

    if clipboard_status == "unavailable" and transcript != "" do
      Logger.warning("[push_to_talk] browser clipboard unavailable for completed transcript")
    end

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

      <div id="transcript" class="ptt-transcript" aria-live="polite">
        <p id="transcript-text" class="transcript-text">{@transcript}</p>
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

  defp mount_phase(socket) do
    if connected?(socket), do: "connected", else: "disconnected"
  end

  defp transcript_preview(transcript) do
    transcript
    |> String.trim()
    |> String.replace(~r/\s+/, " ")
    |> String.slice(0, @transcript_preview_limit)
  end
end
