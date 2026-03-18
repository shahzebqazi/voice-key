defmodule VoiceKey.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application
  require Logger

  @impl true
  def start(_type, _args) do
    Logger.info("[voice_key] starting Phoenix server with verbose patch logging enabled")

    children = [
      VoiceKeyWeb.Telemetry,
      {DNSCluster, query: Application.get_env(:voice_key, :dns_cluster_query) || :ignore},
      {Phoenix.PubSub, name: VoiceKey.PubSub},
      # Start a worker by calling: VoiceKey.Worker.start_link(arg)
      # {VoiceKey.Worker, arg},
      # Start to serve requests, typically the last entry
      VoiceKeyWeb.Endpoint
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: VoiceKey.Supervisor]
    Logger.debug("[voice_key] supervisor strategy=#{opts[:strategy]} children=#{length(children)}")
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    Logger.info(
      "[voice_key] config change received changed_keys=#{map_size(changed)} removed_keys=#{length(removed)}"
    )

    VoiceKeyWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
