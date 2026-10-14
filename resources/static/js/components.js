(function (global) {
  function openModal(id, options) {
    const el = typeof id === "string" ? document.getElementById(id) : id;
    if (!el) return;
    const opts = options || {};
    const titleEl = el.querySelector("[data-nt-modal-title]");
    if (titleEl) {
      titleEl.textContent = opts.title || el.getAttribute("data-nt-default-title") || titleEl.textContent;
    }
    if (opts.formId) {
      const form = document.getElementById(opts.formId);
      if (form) {
        if (opts.action) form.setAttribute("action", opts.action);
        if (opts.reset) form.reset();
        if (opts.fill) fillForm(opts.formId, opts.fill);
      }
    }
    el.classList.add("is-open");
    el.setAttribute("aria-hidden", "false");
    document.body.classList.add("nt-modal-open");
  }

  function closeModal(id) {
    const el = typeof id === "string" ? document.getElementById(id) : id;
    if (!el) return;
    el.classList.remove("is-open");
    el.setAttribute("aria-hidden", "true");
    if (!document.querySelector(".nt-modal.is-open")) {
      document.body.classList.remove("nt-modal-open");
    }
  }

  function fillForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form || !data) return;
    Object.keys(data).forEach((name) => {
      const fields = form.querySelectorAll(`[name="${name}"]`);
      if (!fields.length) return;
      const value = data[name];
      fields.forEach((field) => {
        if (field.type === "checkbox") {
          field.checked = Boolean(value);
        } else if (field.type === "radio") {
          field.checked = field.value === String(value);
        } else {
          field.value = value == null ? "" : String(value);
        }
      });
    });
  }

  function parseDatasetJson(raw) {
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  function bindModal(root) {
    root.querySelectorAll("[data-nt-modal-open]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const modalId = btn.getAttribute("data-nt-modal-open");
        const fill = parseDatasetJson(btn.getAttribute("data-nt-fill"));
        const options = {
          title: btn.getAttribute("data-nt-modal-title") || undefined,
          formId: btn.getAttribute("data-nt-form") || undefined,
          action: btn.getAttribute("data-nt-action") || undefined,
          fill: fill || undefined,
          reset: btn.hasAttribute("data-nt-reset"),
        };
        openModal(modalId, options);

        // 额外：密码必填开关（新建必填，编辑不必填）
        const requiredNames = (btn.getAttribute("data-nt-required") || "").split(",").filter(Boolean);
        const optionalNames = (btn.getAttribute("data-nt-optional") || "").split(",").filter(Boolean);
        const form = options.formId ? document.getElementById(options.formId) : null;
        if (form) {
          requiredNames.forEach((name) => {
            const field = form.querySelector(`[name="${name}"]`);
            if (field) field.required = true;
          });
          optionalNames.forEach((name) => {
            const field = form.querySelector(`[name="${name}"]`);
            if (field) field.required = false;
          });
        }

        // 删除确认文案
        const msg = btn.getAttribute("data-nt-confirm-text");
        if (msg) {
          const tip = document.querySelector(`#${modalId} [data-nt-confirm-message]`);
          if (tip) tip.textContent = msg;
        }
      });
    });

    root.querySelectorAll(".nt-modal").forEach((modal) => {
      modal.querySelectorAll("[data-nt-modal-close]").forEach((btn) => {
        btn.addEventListener("click", () => closeModal(modal));
      });
      modal.querySelectorAll("[data-nt-modal-ok]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const formId = btn.getAttribute("data-nt-modal-submit");
          if (formId) {
            const form = document.getElementById(formId);
            if (form) {
              if (typeof form.requestSubmit === "function") {
                form.requestSubmit();
              } else {
                form.submit();
              }
              return;
            }
          }
          const event = new CustomEvent("nt-modal:ok", {
            detail: { id: modal.id },
            cancelable: true,
          });
          if (modal.dispatchEvent(event)) {
            closeModal(modal);
          }
        });
      });
    });
  }

  function dismissToast(toast, cleanUrl) {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    window.setTimeout(() => {
      const host = toast.parentElement;
      toast.remove();
      if (host && !host.querySelector("[data-nt-toast]")) {
        host.remove();
      }
      if (cleanUrl) {
        const url = new URL(window.location.href);
        if (url.searchParams.has("ok") || url.searchParams.has("err")) {
          url.searchParams.delete("ok");
          url.searchParams.delete("err");
          window.history.replaceState({}, "", url.pathname + url.search + url.hash);
        }
      }
    }, 250);
  }

  function bindToast(root, duration) {
    const ms = typeof duration === "number" ? duration : 2800;
    root.querySelectorAll("[data-nt-toast]").forEach((toast) => {
      const closer = toast.querySelector("[data-nt-toast-close]");
      if (closer) {
        closer.addEventListener("click", () => dismissToast(toast, true));
      }
      window.setTimeout(() => dismissToast(toast, true), ms);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindModal(document);
    bindToast(document);
  });

  global.NtUI = {
    openModal,
    closeModal,
    fillForm,
    bindModal,
    dismissToast,
    bindToast,
  };
})(window);
