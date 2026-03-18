/**
 * Shell behavior for voice-key index.html: horizontal file-tree header, viewport sizing,
 * and mockup iframe loading.
 */
(function () {
  var WIDE_MQ = "(min-width: 960px)";
  var mq = window.matchMedia(WIDE_MQ);
  var shell = document.getElementById("app-shell");
  var header = document.getElementById("shell-header");
  var rightPanel = document.getElementById("right-panel");
  var phoneFrame = document.getElementById("phone-frame");
  var iframe = document.getElementById("mockup-iframe");
  var overview = document.getElementById("shell-overview");
  var mockupFrameClose = document.getElementById("mockup-frame-close");
  var menuButtons = document.querySelectorAll("[data-menu-target]");
  var menuPanels = document.querySelectorAll("[data-menu-panel]");
  var sizeButtons = document.querySelectorAll("[data-mockup-size]");
  var mockupLinks = document.querySelectorAll(".mockup-link");
  var docLinks = document.querySelectorAll(".doc-link");
  var MOCKUP_SIZES = {
    phone: { className: "phone-frame--phone" },
    desktop: { className: "phone-frame--desktop" },
  };

  function activeMenuId() {
    var active = document.querySelector(".tree-nav__tab.is-active");
    return active ? active.getAttribute("data-menu-target") : null;
  }

  function activeMockupLink() {
    return document.querySelector(".mockup-link.is-active");
  }

  function shouldShowMockupPanel() {
    return !!activeMockupLink();
  }

  function setActiveMenu(id) {
    menuButtons.forEach(function (btn) {
      var on = !!id && btn.getAttribute("data-menu-target") === id;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-expanded", on ? "true" : "false");
    });

    menuPanels.forEach(function (panel) {
      var on = !!id && panel.id === id;
      panel.hidden = !on;
      panel.classList.toggle("is-active", on);
    });

    syncOverviewVisibility();
  }

  function syncOverviewVisibility() {
    if (!overview) return;
    var expanded = !!activeMenuId();
    overview.hidden = expanded;
    overview.setAttribute("aria-hidden", expanded ? "true" : "false");
  }

  function applyLayout() {
    var split = shouldShowMockupPanel();
    shell.dataset.layoutWide = mq.matches ? "true" : "false";
    shell.dataset.layoutSplit = split ? "true" : "false";
    shell.classList.remove("app-shell--intro", "app-shell--split-wide", "app-shell--split-narrow");

    if (!split) {
      shell.classList.add("app-shell--intro");
      rightPanel.hidden = true;
      rightPanel.setAttribute("aria-hidden", "true");
      phoneFrame.hidden = true;
      phoneFrame.setAttribute("aria-hidden", "true");
      return;
    }

    shell.classList.add(mq.matches ? "app-shell--split-wide" : "app-shell--split-narrow");
    rightPanel.hidden = false;
    rightPanel.setAttribute("aria-hidden", "false");
    phoneFrame.hidden = false;
    phoneFrame.setAttribute("aria-hidden", "false");
  }

  function applyActiveMockupViewport() {
    var active = activeMockupLink();
    if (!active) {
      if (iframe) iframe.removeAttribute("src");
      phoneFrame.hidden = true;
      phoneFrame.setAttribute("aria-hidden", "true");
      return;
    }

    iframe.src = active.getAttribute("href");
    phoneFrame.hidden = false;
    phoneFrame.setAttribute("aria-hidden", "false");
  }

  function clearMockup() {
    mockupLinks.forEach(function (link) {
      link.classList.remove("is-active");
    });
    applyLayout();
    applyActiveMockupViewport();
  }

  function applyMockupSize(key) {
    var spec = MOCKUP_SIZES[key] || MOCKUP_SIZES.phone;
    phoneFrame.classList.remove("phone-frame--phone", "phone-frame--desktop");
    phoneFrame.classList.add(spec.className);
    phoneFrame.dataset.size = key;

    sizeButtons.forEach(function (btn) {
      var on = btn.getAttribute("data-mockup-size") === key;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  menuButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = btn.getAttribute("data-menu-target");
      setActiveMenu(activeMenuId() === target ? null : target);
    });
  });

  sizeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      applyMockupSize(btn.getAttribute("data-mockup-size"));
    });
  });

  mockupLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      mockupLinks.forEach(function (node) {
        node.classList.remove("is-active");
      });
      link.classList.add("is-active");
      setActiveMenu(null);
      applyLayout();
      applyActiveMockupViewport();
    });
  });

  docLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      setActiveMenu(null);
    });
  });

  if (mockupFrameClose) {
    mockupFrameClose.addEventListener("click", function () {
      clearMockup();
    });
  }

  if (typeof mq.addEventListener === "function") {
    mq.addEventListener("change", applyLayout);
  } else {
    mq.addListener(applyLayout);
  }

  document.addEventListener("click", function (event) {
    if (!activeMenuId()) return;
    if (header && header.contains(event.target)) return;
    setActiveMenu(null);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setActiveMenu(null);
    }
  });

  applyMockupSize(window.matchMedia("(max-width: 767px)").matches ? "phone" : "desktop");
  setActiveMenu(null);
  applyLayout();
  applyActiveMockupViewport();
})();
