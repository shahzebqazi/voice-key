(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.BuildStatus = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function shortBuildId(value) {
    if (typeof value !== "string") return null;
    var n = value.trim();
    return n ? n.slice(0, 7) : null;
  }

  function buildCommitApiUrl(config) {
    var owner = config && config.owner ? config.owner : "";
    var repo = config && config.repo ? config.repo : "";
    var branch = config && config.branch ? config.branch : "main";
    return "https://api.github.com/repos/" + owner + "/" + repo + "/commits/" + branch;
  }

  function formatBuildStatusText(config, commit) {
    var label = config && config.label ? config.label : "GitHub Pages";
    var buildId = shortBuildId(commit && commit.sha) || shortBuildId(config && config.fallbackBuildId);
    return buildId ? label + ": build " + buildId : label + ": build unavailable";
  }

  function buildRefreshUrl(currentUrl, buildId) {
    if (typeof URL !== "function") return currentUrl;
    var nextUrl = new URL(currentUrl, currentUrl);
    nextUrl.searchParams.set("refresh", shortBuildId(buildId) || String(Date.now()));
    return nextUrl.toString();
  }

  async function fetchJson(fetchImpl, url, options) {
    var response = await fetchImpl(url, options);
    if (!response.ok) throw new Error("Request failed: " + response.status);
    return response.json();
  }

  function applyStatusText(target, text, state) {
    if (!target) return;
    target.textContent = text;
    target.dataset.statusState = state;
  }

  function updateRefreshLink(link, buildId) {
    if (!link) return;
    link.href = buildRefreshUrl(window.location.href, buildId || "");
    link.dataset.buildId = shortBuildId(buildId || "") || "latest";
  }

  async function initBuildStatus(target, fetchImpl) {
    if (!target || typeof fetchImpl !== "function") return;
    var configUrl = target.getAttribute("data-build-status-url") || "build-status.json";
    var refreshLink = document.getElementById("pages-status-refresh");
    var config;
    try {
      config = await fetchJson(fetchImpl, configUrl, { cache: "no-store" });
    } catch (e) {
      applyStatusText(target, "GitHub Pages: build unavailable", "error");
      updateRefreshLink(refreshLink, "");
      return;
    }
    applyStatusText(target, formatBuildStatusText(config), "loading");
    updateRefreshLink(refreshLink, config.fallbackBuildId);
    try {
      var commit = await fetchJson(fetchImpl, buildCommitApiUrl(config), {
        cache: "no-store",
        headers: { Accept: "application/vnd.github+json" },
      });
      applyStatusText(target, formatBuildStatusText(config, commit), "ready");
      updateRefreshLink(refreshLink, commit && commit.sha);
    } catch (e) {
      applyStatusText(target, formatBuildStatusText(config), "fallback");
      updateRefreshLink(refreshLink, config.fallbackBuildId);
    }
  }

  var api = {
    shortBuildId: shortBuildId,
    buildCommitApiUrl: buildCommitApiUrl,
    buildRefreshUrl: buildRefreshUrl,
    formatBuildStatusText: formatBuildStatusText,
    initBuildStatus: initBuildStatus,
  };

  if (typeof window !== "undefined" && typeof document !== "undefined") {
    var target = document.getElementById("pages-status");
    if (target && typeof window.fetch === "function") {
      api.initBuildStatus(target, window.fetch.bind(window));
    }
  }

  return api;
});
