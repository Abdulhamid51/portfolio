/* Rasmni kesish oynasi: surish, kattalashtirish, nisbatni tanlash.
   Natija fayl maydoniga kesilgan rasm sifatida qaytadi — serverga tayyor holda boradi. */
(function () {
  "use strict";

  const DEFAULT_MAX_WIDTH = 1800;
  const QUALITY = 0.92;

  let overlay, stageEl, frameEl, imgEl, zoomEl, ratioBox, hintEl;
  let job = null; // { natural, frame, ratio, zoom, tx, ty, resolve, file }

  /* ---------- Oyna qurish ---------- */

  function build() {
    overlay = document.createElement("div");
    overlay.className = "cropper";
    overlay.hidden = true;
    overlay.innerHTML =
      '<div class="cropper__box" role="dialog" aria-modal="true" aria-label="Rasmni kesish">' +
      '  <div class="cropper__head">' +
      '    <strong>Rasmni joylashtiring</strong>' +
      '    <span class="cropper__hint" data-hint></span>' +
      '  </div>' +
      '  <div class="cropper__stage" data-stage>' +
      '    <div class="cropper__frame" data-frame><img alt="" data-img draggable="false"></div>' +
      '  </div>' +
      '  <div class="cropper__tools">' +
      '    <div class="cropper__ratios" data-ratios></div>' +
      '    <label class="cropper__zoom">Kattalashtirish' +
      '      <input type="range" min="1" max="4" step="0.01" value="1" data-zoom>' +
      '    </label>' +
      '  </div>' +
      '  <div class="cropper__actions">' +
      '    <button type="button" class="btn btn--primary" data-apply>Kesish va qo\'yish</button>' +
      '    <button type="button" class="btn btn--ghost" data-original>Asl holida qoldirish</button>' +
      '    <button type="button" class="btn btn--ghost cropper__cancel" data-cancel>Bekor qilish</button>' +
      '  </div>' +
      '</div>';
    document.body.appendChild(overlay);

    stageEl = overlay.querySelector("[data-stage]");
    frameEl = overlay.querySelector("[data-frame]");
    imgEl = overlay.querySelector("[data-img]");
    zoomEl = overlay.querySelector("[data-zoom]");
    ratioBox = overlay.querySelector("[data-ratios]");
    hintEl = overlay.querySelector("[data-hint]");

    zoomEl.addEventListener("input", () => {
      setZoom(parseFloat(zoomEl.value));
    });
    overlay.querySelector("[data-apply]").addEventListener("click", apply);
    overlay.querySelector("[data-original]").addEventListener("click", () => finish(job && job.file));
    overlay.querySelector("[data-cancel]").addEventListener("click", () => finish(null));
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) finish(null);
    });
    document.addEventListener("keydown", (e) => {
      if (!job) return;
      if (e.key === "Escape") finish(null);
      if (e.key === "Enter" && !e.target.closest("input[type=range]")) apply();
    });

    wireDrag();
    window.addEventListener("resize", () => { if (job) layout(true); });
  }

  /* ---------- Surish ---------- */

  function wireDrag() {
    let startX = 0, startY = 0, baseX = 0, baseY = 0, dragging = false;

    frameEl.addEventListener("pointerdown", (e) => {
      if (!job) return;
      dragging = true;
      frameEl.setPointerCapture(e.pointerId);
      frameEl.classList.add("is-dragging");
      startX = e.clientX; startY = e.clientY;
      baseX = job.tx; baseY = job.ty;
    });
    frameEl.addEventListener("pointermove", (e) => {
      if (!dragging || !job) return;
      job.tx = baseX + (e.clientX - startX);
      job.ty = baseY + (e.clientY - startY);
      clamp();
      paint();
    });
    const stop = () => { dragging = false; frameEl.classList.remove("is-dragging"); };
    frameEl.addEventListener("pointerup", stop);
    frameEl.addEventListener("pointercancel", stop);

    frameEl.addEventListener("wheel", (e) => {
      if (!job) return;
      e.preventDefault();
      setZoom(job.zoom * (e.deltaY < 0 ? 1.08 : 1 / 1.08), e);
    }, { passive: false });
  }

  /* ---------- Hisob-kitob ---------- */

  function baseScale() {
    return Math.max(job.frame.w / job.natural.w, job.frame.h / job.natural.h);
  }

  function clamp() {
    const s = baseScale() * job.zoom;
    const dw = job.natural.w * s;
    const dh = job.natural.h * s;
    job.tx = dw <= job.frame.w ? (job.frame.w - dw) / 2 : Math.min(0, Math.max(job.frame.w - dw, job.tx));
    job.ty = dh <= job.frame.h ? (job.frame.h - dh) / 2 : Math.min(0, Math.max(job.frame.h - dh, job.ty));
  }

  function paint() {
    const s = baseScale() * job.zoom;
    imgEl.style.width = job.natural.w * s + "px";
    imgEl.style.height = job.natural.h * s + "px";
    imgEl.style.transform = "translate(" + job.tx + "px," + job.ty + "px)";
  }

  function setZoom(value, wheelEvent) {
    const next = Math.min(4, Math.max(1, value));
    if (next === job.zoom) return;
    // Kattalashtirganda markaz (yoki kursor ostidagi nuqta) joyida qolsin
    const rect = frameEl.getBoundingClientRect();
    const px = wheelEvent ? wheelEvent.clientX - rect.left : job.frame.w / 2;
    const py = wheelEvent ? wheelEvent.clientY - rect.top : job.frame.h / 2;
    const ratio = next / job.zoom;
    job.tx = px - (px - job.tx) * ratio;
    job.ty = py - (py - job.ty) * ratio;
    job.zoom = next;
    zoomEl.value = String(next);
    clamp();
    paint();
  }

  function layout(keepCenter) {
    // Ramka o'lchami: ekranga sig'adigan eng katta holat
    const maxW = Math.min(stageEl.clientWidth || 640, 720);
    const maxH = Math.max(220, Math.min(window.innerHeight - 340, 460));
    let w = maxW;
    let h = w / job.ratio;
    if (h > maxH) { h = maxH; w = h * job.ratio; }

    let centerNat = null;
    if (keepCenter && job.frame.w) {
      const s = baseScale() * job.zoom;
      centerNat = {
        x: (-job.tx + job.frame.w / 2) / s,
        y: (-job.ty + job.frame.h / 2) / s,
      };
    }

    job.frame = { w: Math.round(w), h: Math.round(h) };
    frameEl.style.width = job.frame.w + "px";
    frameEl.style.height = job.frame.h + "px";

    const s = baseScale() * job.zoom;
    if (centerNat) {
      job.tx = job.frame.w / 2 - centerNat.x * s;
      job.ty = job.frame.h / 2 - centerNat.y * s;
    } else {
      job.tx = (job.frame.w - job.natural.w * s) / 2;
      job.ty = (job.frame.h - job.natural.h * s) / 2;
    }
    clamp();
    paint();
  }

  /* ---------- Nisbat tugmalari ---------- */

  function buildRatios(recommended, label) {
    const options = [
      { key: recommended, text: label + " (tavsiya)" },
      { key: 1, text: "1:1" },
      { key: 4 / 3, text: "4:3" },
      { key: 16 / 9, text: "16:9" },
      { key: job.natural.w / job.natural.h, text: "Asl nisbat" },
    ];
    ratioBox.innerHTML = "";
    const seen = [];
    options
      .filter((opt) => {
        if (seen.some((k) => Math.abs(k - opt.key) < 0.01)) return false;
        seen.push(opt.key);
        return true;
      })
      .forEach((opt, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cropper__ratio";
      btn.textContent = opt.text;
      btn.setAttribute("aria-pressed", i === 0 ? "true" : "false");
      btn.addEventListener("click", () => {
        job.ratio = opt.key;
        Array.from(ratioBox.children).forEach((b) => b.setAttribute("aria-pressed", "false"));
        btn.setAttribute("aria-pressed", "true");
        layout(true);
      });
        ratioBox.appendChild(btn);
      });
  }

  /* ---------- Ochish va yakunlash ---------- */

  function parseRatio(text, natural) {
    if (!text || text === "auto") return natural.w / natural.h;
    const parts = String(text).split("/");
    const w = parseFloat(parts[0]);
    const h = parseFloat(parts[1] || 1);
    return w && h ? w / h : 16 / 9;
  }

  function open(source, options) {
    if (!overlay) build();
    return new Promise((resolve) => {
      const url = typeof source === "string" ? source : URL.createObjectURL(source);
      const probe = new Image();
      probe.onload = () => {
        job = {
          file: typeof source === "string" ? null : source,
          url: url,
          revoke: typeof source !== "string",
          natural: { w: probe.naturalWidth, h: probe.naturalHeight },
          frame: { w: 0, h: 0 },
          ratio: parseRatio(options.ratio, { w: probe.naturalWidth, h: probe.naturalHeight }),
          zoom: 1,
          tx: 0,
          ty: 0,
          maxWidth: options.maxWidth || DEFAULT_MAX_WIDTH,
          name: options.name || "rasm.jpg",
          type: options.type || "image/jpeg",
          resolve: resolve,
        };
        imgEl.src = url;
        zoomEl.value = "1";
        hintEl.textContent = probe.naturalWidth + "×" + probe.naturalHeight + " px";
        overlay.hidden = false;
        document.body.style.overflow = "hidden";
        buildRatios(job.ratio, options.ratioLabel || "Tavsiya");
        layout(false);
      };
      probe.onerror = () => {
        window.alert("Rasmni ochib bo'lmadi.");
        resolve(null);
      };
      probe.src = url;
    });
  }

  function finish(file) {
    if (!job) return;
    const resolve = job.resolve;
    if (job.revoke) URL.revokeObjectURL(job.url);
    overlay.hidden = true;
    document.body.style.overflow = "";
    imgEl.removeAttribute("src");
    job = null;
    resolve(file || null);
  }

  function apply() {
    if (!job) return;
    const s = baseScale() * job.zoom;
    const sx = Math.max(0, -job.tx / s);
    const sy = Math.max(0, -job.ty / s);
    const sw = Math.min(job.natural.w - sx, job.frame.w / s);
    const sh = Math.min(job.natural.h - sy, job.frame.h / s);

    const outW = Math.max(1, Math.min(job.maxWidth, Math.round(sw)));
    const outH = Math.max(1, Math.round(outW * (sh / sw)));

    const canvas = document.createElement("canvas");
    canvas.width = outW;
    canvas.height = outH;
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(imgEl, sx, sy, sw, sh, 0, 0, outW, outH);

    const png = job.type === "image/png";
    const outType = png ? "image/png" : "image/jpeg";
    const base = job.name.replace(/\.[^.]+$/, "") || "rasm";
    const outName = base + "-" + outW + "x" + outH + (png ? ".png" : ".jpg");

    canvas.toBlob((blob) => {
      if (!blob) return finish(job.file);
      finish(new File([blob], outName, { type: outType }));
    }, outType, png ? undefined : QUALITY);
  }

  /* ---------- Fayl maydonlari bilan bog'lash ---------- */

  function fieldOptions(wrap, file) {
    return {
      ratio: wrap.dataset.ratio,
      ratioLabel: wrap.dataset.ratioLabel,
      maxWidth: parseInt(wrap.dataset.maxWidth, 10) || DEFAULT_MAX_WIDTH,
      name: file ? file.name : "rasm.jpg",
      type: file ? file.type : "image/jpeg",
    };
  }

  function putFile(input, file) {
    if (!window.DataTransfer) return false;
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    return true;
  }

  function showResult(wrap, file) {
    const box = wrap.querySelector("[data-result]");
    if (!box) return;
    const img = box.querySelector("[data-result-img]");
    const note = box.querySelector("[data-result-note]");
    if (img.dataset.url) URL.revokeObjectURL(img.dataset.url);
    const url = URL.createObjectURL(file);
    img.dataset.url = url;
    img.src = url;
    note.textContent = file.name + " · " + Math.round(file.size / 1024) + " KB";
    box.hidden = false;
  }

  async function handleFile(wrap, input) {
    const file = input.files && input.files[0];
    if (!file || !file.type.startsWith("image/")) return;
    wrap._lastFile = file;
    const cropped = await open(file, fieldOptions(wrap, file));
    if (cropped && cropped !== file) {
      if (putFile(input, cropped)) showResult(wrap, cropped);
    } else if (cropped === file) {
      showResult(wrap, file);
    }
  }

  /* Boshqa skriptlar uchun (masalan, matn muharriri) */
  window.ImageCropper = { open: open };

  document.addEventListener("change", (e) => {
    const input = e.target;
    if (!input.matches || !input.matches('input[type="file"]')) return;
    const wrap = input.closest("[data-crop]");
    if (wrap) handleFile(wrap, input);
  });

  document.addEventListener("click", async (e) => {
    // Saytda turgan rasmni qayta kesish
    const recrop = e.target.closest("[data-recrop]");
    if (recrop) {
      e.preventDefault();
      const wrap = recrop.closest("[data-crop]");
      const input = wrap.querySelector('input[type="file"]');
      const src = recrop.dataset.src;
      const name = src.split("/").pop() || "rasm.jpg";
      const cropped = await open(src, Object.assign(fieldOptions(wrap, null), {
        name: name,
        type: /\.png$/i.test(name) ? "image/png" : "image/jpeg",
      }));
      if (cropped && putFile(input, cropped)) showResult(wrap, cropped);
      return;
    }
    // Tanlangan rasmni qayta sozlash
    const edit = e.target.closest("[data-result-edit]");
    if (edit) {
      e.preventDefault();
      const wrap = edit.closest("[data-crop]");
      const input = wrap.querySelector('input[type="file"]');
      const file = (input.files && input.files[0]) || wrap._lastFile;
      if (!file) return;
      const cropped = await open(wrap._lastFile || file, fieldOptions(wrap, file));
      if (cropped && putFile(input, cropped)) showResult(wrap, cropped);
    }
  });
})();
