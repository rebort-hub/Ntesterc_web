/**
 * Admin 壳：侧栏折叠、布局模式（垂直/水平/混合/双列）交互。
 * 一级菜单必须可跳转：优先走元素自身 href / data-first-href。
 */
(function (global) {
  var shell = null;
  var mixedActive = null;

  function getLayout() {
    if (global.NtTheme && global.NtTheme.get) {
      return global.NtTheme.get().layout || "vertical";
    }
    return document.documentElement.getAttribute("data-nt-layout") || "vertical";
  }

  function firstLeafHref(groupCode) {
    var link = document.querySelector(
      '.menu-item--sub[data-menu-group-code="' + groupCode + '"]'
    );
    if (link && link.getAttribute("href")) return link.getAttribute("href");
    var group = document.querySelector(
      '.admin-hmenu__group[data-hmenu-group="' + groupCode + '"]'
    );
    if (group && group.getAttribute("data-first-href")) {
      return group.getAttribute("data-first-href");
    }
    var rail = document.querySelector('.admin-rail__item[data-rail="' + groupCode + '"]');
    if (rail && rail.getAttribute("data-first-href")) {
      return rail.getAttribute("data-first-href");
    }
    if (rail && rail.getAttribute("href")) return rail.getAttribute("href");
    return null;
  }

  function go(href) {
    if (!href || href === "#" || href.indexOf("javascript:") === 0) return false;
    window.location.href = href;
    return true;
  }

  function syncMixedSidebar(groupCode) {
    mixedActive = groupCode || mixedActive || "dashboard";
    var menu = document.getElementById("sidebar-menu");
    var sidebar = document.getElementById("admin-sidebar");
    var layout = getLayout();
    if (!menu) return;

    menu.querySelectorAll("[data-menu-group]").forEach(function (group) {
      var code = group.getAttribute("data-group-code");
      var match = code === mixedActive;
      group.hidden = !match;
      group.classList.toggle("is-open", match);
      var trigger = group.querySelector(".menu-group__trigger");
      if (trigger) trigger.setAttribute("aria-expanded", match ? "true" : "false");
    });

    var root = menu.querySelector('.menu-item--root[data-menu-group-code="dashboard"]');
    if (root) root.hidden = true;

    if (sidebar) {
      sidebar.classList.toggle("is-leaf-only", mixedActive === "dashboard");
    }
    if (shell) {
      shell.classList.toggle("is-rail-dashboard", mixedActive === "dashboard");
    }

    var brandTitle = document.querySelector(".sidebar-brand__title");
    if (brandTitle && layout === "columns") {
      if (mixedActive === "dashboard") {
        brandTitle.textContent = brandTitle.dataset.defaultTitle || "控制台";
      } else {
        var label = menu.querySelector(
          '[data-group-code="' + mixedActive + '"] .menu-group__trigger .menu-label'
        );
        brandTitle.textContent = label ? label.textContent : "";
      }
    }
  }

  function syncColumnsRail() {
    document.querySelectorAll(".admin-rail__item").forEach(function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-rail") === mixedActive);
    });
    var layout = getLayout();
    if (layout === "columns" || layout === "mixed") {
      syncMixedSidebar(mixedActive);
    }
  }

  function detectActiveGroup() {
    var activeSub = document.querySelector(".menu-item--sub.is-active");
    if (activeSub) return activeSub.getAttribute("data-menu-group-code");
    if (document.querySelector(".menu-item--root.is-active")) return "dashboard";
    var activeH = document.querySelector(".admin-hmenu__group.is-active");
    if (activeH) return activeH.getAttribute("data-hmenu-group");
    return "system";
  }

  function applyLayoutView() {
    var layout = getLayout();
    shell = document.getElementById("admin-shell");
    if (!shell) return;

    if (layout === "vertical" || layout === "horizontal") {
      document.querySelectorAll("[data-menu-group]").forEach(function (group) {
        group.hidden = false;
      });
      var root = document.querySelector('.menu-item--root[data-menu-group-code="dashboard"]');
      if (root) root.hidden = false;
      var brandTitle = document.querySelector(".sidebar-brand__title");
      if (brandTitle && brandTitle.dataset.defaultTitle) {
        brandTitle.textContent = brandTitle.dataset.defaultTitle;
      }
      shell.classList.remove("is-rail-dashboard");
      var sidebar = document.getElementById("admin-sidebar");
      if (sidebar) sidebar.classList.remove("is-leaf-only");
    }

    if (layout === "mixed" || layout === "columns") {
      mixedActive = detectActiveGroup();
      syncMixedSidebar(mixedActive);
      syncColumnsRail();
    }

    document.querySelectorAll(".admin-hmenu__group").forEach(function (g) {
      g.classList.remove("is-open");
    });
  }

  function bindCollapse() {
    var toggle = document.getElementById("sidebar-toggle");
    if (!toggle || !shell) return;
    toggle.addEventListener("click", function () {
      shell.classList.toggle("is-sidebar-collapsed");
    });
  }

  function bindVerticalGroups() {
    document.querySelectorAll("[data-menu-group]").forEach(function (group) {
      var trigger = group.querySelector(".menu-group__trigger");
      if (!trigger) return;
      trigger.addEventListener("click", function () {
        if (getLayout() === "mixed" || getLayout() === "columns") return;
        var open = group.classList.toggle("is-open");
        trigger.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
  }

  function resolveGroupHref(el, groupCode) {
    return (
      (el && el.getAttribute("href")) ||
      (el && el.getAttribute("data-first-href")) ||
      firstLeafHref(groupCode)
    );
  }

  function bindMenus() {
    // 顶栏一级：水平 / 混合 — 必须跳到该组首页
    var hmenu = document.getElementById("admin-hmenu");
    if (hmenu) {
      hmenu.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

        var dropItem = e.target.closest("a.admin-hmenu__drop-item");
        if (dropItem) {
          e.preventDefault();
          go(dropItem.getAttribute("href"));
          return;
        }

        var trigger = e.target.closest(".admin-hmenu__trigger[data-hmenu]");
        if (!trigger) return;

        var layout = getLayout();
        var code = trigger.getAttribute("data-hmenu");
        if (code === "dashboard") return; // 自身已是链接

        if (layout !== "horizontal" && layout !== "mixed") return;

        e.preventDefault();
        e.stopPropagation();

        if (layout === "mixed") {
          mixedActive = code;
          syncMixedSidebar(code);
          document.querySelectorAll(".admin-hmenu__group").forEach(function (g) {
            g.classList.toggle(
              "is-active",
              g.getAttribute("data-hmenu-group") === code
            );
          });
        }

        var href = resolveGroupHref(trigger, code);
        if (!go(href)) {
          console.warn("[NtAdmin] 一级菜单无有效跳转地址", code, trigger);
        }
      });
    }

    // 侧栏叶子
    var sideMenu = document.getElementById("sidebar-menu");
    if (sideMenu) {
      sideMenu.addEventListener("click", function (e) {
        var leaf = e.target.closest("a.menu-item[href]");
        if (!leaf) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var layout = getLayout();
        if (layout !== "mixed" && layout !== "columns") return;
        e.preventDefault();
        go(leaf.getAttribute("href"));
      });
    }

    // 双列图标栏一级
    var rail = document.getElementById("admin-rail");
    if (rail) {
      rail.addEventListener("click", function (e) {
        if (getLayout() !== "columns") return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var item = e.target.closest("[data-rail]");
        if (!item) return;
        var code = item.getAttribute("data-rail");
        if (code === "dashboard") return;
        e.preventDefault();
        mixedActive = code;
        syncColumnsRail();
        var href = resolveGroupHref(item, code);
        if (!go(href)) {
          console.warn("[NtAdmin] 双列一级菜单无有效跳转地址", code, item);
        }
      });
    }
  }

  function rememberBrandTitle() {
    var brandTitle = document.querySelector(".sidebar-brand__title");
    if (brandTitle && !brandTitle.dataset.defaultTitle) {
      brandTitle.dataset.defaultTitle = brandTitle.textContent;
    }
  }

  function onThemeChange() {
    applyLayoutView();
  }

  function hideLoader() {
    var el = document.getElementById("nt-loader");
    if (!el) return;
    el.classList.add("is-done");
    el.setAttribute("aria-hidden", "true");
    setTimeout(function () {
      if (el && el.parentNode) el.parentNode.removeChild(el);
    }, 220);
  }

  function isFullscreen() {
    return !!(
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.msFullscreenElement
    );
  }

  function toggleFullscreen() {
    var btn = document.getElementById("nt-fullscreen");
    var icon = btn && btn.querySelector(".layui-icon");
    if (isFullscreen()) {
      var exit =
        document.exitFullscreen ||
        document.webkitExitFullscreen ||
        document.msExitFullscreen;
      if (exit) exit.call(document);
      if (icon) icon.className = "layui-icon layui-icon-screen-full";
    } else {
      var el = document.documentElement;
      var req =
        el.requestFullscreen ||
        el.webkitRequestFullscreen ||
        el.msRequestFullscreen;
      if (req) req.call(el);
      if (icon) icon.className = "layui-icon layui-icon-screen-restore";
    }
  }

  function bindToolbar() {
    var fs = document.getElementById("nt-fullscreen");
    if (fs) {
      fs.addEventListener("click", function (e) {
        e.preventDefault();
        toggleFullscreen();
      });
      document.addEventListener("fullscreenchange", function () {
        var icon = fs.querySelector(".layui-icon");
        if (!icon) return;
        icon.className = isFullscreen()
          ? "layui-icon layui-icon-screen-restore"
          : "layui-icon layui-icon-screen-full";
      });
    }

    var user = document.getElementById("nt-user-menu");
    if (user) {
      var btn = user.querySelector(".admin-toolbar__user-btn");
      var drop = user.querySelector(".admin-toolbar__drop");
      if (btn && drop) {
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          var open = drop.hidden;
          drop.hidden = !open;
          btn.setAttribute("aria-expanded", open ? "true" : "false");
        });
        document.addEventListener("click", function () {
          drop.hidden = true;
          btn.setAttribute("aria-expanded", "false");
        });
      }
    }

    var searchBtn = document.getElementById("nt-menu-search");
    if (searchBtn) {
      searchBtn.addEventListener("click", function (e) {
        e.preventDefault();
        openMenuSearch();
      });
    }

    var notice = document.getElementById("nt-notice");
    if (notice) {
      notice.addEventListener("click", function (e) {
        e.preventDefault();
      });
    }
  }

  function openMenuSearch() {
    var existing = document.getElementById("nt-menu-search-panel");
    if (existing) {
      existing.remove();
      return;
    }
    var items = [];
    document.querySelectorAll("#sidebar-menu a.menu-item[href]").forEach(function (a) {
      var label = a.querySelector(".menu-label");
      items.push({
        name: label ? label.textContent.trim() : a.getAttribute("data-tab-title") || "",
        href: a.getAttribute("href"),
      });
    });

    var panel = document.createElement("div");
    panel.id = "nt-menu-search-panel";
    panel.className = "admin-menu-search";
    panel.innerHTML =
      '<div class="admin-menu-search__mask" data-close></div>' +
      '<div class="admin-menu-search__box" role="dialog" aria-label="菜单搜索">' +
      '<input type="search" class="admin-menu-search__input" placeholder="搜索菜单" autofocus>' +
      '<ul class="admin-menu-search__list"></ul>' +
      "</div>";
    document.body.appendChild(panel);

    var input = panel.querySelector(".admin-menu-search__input");
    var list = panel.querySelector(".admin-menu-search__list");

    function render(q) {
      var qq = (q || "").trim().toLowerCase();
      var matched = items.filter(function (it) {
        return it.name && (!qq || it.name.toLowerCase().indexOf(qq) >= 0);
      });
      list.innerHTML = matched
        .slice(0, 20)
        .map(function (it) {
          return (
            '<li><a href="' +
            it.href +
            '">' +
            it.name +
            "</a></li>"
          );
        })
        .join("");
    }

    render("");
    input.addEventListener("input", function () {
      render(input.value);
    });
    panel.querySelector("[data-close]").addEventListener("click", function () {
      panel.remove();
    });
    document.addEventListener(
      "keydown",
      function onEsc(e) {
        if (e.key === "Escape") {
          panel.remove();
          document.removeEventListener("keydown", onEsc);
        }
      }
    );
  }

  function init() {
    shell = document.getElementById("admin-shell");
    if (!shell) return;
    rememberBrandTitle();
    bindCollapse();
    bindVerticalGroups();
    bindMenus();
    bindToolbar();
    applyLayoutView();
    // 首屏加载动画：布局就绪后收起（对齐 rebort keepLoad）
    setTimeout(hideLoader, 280);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.NtAdmin = {
    onThemeChange: onThemeChange,
    applyLayoutView: applyLayoutView,
  };
})(window);
