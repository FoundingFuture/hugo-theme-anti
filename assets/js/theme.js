(function () {
  "use strict";

  // head.html has already restored saved settings into these attributes.
  var root = document.documentElement;
  var storageKey = root.getAttribute("data-settings-key");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function setting(name) {
    return root.getAttribute("data-" + name);
  }

  function save() {
    var saved = {};
    root.getAttribute("data-settings").split(" ").forEach(function (name) {
      saved[name] = setting(name);
    });
    try { localStorage.setItem(storageKey, JSON.stringify(saved)); } catch (e) {}
  }

  function render() {
    document.querySelectorAll("[data-toggle]").forEach(function (button) {
      var on = setting(button.getAttribute("data-toggle")) !== "off";
      button.setAttribute("aria-pressed", String(on));
      button.querySelector(".mark").textContent = on ? "x" : " ";
    });
    document.querySelectorAll("[data-set-mode]").forEach(function (button) {
      var on = button.getAttribute("data-set-mode") === setting("mode");
      button.setAttribute("aria-pressed", String(on));
      button.querySelector(".mark").textContent = on ? "*" : " ";
    });
    // Read the colour from the stylesheet so the palette stays defined once.
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "theme-color";
      document.head.appendChild(meta);
    }
    meta.content = getComputedStyle(root).getPropertyValue("--bg-page").trim();
  }

  function change(name, value) {
    root.setAttribute("data-" + name, value);
    save();
    render();
  }

  render();

  // Generate the noise tiles here, so the theme ships no image assets.
  function noiseTile(size) {
    var canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    var ctx = canvas.getContext("2d");
    var img = ctx.createImageData(size, size);
    for (var i = 0; i < img.data.length; i += 4) {
      var v = Math.floor(Math.random() * 255);
      img.data[i] = v; img.data[i + 1] = v; img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    return canvas.toDataURL();
  }
  document.querySelectorAll("[data-noise-tile]").forEach(function (el) {
    el.style.backgroundImage = "url('" + noiseTile(128) + "')";
  });

  document.querySelectorAll("[data-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      var name = button.getAttribute("data-toggle");
      change(name, setting(name) === "off" ? "on" : "off");
    });
  });
  document.querySelectorAll("[data-set-mode]").forEach(function (button) {
    button.addEventListener("click", function () {
      change("mode", button.getAttribute("data-set-mode"));
    });
  });

  var toggle = document.querySelector("[data-settings-toggle]");
  var panel = document.querySelector("[data-settings-panel]");
  if (toggle && panel) {
    var setOpen = function (open, restoreFocus) {
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
      if (!open && restoreFocus) toggle.focus();
    };
    toggle.addEventListener("click", function () {
      setOpen(panel.hidden, false);
    });
    var close = panel.querySelector("[data-settings-close]");
    if (close) {
      close.addEventListener("click", function () { setOpen(false, true); });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !panel.hidden) setOpen(false, true);
    });
    document.addEventListener("click", function (e) {
      if (!panel.hidden && !panel.contains(e.target) && !toggle.contains(e.target)) {
        setOpen(false, false);
      }
    });
  }

  // Live stats. The heap reading exists only in Chromium browsers.
  var mountTime = Date.now();
  var uptimeEl = document.querySelector("[data-stat-uptime]");
  var coresEl = document.querySelector("[data-stat-cores]");
  var coresWrap = document.querySelector("[data-stat-cores-wrap]");
  var memEl = document.querySelector("[data-stat-mem]");
  var memWrap = document.querySelector("[data-stat-mem-wrap]");

  if (coresEl && coresWrap && navigator.hardwareConcurrency) {
    coresEl.textContent = navigator.hardwareConcurrency;
    coresWrap.hidden = false;
  }

  function tick() {
    if (uptimeEl) {
      var sec = Math.floor((Date.now() - mountTime) / 1000);
      uptimeEl.textContent = String(Math.floor(sec / 60)).padStart(2, "0") + ":" + String(sec % 60).padStart(2, "0");
    }
    if (memEl && memWrap) {
      var heap = performance.memory && performance.memory.usedJSHeapSize;
      memWrap.hidden = !heap;
      if (heap) memEl.textContent = Math.round(heap / 1048576);
    }
  }
  tick();
  setInterval(tick, 1000);

  // A sync glitch every 9 to 25 seconds, unless the reader turned it off
  // or asks the system for reduced motion.
  var glitchTarget = document.querySelector("[data-glitch-target]") || document.body;
  function scheduleGlitch() {
    setTimeout(function () {
      if (setting("sync") !== "off" && !reducedMotion.matches) {
        glitchTarget.classList.add("glitch");
        setTimeout(function () { glitchTarget.classList.remove("glitch"); }, 420);
      }
      scheduleGlitch();
    }, 9000 + Math.random() * 16000);
  }
  scheduleGlitch();
})();
