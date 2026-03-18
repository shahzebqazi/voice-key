defmodule VoiceKeyWeb.PushToTalkLiveTest do
  use VoiceKeyWeb.ConnCase, async: true
  import Phoenix.LiveViewTest

  describe "GET /" do
    test "renders the push-to-talk page", %{conn: conn} do
      {:ok, _view, html} = live(conn, "/")

      assert html =~ "Voice Key"
      assert html =~ "push-to-talk-btn"
      assert html =~ "transcript"
    end

    test "page has mobile viewport meta tag", %{conn: conn} do
      conn = get(conn, "/")
      html = html_response(conn, 200)

      assert html =~ ~s(name="viewport")
      assert html =~ ~s(width=device-width)
    end

    test "page includes speech recognition JavaScript", %{conn: conn} do
      conn = get(conn, "/")
      html = html_response(conn, 200)

      assert html =~ "app.js"
    end
  end

  describe "LiveView interactions" do
    test "starts in idle state", %{conn: conn} do
      {:ok, _view, html} = live(conn, "/")

      assert html =~ "Hold to Talk"
      refute html =~ "recording"
    end

    test "transitions to recording state", %{conn: conn} do
      {:ok, view, _html} = live(conn, "/")

      html = render_click(view, "start_recording")
      assert html =~ "recording"
      assert html =~ "Listening"
    end

    test "transitions to done state and shows transcript", %{conn: conn} do
      {:ok, view, _html} = live(conn, "/")

      render_click(view, "start_recording")
      html =
        render_click(view, "stop_recording", %{
          "transcript" => "hello world",
          "clipboard_status" => "copied"
        })

      assert html =~ "hello world"
      assert html =~ "Copied to clipboard"
      refute html =~ "recording"
    end

    test "can start a new recording after completing one", %{conn: conn} do
      {:ok, view, _html} = live(conn, "/")

      render_click(view, "start_recording")
      render_click(view, "stop_recording", %{"transcript" => "first"})

      html = render_click(view, "start_recording")
      assert html =~ "recording"
      assert html =~ "Listening"
    end

    test "handles empty transcript on stop", %{conn: conn} do
      {:ok, view, _html} = live(conn, "/")

      render_click(view, "start_recording")
      html = render_click(view, "stop_recording", %{"transcript" => ""})

      assert html =~ "Hold to Talk"
    end

    test "shows clipboard warning when browser copy is unavailable", %{conn: conn} do
      {:ok, view, _html} = live(conn, "/")

      render_click(view, "start_recording")

      html =
        render_click(view, "stop_recording", %{
          "transcript" => "hello world",
          "clipboard_status" => "unavailable"
        })

      assert html =~ "Clipboard unavailable on this browser"
    end
  end
end
