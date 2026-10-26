/**
 * 主题：主色 / 暗色 / 菜单布局 / 多标签，持久化 localStorage。
 * 键：nt-theme = { primary, dark, layout, tabs }
 * layout: vertical | horizontal | mixed | columns
 */
(function (global) {
  var STORAGE_KEY = "nt-theme";
  var LAYOUTS = ["vertical", "horizontal", "mixed", "columns"];
  var DEFAULTS = {
    primary: "#1677ff",
    dark: false,
    layout: "vertical",
    tabs: true,
  };
  var PRESET_COLORS = [
    "#1677ff",
    "#16baaa",
    "#52c41a",
    "#faad14",
    "#f5222d",
    "#722ed1",
    "#eb2f96",
    "#13c2c2",
  ];

  function normalize(state) {
    var next = Object.assign({}, DEFAULTS, state || {});
    if (LAYOUTS.indexOf(next.layout) < 0) next.layout = DEFAULTS.layout;
    next.dark = !!next.dark;
    next.tabs = next.tabs !== false;
    // 迁移旧字段
    delete next.menu;
    delete next.header;
    return next;
  }

  function read() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return Object.assign({}, DEFAULTS);
      return normalize(JSON.parse(raw));
    } catch (e) {
      return Object.assign({}, DEFAULTS);
    }
  }

  function write(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(normalize(state)));
    } catch (e) {}
  }

  function hexToRgb(hex) {
    var h = String(hex || "").replace("#", "");
    if (h.length === 3) {
      h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    }
    if (h.length !== 6) return null;
    return {
      r: parseInt(h.slice(0, 2), 16),
      g: parseInt(h.slice(2, 4), 16),
      b: parseInt(h.slice(4, 6), 16),
    };
  }

  function apply(state) {
    state = normalize(state);
    var root = document.documentElement;
    var primary = state.primary || DEFAULTS.primary;
    var rgb = hexToRgb(primary);
    root.style.setProperty("--nt-primary", primary);
    if (rgb) {
      root.style.setProperty("--nt-primary-rgb", rgb.r + ", " + rgb.g + ", " + rgb.b);
      root.style.setProperty(
        "--nt-menu-active-bg",
        "rgba(" + rgb.r + ", " + rgb.g + ", " + rgb.b + ", 0.1)"
      );
    }
    root.style.setProperty("--nt-menu-active-color", primary);
    root.classList.toggle("nt-dark", !!state.dark);
    root.setAttribute("data-nt-layout", state.layout);
    root.classList.toggle("nt-tabs-off", !state.tabs);

    var shell = document.querySelector(".admin-shell");
    if (shell) {
      shell.setAttribute("data-layout", state.layout);
      shell.classList.toggle("is-tabs-off", !state.tabs);
      // 清除旧皮肤 class
      shell.classList.remove(
        "is-menu-dark",
        "is-header-dark",
        "is-header-primary"
      );
    }

    if (global.NtAdmin && typeof global.NtAdmin.onThemeChange === "function") {
      global.NtAdmin.onThemeChange(state);
    }
    if (global.NtTabs && typeof global.NtTabs.setEnabled === "function") {
      global.NtTabs.setEnabled(state.tabs);
    }
  }

  function get() {
    return read();
  }

  function set(partial) {
    var next = normalize(Object.assign(read(), partial || {}));
    write(next);
    apply(next);
    syncDrawer(next);
    return next;
  }

  function boot() {
    apply(read());
  }

  function openDrawer() {
    var drawer = document.getElementById("nt-theme-drawer");
    if (!drawer) return;
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
    document.body.classList.add("nt-drawer-open");
    syncDrawer(read());
  }

  function closeDrawer() {
    var drawer = document.getElementById("nt-theme-drawer");
    if (!drawer) return;
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    document.body.classList.remove("nt-drawer-open");
  }

  function syncDrawer(state) {
    var drawer = document.getElementById("nt-theme-drawer");
    if (!drawer) return;
    drawer.querySelectorAll("[data-nt-color]").forEach(function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-nt-color") === state.primary);
    });
    drawer.querySelectorAll("[data-nt-layout]").forEach(function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-nt-layout") === state.layout);
    });
    var darkSwitch = drawer.querySelector("[data-nt-dark]");
    if (darkSwitch) darkSwitch.checked = !!state.dark;
    var tabsSwitch = drawer.querySelector("[data-nt-tabs]");
    if (tabsSwitch) tabsSwitch.checked = !!state.tabs;
  }

  function bindDrawer() {
    var openBtn = document.getElementById("nt-theme-open");
    if (openBtn) openBtn.addEventListener("click", openDrawer);

    var drawer = document.getElementById("nt-theme-drawer");
    if (!drawer) return;

    drawer.querySelectorAll("[data-nt-drawer-close]").forEach(function (el) {
      el.addEventListener("click", closeDrawer);
    });

    drawer.querySelectorAll("[data-nt-color]").forEach(function (el) {
      el.addEventListener("click", function () {
        set({ primary: el.getAttribute("data-nt-color") });
      });
    });

    drawer.querySelectorAll("[data-nt-layout]").forEach(function (el) {
      el.addEventListener("click", function () {
        set({ layout: el.getAttribute("data-nt-layout") });
      });
    });

    var darkSwitch = drawer.querySelector("[data-nt-dark]");
    if (darkSwitch) {
      darkSwitch.addEventListener("change", function () {
        set({ dark: darkSwitch.checked });
      });
    }

    var tabsSwitch = drawer.querySelector("[data-nt-tabs]");
    if (tabsSwitch) {
      tabsSwitch.addEventListener("change", function () {
        set({ tabs: tabsSwitch.checked });
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) {
        closeDrawer();
      }
    });
  }

  boot();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      apply(read());
      bindDrawer();
    });
  } else {
    apply(read());
    bindDrawer();
  }

  global.NtTheme = {
    get: get,
    set: set,
    apply: apply,
    boot: boot,
    openDrawer: openDrawer,
    closeDrawer: closeDrawer,
    colors: PRESET_COLORS,
    layouts: LAYOUTS,
    defaults: DEFAULTS,
  };
})(window);
