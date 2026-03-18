defmodule VoiceKeyWeb.PageController do
  use VoiceKeyWeb, :controller

  def home(conn, _params) do
    render(conn, :home)
  end
end
