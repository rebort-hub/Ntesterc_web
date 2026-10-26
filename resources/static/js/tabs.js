/**
 * 多标签页
 */
(function (global) {
  var STORAGE_KEY = "nt-tabs";
  var MAX_TABS = 16;
  var SCROLL_STEP = 280;
  var enabled = true;

  function readTabs() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (e) {
      return [];
    }
  }

  function writeTabs(list) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {}
  }

  function normalizePath(path) {
    if (!path) return "/";
    try {
      if (path.indexOf("http") === 0) path = new URL(path).pathname;
    } catch (e) {}
    return path.split("?")[0].split("#")[0] || "/";
  }

  function homePath() {
    var shell = document.getElementById("admin-shell");
    var brand = document.querySelector(".sidebar-brand__link, .topbar-brand, .admin-rail__item[data-rail='dashboard']");
    if (brand && brand.getAttribute("href")) return normalizePath(brand.getAttribute("href"));
    if (shell && shell.getAttribute("data-home")) return normalizePath(shell.getAttribute("data-home"));
    return "/admin";
  }

  function currentPath() {
    var shell = document.getElementById("admin-shell");
    if (shell && shell.getAttribute("data-page-path")) {
      return normalizePath(shell.getAttribute("data-page-path"));
    }
    return normalizePath(location.pathname);
  }

  function currentTitle() {
    var shell = document.getElementById("admin-shell");
    if (shell && shell.getAttribute("data-page-title")) {
      return shell.getAttribute("data-page-title");
    }
    var h1 = document.querySelector(".admin-topbar__title");
    return (h1 && h1.textContent.trim()) || document.title || "页面";
  }

  function upsertCurrent() {
    var path = currentPath();
    var title = currentTitle();
    var list = readTabs();
    var found = list.find(function (t) {
      return t.path === path;
    });
    if (found) {
      found.title = title || found.title;
    } else {
      list.push({ path: path, title: title });
      if (list.length > MAX_TABS) list = list.slice(list.length - MAX_TABS);
    }
    writeTabs(list);
    return list;
  }

  function render() {
    var host = document.getElementById("admin-tabs-list");
    if (!host) return;
    if (!enabled) {
      host.innerHTML = "";
      return;
    }
    var list = readTabs();
    var active = currentPath();
    host.innerHTML = list
      .map(function (tab) {
        var isActive = tab.path === active;
        var closable = list.length > 1;
        return (
          '<div class="admin-tab' +
          (isActive ? " is-active" : "") +
          '" data-tab-path="' +
          tab.path +
          '" title="' +
          escapeAttr(tab.title) +
          '">' +
          '<span class="admin-tab__dot" aria-hidden="true"></span>' +
          '<a class="admin-tab__link" href="' +
          escapeAttr(tab.path) +
          '">' +
          escapeHtml(tab.title) +
          "</a>" +
          (closable
            ? '<button type="button" class="admin-tab__close" data-tab-close="' +
              escapeAttr(tab.path) +
              '" aria-label="关闭">×</button>'
            : "") +
          "</div>"
        );
      })
      .join("");

    // 滚到当前标签可见
    var activeEl = host.querySelector(".admin-tab.is-active");
    if (activeEl && typeof activeEl.scrollIntoView === "function") {
      try {
        activeEl.scrollIntoView({ inline: "nearest", block: "nearest", behavior: "smooth" });
      } catch (e) {
        activeEl.scrollIntoView(false);
      }
    }
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function closeTab(path) {
    path = normalizePath(path);
    var list = readTabs().filter(function (t) {
      return t.path !== path;
    });
    if (!list.length) {
      writeTabs([{ path: currentPath(), title: currentTitle() }]);
      render();
      return;
    }
    writeTabs(list);
    if (path === currentPath()) {
      var next = list[list.length - 1];
      location.href = next.path;
      return;
    }
    render();
  }

  function closeCurrent() {
    var list = readTabs();
    if (list.length <= 1) return;
    closeTab(currentPath());
  }

  function closeOthers() {
    var path = currentPath();
    var title = currentTitle();
    var list = readTabs().filter(function (t) {
      return t.path === path;
    });
    if (!list.length) list = [{ path: path, title: title }];
    writeTabs(list);
    render();
  }

  function closeAll() {
    var home = homePath();
    var cur = currentPath();
    if (cur === home) {
      writeTabs([{ path: home, title: "控制台" }]);
      render();
      return;
    }
    writeTabs([{ path: home, title: "控制台" }]);
    location.href = home;
  }

  function scrollTabs(dir) {
    var host = document.getElementById("admin-tabs-list");
    if (!host) return;
    var delta = dir === "left" ? -SCROLL_STEP : SCROLL_STEP;
    if (typeof host.scrollBy === "function") {
      host.scrollBy({ left: delta, behavior: "smooth" });
    } else {
      host.scrollLeft += delta;
    }
  }

  function closeToolMenu() {
    var menu = document.getElementById("nt-tabs-menu");
    var btn = document.getElementById("nt-tabs-tool-btn");
    if (menu) menu.hidden = true;
    if (btn) btn.setAttribute("aria-expanded", "false");
  }

  function toggleToolMenu() {
    var menu = document.getElementById("nt-tabs-menu");
    var btn = document.getElementById("nt-tabs-tool-btn");
    if (!menu || !btn) return;
    var open = menu.hidden;
    menu.hidden = !open;
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function setEnabled(on) {
    enabled = !!on;
    var bar = document.getElementById("admin-tabs");
    if (bar) bar.hidden = !enabled;
    if (enabled) {
      upsertCurrent();
      render();
    } else {
      render();
      closeToolMenu();
    }
  }

  function bind() {
    var host = document.getElementById("admin-tabs-list");
    if (host) {
      host.addEventListener("click", function (e) {
        var closeBtn = e.target.closest("[data-tab-close]");
        if (closeBtn) {
          e.preventDefault();
          e.stopPropagation();
          closeTab(closeBtn.getAttribute("data-tab-close"));
        }
      });
    }

    var prev = document.getElementById("nt-tabs-prev");
    var next = document.getElementById("nt-tabs-next");
    if (prev) {
      prev.addEventListener("click", function (e) {
        e.preventDefault();
        scrollTabs("left");
      });
    }
    if (next) {
      next.addEventListener("click", function (e) {
        e.preventDefault();
        scrollTabs("right");
      });
    }

    var toolBtn = document.getElementById("nt-tabs-tool-btn");
    var menu = document.getElementById("nt-tabs-menu");
    var tool = document.getElementById("nt-tabs-tool");
    if (toolBtn) {
      toolBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        toggleToolMenu();
      });
    }
    if (menu) {
      menu.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-nt-tabs-action]");
        if (!btn) return;
        e.preventDefault();
        var action = btn.getAttribute("data-nt-tabs-action");
        closeToolMenu();
        if (action === "close-this") closeCurrent();
        else if (action === "close-other") closeOthers();
        else if (action === "close-all") closeAll();
      });
    }
    document.addEventListener("click", function (e) {
      if (tool && !tool.contains(e.target)) closeToolMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeToolMenu();
    });
  }

  function init() {
    var theme = global.NtTheme && global.NtTheme.get ? global.NtTheme.get() : { tabs: true };
    enabled = theme.tabs !== false;
    var bar = document.getElementById("admin-tabs");
    if (bar) bar.hidden = !enabled;
    if (enabled) upsertCurrent();
    render();
    bind();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.NtTabs = {
    render: render,
    closeTab: closeTab,
    closeCurrent: closeCurrent,
    closeOthers: closeOthers,
    closeAll: closeAll,
    setEnabled: setEnabled,
    upsertCurrent: upsertCurrent,
  };
})(window);
