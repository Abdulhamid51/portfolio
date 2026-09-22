/* Sayt bo'ylab ishlaydigan kichik yordamchilar */
(function () {
  "use strict";

  /* Yorug' / to'q rejim */
  const KEY = "edition";
  const root = document.documentElement;

  function applyEdition(value) {
    root.dataset.edition = value;
    document.querySelectorAll("[data-edition-toggle]").forEach((btn) => {
      btn.textContent = value === "night" ? "Yorug' rejim" : "To'q rejim";
      btn.setAttribute("aria-pressed", value === "night" ? "true" : "false");
    });
  }

  try {
    applyEdition(localStorage.getItem(KEY) || "day");
  } catch (e) {
    applyEdition("day");
  }

  document.addEventListener("click", (e) => {
    const toggle = e.target.closest("[data-edition-toggle]");
    if (!toggle) return;
    e.preventDefault();
    const next = root.dataset.edition === "night" ? "day" : "night";
    applyEdition(next);
    try { localStorage.setItem(KEY, next); } catch (err) { /* shaxsiy rejim */ }
  });

  /* Formset: yangi qator qo'shish */
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-add-row]");
    if (!btn) return;
    e.preventDefault();
    const prefix = btn.dataset.addRow;
    const container = document.querySelector('[data-rows="' + prefix + '"]');
    const total = document.querySelector("#id_" + prefix + "-TOTAL_FORMS");
    const template = container.querySelector(".inline-row:last-child");
    if (!container || !total || !template) return;

    const index = parseInt(total.value, 10);
    const clone = template.cloneNode(true);
    clone.querySelectorAll("input, select, textarea, label").forEach((el) => {
      ["name", "id", "for"].forEach((attr) => {
        const val = el.getAttribute(attr);
        if (val) el.setAttribute(attr, val.replace(/-\d+-/, "-" + index + "-"));
      });
      if (el.type === "checkbox") el.checked = false;
      else if (el.tagName !== "SELECT" && el.type !== "hidden") el.value = "";
    });
    clone.querySelectorAll(".errorlist, a").forEach((el) => el.remove());
    container.appendChild(clone);
    total.value = index + 1;
  });

  /* Matn maydoni burchagida belgilar hisobi */
  document.querySelectorAll("textarea[maxlength]").forEach((area) => {
    const limit = parseInt(area.getAttribute("maxlength"), 10);
    if (!limit) return;

    const wrap = document.createElement("div");
    wrap.className = "counted";
    area.parentNode.insertBefore(wrap, area);
    wrap.appendChild(area);

    const badge = document.createElement("span");
    badge.className = "counted__value";
    wrap.appendChild(badge);

    const show = () => {
      const used = area.value.length;
      badge.textContent = used + " / " + limit;
      badge.classList.toggle("is-near", used >= limit * 0.9);
    };
    area.addEventListener("input", show);
    show();
  });

  /* Chop etish tugmasi */
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-print]")) {
      e.preventDefault();
      window.print();
    }
  });

  /* O'chirishdan oldin tasdiqlash */
  document.addEventListener("submit", (e) => {
    const form = e.target.closest("form[data-confirm]");
    if (form && !window.confirm(form.dataset.confirm)) e.preventDefault();
  });

  /* Slayder (range) maydonlari yonida joriy qiymat */
  document.querySelectorAll("input.f-range").forEach((input) => {
    const out = document.createElement("output");
    out.className = "f-range__value";
    const show = () => { out.textContent = input.value + (input.dataset.unit || ""); };
    input.insertAdjacentElement("afterend", out);
    input.addEventListener("input", show);
    show();
  });

  /* Flash xabarlarini bir necha soniyadan keyin yopish */
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity .5s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 550);
    }, 6000);
  });
})();
