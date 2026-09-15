(function(){
  "use strict";
  var STORAGE_KEY = "anti-terminal-settings";
  var root = document.documentElement;
  var body = document.body;

  function loadSettings(){
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch(e){ return {}; }
  }
  function saveSettings(s){
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); } catch(e){}
  }

  var settings = Object.assign({ noise: true, scanlines: true, sync: true, mode: "amber" }, loadSettings());

  function applySettings(){
    root.setAttribute("data-mode", settings.mode);
    body.classList.toggle("effects-noise-off", !settings.noise);
    body.classList.toggle("effects-scanlines-off", !settings.scanlines);
    var marks = document.querySelectorAll("[data-mark]");
    marks.forEach(function(el){
      var key = el.getAttribute("data-mark");
      if (key === "scanlines") el.textContent = settings.scanlines ? "x" : " ";
      if (key === "noise") el.textContent = settings.noise ? "x" : " ";
      if (key === "sync") el.textContent = settings.sync ? "x" : " ";
      if (key === "mode-amber") el.textContent = settings.mode === "amber" ? "*" : " ";
      if (key === "mode-green") el.textContent = settings.mode === "green" ? "*" : " ";
      if (key === "mode-light") el.textContent = settings.mode === "light" ? "*" : " ";
    });
  }

  function persist(){ saveSettings(settings); applySettings(); }

  document.addEventListener("DOMContentLoaded", function(){
    applySettings();

    // generate noise tiles client-side (no static image assets needed)
    function makeNoiseTile(size){
      var canvas = document.createElement("canvas");
      canvas.width = size; canvas.height = size;
      var ctx = canvas.getContext("2d");
      var img = ctx.createImageData(size, size);
      for (var i = 0; i < img.data.length; i += 4) {
        var v = Math.floor(Math.random() * 255);
        img.data[i] = v; img.data[i+1] = v; img.data[i+2] = v; img.data[i+3] = 255;
      }
      ctx.putImageData(img, 0, 0);
      return canvas.toDataURL();
    }
    document.querySelectorAll("[data-noise]").forEach(function(el){
      el.style.backgroundImage = "url('" + makeNoiseTile(128) + "')";
    });

    document.querySelectorAll("[data-toggle]").forEach(function(el){
      el.addEventListener("click", function(e){
        e.preventDefault();
        var key = el.getAttribute("data-toggle");
        settings[key] = !settings[key];
        persist();
      });
    });
    document.querySelectorAll("[data-set-mode]").forEach(function(el){
      el.addEventListener("click", function(e){
        e.preventDefault();
        settings.mode = el.getAttribute("data-set-mode");
        persist();
      });
    });

    var settingsToggle = document.querySelector("[data-settings-toggle]");
    var settingsPanel = document.querySelector("[data-settings-panel]");
    if (settingsToggle && settingsPanel) {
      settingsToggle.addEventListener("click", function(e){
        e.preventDefault();
        settingsPanel.classList.toggle("open");
      });
      var closeBtn = settingsPanel.querySelector("[data-settings-close]");
      if (closeBtn) closeBtn.addEventListener("click", function(e){
        e.preventDefault();
        settingsPanel.classList.remove("open");
      });
      document.addEventListener("click", function(e){
        if (!settingsPanel.contains(e.target) && !settingsToggle.contains(e.target)) {
          settingsPanel.classList.remove("open");
        }
      });
    }

    // live stats: uptime, cores, heap (heap only in Chromium)
    var mountTime = Date.now();
    var uptimeEl = document.querySelector("[data-stat-uptime]");
    var coresEl = document.querySelector("[data-stat-cores]");
    var coresWrap = document.querySelector("[data-stat-cores-wrap]");
    var memEl = document.querySelector("[data-stat-mem]");
    var memWrap = document.querySelector("[data-stat-mem-wrap]");

    if (coresEl && navigator.hardwareConcurrency) {
      coresEl.textContent = navigator.hardwareConcurrency;
      if (coresWrap) coresWrap.style.display = "";
    } else if (coresWrap) {
      coresWrap.style.display = "none";
    }

    function tick(){
      if (uptimeEl) {
        var sec = Math.floor((Date.now() - mountTime) / 1000);
        var m = String(Math.floor(sec / 60)).padStart(2, "0");
        var s = String(sec % 60).padStart(2, "0");
        uptimeEl.textContent = m + ":" + s;
      }
      if (memEl && memWrap) {
        if (performance.memory && performance.memory.usedJSHeapSize) {
          memEl.textContent = Math.round(performance.memory.usedJSHeapSize / 1048576);
          memWrap.style.display = "";
        } else {
          memWrap.style.display = "none";
        }
      }
    }
    tick();
    setInterval(tick, 1000);

    // random sync-glitch burst on the whole page
    var glitchTarget = document.querySelector("[data-glitch-target]") || body;
    function scheduleGlitch(){
      var wait = 9000 + Math.random() * 16000;
      setTimeout(function(){
        if (settings.sync) {
          glitchTarget.classList.add("glitch");
          setTimeout(function(){ glitchTarget.classList.remove("glitch"); }, 420);
        }
        scheduleGlitch();
      }, wait);
    }
    scheduleGlitch();
  });
})();
