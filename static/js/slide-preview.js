/* Slayd formasidagi jonli ko'rinish: sozlamalar o'zgarishi bilan yangilanadi */
(function () {
  "use strict";

  const box = document.querySelector("[data-slide-preview]");
  if (!box) return;

  const slide = box.querySelector("[data-preview-slide]");
  const img = box.querySelector("[data-preview-img]");
  const blurImg = box.querySelector("[data-preview-blur]");
  const empty = box.querySelector("[data-preview-empty]");
  const panel = box.querySelector("[data-preview-panel]");
  const titleEl = box.querySelector("[data-preview-title]");
  const textEl = box.querySelector("[data-preview-text]");
  const linkEl = box.querySelector("[data-preview-link]");

  const el = (id) => document.getElementById(id);
  const fields = {
    title: el("id_title"),
    subtitle: el("id_subtitle"),
    linkLabel: el("id_link_label"),
    url: el("id_url"),
    side: el("id_side"),
    style: el("id_panel_style"),
    panelBlur: el("id_panel_blur"),
    imageBlur: el("id_image_blur"),
    blurWidth: el("id_blur_width"),
  };
  const fileInput = document.querySelector('[data-crop] input[type="file"]');

  let objectUrl = null;

  function currentImage() {
    if (fileInput && fileInput.files && fileInput.files[0]) {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = URL.createObjectURL(fileInput.files[0]);
      return objectUrl;
    }
    return box.dataset.current || "";
  }

  function paint() {
    const src = currentImage();
    if (src) {
      img.src = src;
      blurImg.src = src;
      img.hidden = blurImg.hidden = false;
      empty.hidden = true;
    } else {
      img.removeAttribute("src");
      blurImg.removeAttribute("src");
      img.hidden = blurImg.hidden = true;
      empty.hidden = false;
    }

    const side = fields.side ? fields.side.value : "left";
    slide.className = "slide slide--" + side;

    const style = fields.style ? fields.style.value : "glass";
    panel.className = "slide__panel slide__panel--" + style;

    const panelBlur = fields.panelBlur ? fields.panelBlur.value : 16;
    const imageBlur = fields.imageBlur ? fields.imageBlur.value : 12;
    const blurWidth = fields.blurWidth ? fields.blurWidth.value : 52;
    slide.style.setProperty("--panel-blur", panelBlur + "px");
    slide.style.setProperty("--image-blur", imageBlur + "px");
    slide.style.setProperty("--blur-width", blurWidth + "%");
    blurImg.style.display = Number(imageBlur) > 0 ? "" : "none";

    titleEl.textContent = (fields.title && fields.title.value) || "Sarlavha";
    const sub = fields.subtitle ? fields.subtitle.value.trim() : "";
    textEl.textContent = sub;
    textEl.hidden = !sub;
    linkEl.textContent = (fields.linkLabel && fields.linkLabel.value.trim()) || "Batafsil";
    linkEl.hidden = !(fields.url && fields.url.value.trim());
  }

  Object.values(fields).forEach((input) => {
    if (!input) return;
    input.addEventListener("input", paint);
    input.addEventListener("change", paint);
  });
  if (fileInput) fileInput.addEventListener("change", () => setTimeout(paint, 60));
  // Kesish oynasidan qaytgan rasm ham ko'rinsin
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-apply], [data-original]")) setTimeout(paint, 300);
  });

  paint();
})();
