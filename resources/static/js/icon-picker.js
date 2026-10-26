
(function (global) {
  var ICONS = [
    "layui-icon-rate-half", "layui-icon-rate", "layui-icon-rate-solid",
    "layui-icon-cellphone", "layui-icon-vercode", "layui-icon-login-wechat",
    "layui-icon-login-qq", "layui-icon-login-weibo", "layui-icon-password",
    "layui-icon-username", "layui-icon-refresh-3", "layui-icon-auz",
    "layui-icon-spread-left", "layui-icon-shrink-right",
    "layui-icon-snowflake", "layui-icon-tips", "layui-icon-note",
    "layui-icon-home", "layui-icon-senior", "layui-icon-refresh",
    "layui-icon-refresh-1", "layui-icon-flag", "layui-icon-theme",
    "layui-icon-notice", "layui-icon-website", "layui-icon-console",
    "layui-icon-face-surprised", "layui-icon-set", "layui-icon-template-1",
    "layui-icon-app", "layui-icon-template", "layui-icon-praise",
    "layui-icon-tread", "layui-icon-male", "layui-icon-female",
    "layui-icon-camera", "layui-icon-camera-fill", "layui-icon-more",
    "layui-icon-more-vertical", "layui-icon-rmb", "layui-icon-dollar",
    "layui-icon-diamond", "layui-icon-fire", "layui-icon-return",
    "layui-icon-location", "layui-icon-read", "layui-icon-survey",
    "layui-icon-face-smile", "layui-icon-face-cry",
    "layui-icon-cart-simple", "layui-icon-cart", "layui-icon-next",
    "layui-icon-prev", "layui-icon-upload-drag", "layui-icon-upload",
    "layui-icon-download-circle", "layui-icon-component",
    "layui-icon-file-b", "layui-icon-user", "layui-icon-find-fill",
    "layui-icon-loading", "layui-icon-loading-1", "layui-icon-add-1",
    "layui-icon-play", "layui-icon-pause", "layui-icon-headset",
    "layui-icon-video", "layui-icon-voice", "layui-icon-speaker",
    "layui-icon-fonts-del", "layui-icon-fonts-code",
    "layui-icon-fonts-html", "layui-icon-fonts-strong", "layui-icon-unlink",
    "layui-icon-picture", "layui-icon-link", "layui-icon-face-smile-b",
    "layui-icon-align-left", "layui-icon-align-right",
    "layui-icon-align-center", "layui-icon-fonts-u", "layui-icon-fonts-i",
    "layui-icon-tabs", "layui-icon-radio", "layui-icon-circle",
    "layui-icon-edit", "layui-icon-share", "layui-icon-delete",
    "layui-icon-form", "layui-icon-cellphone-fine", "layui-icon-dialogue",
    "layui-icon-fonts-clear", "layui-icon-layer", "layui-icon-date",
    "layui-icon-water", "layui-icon-code-circle", "layui-icon-carousel",
    "layui-icon-prev-circle", "layui-icon-layouts", "layui-icon-util",
    "layui-icon-templeate-1", "layui-icon-upload-circle", "layui-icon-tree",
    "layui-icon-table", "layui-icon-chart", "layui-icon-chart-screen",
    "layui-icon-engine", "layui-icon-triangle-d", "layui-icon-triangle-r",
    "layui-icon-file", "layui-icon-set-sm", "layui-icon-add-circle",
    "layui-icon-404", "layui-icon-about", "layui-icon-up",
    "layui-icon-down", "layui-icon-left", "layui-icon-right",
    "layui-icon-circle-dot", "layui-icon-search", "layui-icon-set-fill",
    "layui-icon-group", "layui-icon-friends", "layui-icon-reply-fill",
    "layui-icon-menu-fill", "layui-icon-log", "layui-icon-picture-fine",
    "layui-icon-face-smile-fine", "layui-icon-list", "layui-icon-release",
    "layui-icon-ok", "layui-icon-help", "layui-icon-chat", "layui-icon-top",
    "layui-icon-star", "layui-icon-star-fill", "layui-icon-close-fill",
    "layui-icon-close", "layui-icon-ok-circle", "layui-icon-add-circle-fine",
  ];

  var LIMIT = 12;

  function toGlyph(val) {
    var v = (val || "").trim();
    if (!v) return "";
    if (v.indexOf(" ") >= 0) {
      var parts = v.split(/\s+/);
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].indexOf("layui-icon-") === 0) return parts[i];
      }
      return "";
    }
    if (v.indexOf("layui-icon-") === 0) return v;
    return "";
  }

  function createPicker(input) {
    if (!input || input.dataset.ntIconBound) return;
    input.dataset.ntIconBound = "1";

    // 规范化已有值
    var glyph0 = toGlyph(input.value);
    if (glyph0) input.value = glyph0;

    var wrap = document.createElement("div");
    wrap.className = "nt-icon-picker";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    input.type = "hidden";

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "nt-icon-picker__trigger";
    trigger.innerHTML = '<i class="layui-icon nt-icon-picker__preview" aria-hidden="true"></i>';
    wrap.insertBefore(trigger, input);

    var panel = document.createElement("div");
    panel.className = "nt-icon-picker__panel";
    panel.hidden = true;
    panel.innerHTML =
      '<div class="nt-icon-picker__search-wrap">' +
      '<input type="search" class="nt-icon-picker__search" placeholder="搜索图标">' +
      '<span class="nt-icon-picker__search-ico" aria-hidden="true"></span>' +
      "</div>" +
      '<div class="nt-icon-picker__grid"></div>' +
      '<div class="nt-icon-picker__pager">' +
      '<span class="nt-icon-picker__pageinfo"></span>' +
      '<div class="nt-icon-picker__pager-btns">' +
      '<button type="button" class="nt-icon-picker__nav" data-ico-prev aria-label="上一页">‹</button>' +
      '<button type="button" class="nt-icon-picker__nav" data-ico-next aria-label="下一页">›</button>' +
      "</div></div>";
    wrap.appendChild(panel);

    var state = { q: "", page: 1 };

    function filtered() {
      var q = state.q.trim().toLowerCase();
      if (!q) return ICONS.slice();
      return ICONS.filter(function (k) {
        return k.toLowerCase().indexOf(q) >= 0;
      });
    }

    function syncPreview() {
      var preview = trigger.querySelector(".nt-icon-picker__preview");
      var val = toGlyph(input.value) || "layui-icon-circle-dot";
      preview.className = "layui-icon nt-icon-picker__preview " + val;
      trigger.title = input.value || "选择图标";
      trigger.classList.toggle("has-value", !!input.value);
    }

    function render() {
      var list = filtered();
      var totalPages = Math.max(1, Math.ceil(list.length / LIMIT));
      if (state.page > totalPages) state.page = totalPages;
      if (state.page < 1) state.page = 1;
      var start = (state.page - 1) * LIMIT;
      var pageItems = list.slice(start, start + LIMIT);
      var grid = panel.querySelector(".nt-icon-picker__grid");
      var cur = toGlyph(input.value);
      grid.innerHTML = pageItems
        .map(function (k) {
          var active = cur === k ? " is-active" : "";
          return (
            '<button type="button" class="nt-icon-picker__item' +
            active +
            '" data-ico="' +
            k +
            '" title="' +
            k +
            '"><i class="layui-icon ' +
            k +
            '"></i></button>'
          );
        })
        .join("");
      panel.querySelector(".nt-icon-picker__pageinfo").textContent =
        state.page + "/" + totalPages + " (" + list.length + ")";
    }

    function open() {
      panel.hidden = false;
      state.page = 1;
      render();
      var search = panel.querySelector(".nt-icon-picker__search");
      if (search) search.focus();
    }

    function close() {
      panel.hidden = true;
    }

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (panel.hidden) open();
      else close();
    });

    panel.querySelector(".nt-icon-picker__search").addEventListener("input", function (e) {
      state.q = e.target.value || "";
      state.page = 1;
      render();
    });

    panel.querySelector("[data-ico-prev]").addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (state.page > 1) {
        state.page -= 1;
        render();
      }
    });
    panel.querySelector("[data-ico-next]").addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var totalPages = Math.max(1, Math.ceil(filtered().length / LIMIT));
      if (state.page < totalPages) {
        state.page += 1;
        render();
      }
    });

    panel.addEventListener("click", function (e) {
      e.stopPropagation();
      var btn = e.target.closest("[data-ico]");
      if (!btn) return;
      input.value = btn.getAttribute("data-ico") || "";
      input.dispatchEvent(new Event("change", { bubbles: true }));
      syncPreview();
      close();
    });

    document.addEventListener("click", function (e) {
      if (!wrap.contains(e.target)) close();
    });

    input.addEventListener("change", function () {
      var g = toGlyph(input.value);
      if (g && input.value !== g) input.value = g;
      syncPreview();
    });

    syncPreview();
  }

  function bindAll(root) {
    (root || document).querySelectorAll("[data-nt-icon-picker]").forEach(createPicker);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      bindAll();
    });
  } else {
    bindAll();
  }

  global.NtIconPicker = { bind: bindAll, icons: ICONS };
})(window);
