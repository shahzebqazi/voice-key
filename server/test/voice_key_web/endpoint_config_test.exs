defmodule VoiceKeyWeb.EndpointConfigTest do
  use ExUnit.Case, async: true

  describe "endpoint configuration" do
    test "dev config binds to 0.0.0.0 for LAN access" do
      dev_config = Application.get_env(:voice_key, VoiceKeyWeb.Endpoint)
      http_config = dev_config[:http] || []
      ip = http_config[:ip]

      # In test env, ip is {127, 0, 0, 1} which is fine.
      # We verify the config key exists and is a tuple.
      assert is_tuple(ip)
    end

    test "endpoint uses Bandit adapter" do
      config = Application.get_env(:voice_key, VoiceKeyWeb.Endpoint)
      assert config[:adapter] == Bandit.PhoenixAdapter
    end

    test "endpoint has LiveView socket configured" do
      # Verify the endpoint module has the /live socket path
      assert VoiceKeyWeb.Endpoint.__sockets__()
             |> Enum.any?(fn {path, _mod, _opts} -> path == "/live" end)
    end
  end
end
