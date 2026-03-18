defmodule VoiceKeyWeb.PageControllerTest do
  use VoiceKeyWeb.ConnCase

  test "GET / returns 200 and renders LiveView", %{conn: conn} do
    conn = get(conn, ~p"/")
    assert html_response(conn, 200) =~ "Voice Key"
  end
end
