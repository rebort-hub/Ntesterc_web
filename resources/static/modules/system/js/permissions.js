(function () {
  function syncTypeFields(form) {
    if (!form) return;
    var typeInput = form.querySelector('input[name="type"]:checked');
    var type = typeInput ? typeInput.value : "menu";
    var showCode = type !== "directory";
    var showPath = type === "menu";
    var showOpen = type === "menu";

    var codeField = form.querySelector('[data-nt-field="code"]');
    var pathField = form.querySelector('[data-nt-field="path"]');
    var openField = form.querySelector('[data-nt-field="open_type"]');

    if (codeField) {
      codeField.style.display = showCode ? "" : "none";
      var codeInput = codeField.querySelector('input[name="code"]');
      if (codeInput) {
        codeInput.required = showCode;
        if (!showCode) codeInput.value = codeInput.value || "dir." + Date.now();
      }
    }
    if (pathField) {
      pathField.style.display = showPath ? "" : "none";
      if (!showPath) {
        var pathInput = pathField.querySelector('input[name="path"]');
        if (pathInput) pathInput.value = "";
      }
    }
    if (openField) {
      openField.style.display = showOpen ? "" : "none";
      if (!showOpen) {
        var openInput = openField.querySelector('select[name="open_type"]');
        if (openInput) openInput.value = "";
      }
    }
  }

  function bindTypeSwitch() {
    document.querySelectorAll("#permForm").forEach(function (form) {
      form.querySelectorAll('input[name="type"]').forEach(function (radio) {
        radio.addEventListener("change", function () {
          syncTypeFields(form);
        });
      });
      syncTypeFields(form);
    });

    // 弹窗打开后根据 fill 再同步一次
    document.querySelectorAll('[data-nt-modal-open="permFormModal"]').forEach(function (btn) {
      btn.addEventListener("click", function () {
        setTimeout(function () {
          var form = document.getElementById("permForm");
          syncTypeFields(form);
          if (window.NtIconPicker) window.NtIconPicker.bind(form);
        }, 0);
      });
    });
  }

  function bindTreeToggle() {
    document.querySelectorAll("[data-nt-tree-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var row = btn.closest("tr");
        if (!row) return;
        var id = row.getAttribute("data-id");
        var open = btn.classList.toggle("is-open");
        btn.textContent = open ? "▾" : "▸";
        toggleChildren(id, open);
      });
    });
  }

  function toggleChildren(parentId, show) {
    document.querySelectorAll('tr[data-parent="' + parentId + '"]').forEach(function (child) {
      child.style.display = show ? "" : "none";
      if (!show) {
        var cid = child.getAttribute("data-id");
        var toggle = child.querySelector("[data-nt-tree-toggle]");
        if (toggle) {
          toggle.classList.remove("is-open");
          toggle.textContent = "▸";
        }
        toggleChildren(cid, false);
      }
    });
  }

  function bindEnableSwitch() {
    document.querySelectorAll("[data-nt-perm-enable]").forEach(function (input) {
      input.addEventListener("change", function () {
        var form = input.closest("form");
        if (!form) return;
        var hidden = form.querySelector('input[name="is_enabled"]');
        if (hidden) hidden.value = input.checked ? "1" : "0";
        form.submit();
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      bindTypeSwitch();
      bindTreeToggle();
      bindEnableSwitch();
    });
  } else {
    bindTypeSwitch();
    bindTreeToggle();
    bindEnableSwitch();
  }
})();
