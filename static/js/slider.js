/* Bosh sahifa slayderi: strelkalar, nuqtalar, barmoq bilan surish, avtomatik aylanish */
(function () {
  "use strict";

  const AUTOPLAY_MS = 7000;
  const SWIPE_MIN = 40;

  function setup(root) {
    const track = root.querySelector("[data-slider-track]");
    const slides = Array.from(root.querySelectorAll("[data-slide]"));
    const prev = root.querySelector("[data-slider-prev]");
    const next = root.querySelector("[data-slider-next]");
    const dotsBox = root.querySelector("[data-slider-dots]");
    if (!track || slides.length < 2 || !dotsBox) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let index = 0;
    let timer = null;

    const dots = slides.map((_, i) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "slider__dot";
      dot.setAttribute("aria-label", i + 1 + "-slayd");
      dot.addEventListener("click", () => goTo(i, true));
      dotsBox.appendChild(dot);
      return dot;
    });

    function paint() {
      dots.forEach((dot, i) => dot.setAttribute("aria-current", i === index ? "true" : "false"));
      slides.forEach((slide, i) => slide.setAttribute("aria-hidden", i === index ? "false" : "true"));
    }

    function goTo(i, stopAuto) {
      index = (i + slides.length) % slides.length;
      track.scrollTo({ left: index * track.clientWidth, behavior: reduced ? "auto" : "smooth" });
      paint();
      if (stopAuto) pause();
    }

    function play() {
      if (reduced || timer) return;
      timer = setInterval(() => goTo(index + 1), AUTOPLAY_MS);
    }

    function pause() {
      clearInterval(timer);
      timer = null;
    }

    prev.addEventListener("click", () => goTo(index - 1, true));
    next.addEventListener("click", () => goTo(index + 1, true));

    root.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") goTo(index - 1, true);
      if (e.key === "ArrowRight") goTo(index + 1, true);
    });

    /* Barmoq yoki sichqoncha bilan surish */
    let startX = null;
    track.addEventListener("pointerdown", (e) => {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      startX = e.clientX;
      pause();
    });
    track.addEventListener("pointerup", (e) => {
      if (startX === null) return;
      const dx = e.clientX - startX;
      startX = null;
      if (Math.abs(dx) > SWIPE_MIN) goTo(index + (dx < 0 ? 1 : -1), true);
      else play();
    });
    track.addEventListener("pointercancel", () => { startX = null; play(); });

    root.addEventListener("mouseenter", pause);
    root.addEventListener("mouseleave", play);
    root.addEventListener("focusin", pause);
    document.addEventListener("visibilitychange", () => (document.hidden ? pause() : play()));

    // O'lcham o'zgarganda joriy slaydga qaytamiz
    let resizeTimer = null;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        track.scrollTo({ left: index * track.clientWidth, behavior: "auto" });
      }, 150);
    });

    paint();
    play();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-slider]").forEach(setup);
  });
})();
