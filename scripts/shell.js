/**
 * Shell behavior for voice-key index.html: theme, disclosures, mockup iframes.
 * Adapted from vst-ui shell.js.
 */
(function () {
  var WIDE_MQ = "(min-width: 768px)";
  var mq = window.matchMedia(WIDE_MQ);
  var shell = document.getElementById("app-shell");
  var rightPanel = document.getElementById("right-panel");
  var phoneFrame = document.getElementById("phone-frame");
  var iframe = document.getElementById("mockup-iframe");
  var themeButtons = document.querySelectorAll("[data-theme]");
  var sizeButtons = document.querySelectorAll("[data-mockup-size]");
  var mockupLinks = document.querySelectorAll(".mockup-link");
  var disclosures = document.querySelectorAll(".nav-disclosure");
  var disclosureMockups = document.getElementById("disclosure-mockups");
  var overview = document.getElementById("shell-overview");
  var mockupFrameClose = document.getElementById("mockup-frame-close");
  var THEME_STORAGE_KEY = "voice-key-wallpaper";
  var THEME_CLASSES = ["bg-blueprint", "bg-paper", "bg-dark-dots"];

  var MOCKUP_SIZES = {
    phone: { className: "phone-frame--phone" },
    desktop: { className: "phone-frame--desktop" },
  };

  function countOpenDisclosures() {
    var n = 0;
    disclosures.forEach(function (d) { if (d.open) n++; });
    return n;
  }

  function anyDisclosureOpen() {
    return countOpenDisclosures() > 0;
  }

  function syncNavDensity() {
    shell.classList.toggle("app-shell--nav-compact", countOpenDisclosures() >= 3);
  }

  function mockupsSectionOpen() {
    return disclosureMockups && disclosureMockups.open;
  }

  function activeMockupLink() {
    return document.querySelector(".mockup-link.is-active");
  }

  function shouldShowMockupPanel() {
    return !!(mockupsSectionOpen() && activeMockupLink());
  }

  function syncOverviewVisibility() {
    var anyOpen = anyDisclosureOpen();
    if (overview) {
      overview.hidden = anyOpen;
      overview.setAttribute("aria-hidden", anyOpen ? "true" : "false");
    }
  }

  function applyLayout() {
    var wide = mq.matches;
    var split = shouldShowMockupPanel();
    shell.dataset.layoutWide = wide ? "true" : "false";
    shell.dataset.layoutSplit = split ? "true" : "false";
    shell.classList.remove("app-shell--intro", "app-shell--split-wide", "app-shell--split-narrow");
    if (!split) {
      shell.classList.add("app-shell--intro");
      rightPanel.setAttribute("aria-hidden", "true");
      rightPanel.hidden = true;
      phoneFrame.hidden = true;
    } else {
      rightPanel.hidden = false;
      rightPanel.setAttribute("aria-hidden", "false");
      phoneFrame.hidden = false;
      phoneFrame.setAttribute("aria-hidden", "false");
      shell.classList.add(wide ? "app-shell--split-wide" : "app-shell--split-narrow");
    }
  }

  function applyActiveMockupViewport() {
    if (!rightPanel || !shouldShowMockupPanel()) {
      phoneFrame.hidden = true;
      return;
    }
    var active = activeMockupLink();
    iframe.src = active.getAttribute("href");
    phoneFrame.hidden = false;
  }

  function clearMockup() {
    mockupLinks.forEach(function (l) { l.classList.remove("is-active"); });
    applyLayout();
    applyActiveMockupViewport();
  }

  function applyMockupSize(key) {
    var spec = MOCKUP_SIZES[key] || MOCKUP_SIZES.phone;
    phoneFrame.classList.remove("phone-frame--phone", "phone-frame--desktop");
    phoneFrame.classList.add(spec.className);
    phoneFrame.dataset.size = key;
    sizeButtons.forEach(function (b) {
      var on = b.getAttribute("data-mockup-size") === key;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function restoreThemeFromStorage() {
    var saved = localStorage.getItem(THEME_STORAGE_KEY);
    document.body.classList.remove("bg-blueprint", "bg-paper", "bg-dark-dots");
    if (saved && THEME_CLASSES.indexOf(saved) !== -1) {
      document.body.classList.add(saved);
    } else {
      document.body.classList.add("bg-blueprint");
    }
    themeButtons.forEach(function (b) {
      var t = b.getAttribute("data-theme");
      var on = document.body.classList.contains(t);
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  disclosures.forEach(function (d) {
    d.addEventListener("toggle", function () {
      syncOverviewVisibility();
      syncNavDensity();
      applyLayout();
      applyActiveMockupViewport();
    });
  });

  if (typeof mq.addEventListener === "function") {
    mq.addEventListener("change", applyLayout);
  } else {
    mq.addListener(applyLayout);
  }

  if (mockupFrameClose) {
    mockupFrameClose.addEventListener("click", function () { clearMockup(); });
  }

  themeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var theme = btn.getAttribute("data-theme");
      document.body.classList.remove("bg-blueprint", "bg-paper", "bg-dark-dots");
      document.body.classList.add(theme);
      try { localStorage.setItem(THEME_STORAGE_KEY, theme); } catch (e) {}
      themeButtons.forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
    });
  });

  sizeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      applyMockupSize(btn.getAttribute("data-mockup-size"));
    });
  });

  mockupLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (!mockupsSectionOpen()) return;
      e.preventDefault();
      mockupLinks.forEach(function (l) { l.classList.remove("is-active"); });
      link.classList.add("is-active");
      applyLayout();
      applyActiveMockupViewport();
    });
  });

  restoreThemeFromStorage();
  syncOverviewVisibility();
  syncNavDensity();
  var sizeKey = window.matchMedia("(max-width: 767px)").matches ? "phone" : "desktop";
  applyMockupSize(sizeKey);
  applyLayout();
  applyActiveMockupViewport();
})();
