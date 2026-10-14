document.querySelectorAll("[data-dashboard-tab]").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".dashboard-tab").forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
  });
});
