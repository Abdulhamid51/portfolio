/* Boy matn muharriri: Quill + rasm yuklash + shaklga sinxronlash */
(function () {
  "use strict";

  const TOOLBAR = [
    [{ header: [2, 3, false] }],
    ["bold", "italic", "underline", "strike"],
    ["blockquote", "code-block"],
    [{ list: "ordered" }, { list: "bullet" }],
    [{ align: [] }],
    ["link", "image", "video"],
    ["clean"],
  ];

  function csrfToken() {
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function uploadUrl() {
    const root = document.body.dataset.uploadUrl;
    return root || "/manage/rasm-yuklash/";
  }

  async function prepare(file) {
    // Kesish oynasi mavjud bo'lsa, avval shu yerdan o'tkazamiz
    if (!window.ImageCropper) return file;
    const result = await window.ImageCropper.open(file, {
      ratio: "auto",
      ratioLabel: "Asl nisbat",
      maxWidth: 1600,
      name: file.name,
      type: file.type,
    });
    return result;
  }

  async function uploadImage(file, wrap) {
    const data = new FormData();
    data.append("image", file);
    wrap.classList.add("is-busy");
    try {
      const res = await fetch(uploadUrl(), {
        method: "POST",
        body: data,
        headers: { "X-CSRFToken": csrfToken() },
        credentials: "same-origin",
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || "Yuklab bo'lmadi");
      return payload.url;
    } finally {
      wrap.classList.remove("is-busy");
    }
  }

  function insertImage(quill, url) {
    const range = quill.getSelection(true) || { index: quill.getLength() };
    quill.insertEmbed(range.index, "image", url, "user");
    quill.setSelection(range.index + 1, 0, "silent");
  }

  function wireImages(quill, wrap) {
    quill.getModule("toolbar").addHandler("image", function () {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.onchange = async () => {
        const file = input.files && input.files[0];
        if (!file) return;
        try {
          const ready = await prepare(file);
          if (!ready) return;
          insertImage(quill, await uploadImage(ready, wrap));
        } catch (err) {
          window.alert("Rasmni yuklab bo'lmadi: " + err.message);
        }
      };
      input.click();
    });

    // Tashlab yuborilgan yoki qo'yilgan (paste) rasmlarni ham yuklaymiz
    const handleFiles = async (files) => {
      for (const file of files) {
        if (!file.type.startsWith("image/")) continue;
        try {
          const ready = await prepare(file);
          if (!ready) continue;
          insertImage(quill, await uploadImage(ready, wrap));
        } catch (err) {
          window.alert("Rasmni yuklab bo'lmadi: " + err.message);
        }
      }
    };

    quill.root.addEventListener("drop", (e) => {
      if (!e.dataTransfer || !e.dataTransfer.files.length) return;
      e.preventDefault();
      handleFiles(Array.from(e.dataTransfer.files));
    });

    quill.root.addEventListener("paste", (e) => {
      const items = e.clipboardData ? Array.from(e.clipboardData.files) : [];
      if (!items.length) return;
      e.preventDefault();
      handleFiles(items);
    });
  }

  function sync(quill, source) {
    const html = quill.getText().trim().length || quill.root.querySelector("img, iframe")
      ? quill.root.innerHTML
      : "";
    source.value = html;
  }

  /* ---------- Gemini bilan matnni tozalash ---------- */

  function setTab(wrap, name) {
    wrap.querySelectorAll("[data-tab]").forEach((tab) => {
      const on = tab.dataset.tab === name;
      tab.classList.toggle("is-active", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
    });
    wrap.querySelectorAll("[data-pane]").forEach((pane) => {
      pane.hidden = pane.dataset.pane !== name;
    });
  }

  async function assist(wrap) {
    const quill = wrap._quill;
    const button = wrap.querySelector("[data-assist]");
    const label = wrap.querySelector("[data-assist-label]");
    const result = wrap.querySelector("[data-assist-result]");
    const note = wrap.querySelector("[data-assist-note]");
    const cleanTab = wrap.querySelector('[data-tab="clean"]');
    if (!quill || !button) return;

    const html = quill.root.innerHTML;
    if (!quill.getText().trim()) {
      window.alert("Avval matn yozing.");
      return;
    }

    const original = label.textContent;
    button.disabled = true;
    wrap.classList.add("is-assisting");
    label.textContent = "Tuzatilmoqda…";

    try {
      const res = await fetch(wrap.dataset.assistUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        credentials: "same-origin",
        body: JSON.stringify({ html: html }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Tuzatib bo'lmadi");

      result.innerHTML = data.html;
      wrap._assistHtml = data.html;
      note.textContent = data.model ? data.model + " tayyorladi" : "";
      cleanTab.disabled = false;
      setTab(wrap, "clean");
    } catch (err) {
      window.alert(err.message);
    } finally {
      button.disabled = false;
      wrap.classList.remove("is-assisting");
      label.textContent = original;
    }
  }

  function wireAssist(wrap) {
    const button = wrap.querySelector("[data-assist]");
    if (!button) return;

    button.addEventListener("click", () => assist(wrap));
    wrap.querySelectorAll("[data-tab]").forEach((tab) => {
      tab.addEventListener("click", () => {
        if (!tab.disabled) setTab(wrap, tab.dataset.tab);
      });
    });

    const back = wrap.querySelector("[data-assist-back]");
    if (back) back.addEventListener("click", () => setTab(wrap, "source"));

    const apply = wrap.querySelector("[data-assist-apply]");
    if (apply) {
      apply.addEventListener("click", () => {
        const quill = wrap._quill;
        if (!quill || !wrap._assistHtml) return;
        wrap._previousHtml = quill.root.innerHTML;
        quill.clipboard.dangerouslyPasteHTML(wrap._assistHtml, "user");
        setTab(wrap, "source");
        showUndo(wrap);
      });
    }
  }

  function showUndo(wrap) {
    const foot = wrap.querySelector(".richtext__foot");
    if (!foot || foot.querySelector("[data-assist-undo]")) return;
    const undo = document.createElement("button");
    undo.type = "button";
    undo.className = "richtext__undo";
    undo.dataset.assistUndo = "1";
    undo.textContent = "Avvalgi matnni qaytarish";
    undo.addEventListener("click", () => {
      if (wrap._previousHtml) {
        wrap._quill.clipboard.dangerouslyPasteHTML(wrap._previousHtml, "user");
      }
      undo.remove();
    });
    foot.insertBefore(undo, foot.firstChild);
  }

  function init(wrap) {
    if (wrap.dataset.ready) return;
    const editorEl = wrap.querySelector("[data-richtext-editor]");
    const source = wrap.querySelector("[data-richtext-source]");
    const counter = wrap.querySelector("[data-richtext-count]");
    if (!editorEl || !source || !window.Quill) return;

    const quill = new window.Quill(editorEl, {
      theme: "snow",
      placeholder: "Loyiha haqida bemalol yozing — sarlavhalar, ro'yxatlar, rasmlar, iqtiboslar…",
      modules: { toolbar: TOOLBAR },
    });

    wireImages(quill, wrap);

    const update = () => {
      sync(quill, source);
      if (counter) {
        const words = quill.getText().trim().split(/\s+/).filter(Boolean).length;
        counter.textContent = words + " so'z";
      }
    };
    quill.on("text-change", update);
    update();

    const form = wrap.closest("form");
    if (form) form.addEventListener("submit", () => sync(quill, source));

    wrap.dataset.ready = "1";
    wrap._quill = quill;
    wireAssist(wrap);
  }

  function initAll(root) {
    (root || document).querySelectorAll("[data-richtext]").forEach(init);
  }

  document.addEventListener("DOMContentLoaded", () => initAll());
  window.initRichText = initAll;
})();
