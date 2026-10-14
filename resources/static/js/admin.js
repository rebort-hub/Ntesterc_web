(function () {
  const shell = document.querySelector(".admin-shell");
  const toggle = document.getElementById("sidebar-toggle");

  if (toggle && shell) {
    toggle.addEventListener("click", () => {
      shell.classList.toggle("is-sidebar-collapsed");
    });
  }

  document.querySelectorAll("[data-menu-group]").forEach((group) => {
    const trigger = group.querySelector(".menu-group__trigger");
    if (!trigger) return;
    trigger.addEventListener("click", () => {
      const open = group.classList.toggle("is-open");
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
})();
