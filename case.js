/* Страницы кейсов: слайдеры и подсветка пункта навигации (общее — в site.js). */
(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  /* Слайдеры: прокрутка со scroll-snap, стрелки, полоски-индикаторы */
  function initSlider(root) {
    var track = root.querySelector(".slider__track");
    var slides = Array.prototype.slice.call(track.querySelectorAll(".slide"));
    var bars = Array.prototype.slice.call(root.querySelectorAll(".slider__bars button"));
    var prev = root.querySelector("[data-prev]");
    var next = root.querySelector("[data-next]");
    var current = 0, raf = 0;

    function left(i) { return slides[i].offsetLeft - slides[0].offsetLeft; }
    function go(i) {
      i = Math.max(0, Math.min(slides.length - 1, i));
      track.scrollTo({ left: left(i), behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    }
    function nearest() {
      var x = track.scrollLeft, best = 0, d = Infinity;
      slides.forEach(function (_, i) {
        var dd = Math.abs(left(i) - x);
        if (dd < d) { d = dd; best = i; }
      });
      return best;
    }
    function update() {
      raf = 0;
      current = nearest();
      bars.forEach(function (b, i) { b.setAttribute("aria-current", i === current ? "true" : "false"); });
      prev.disabled = current === 0;
      next.disabled = current === slides.length - 1;
    }
    track.addEventListener("scroll", function () { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    prev.addEventListener("click", function () { go(current - 1); });
    next.addEventListener("click", function () { go(current + 1); });
    bars.forEach(function (b, i) { b.addEventListener("click", function () { go(i); }); });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(current + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(current - 1); }
    });
    window.addEventListener("resize", update);
    update();
  }

  /* Навигация по разделам: подсвечиваем тот, что сейчас у верха экрана */
  function initSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".case-nav a"));
    if (!links.length) return;
    var pairs = links.map(function (a) {
      return { a: a, s: document.getElementById(a.getAttribute("href").slice(1)) };
    }).filter(function (p) { return p.s; });
    var raf = 0;
    function update() {
      raf = 0;
      var line = window.innerHeight * 0.32, active = pairs[0];
      pairs.forEach(function (p) { if (p.s.getBoundingClientRect().top <= line) active = p; });
      pairs.forEach(function (p) { p.a.classList.toggle("is-active", p === active); });
      /* в горизонтальной ленте (планшет/мобильный) держим активный пункт в поле зрения */
      var ul = active.a.closest("ul");
      if (ul && ul.scrollWidth > ul.clientWidth) {
        var l = active.a.offsetLeft - (ul.clientWidth - active.a.offsetWidth) / 2;
        ul.scrollTo({ left: l });
      }
    }
    window.addEventListener("scroll", function () { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  ready(function () {
    Array.prototype.forEach.call(document.querySelectorAll("[data-slider]"), initSlider);
    initSpy();
  });
})();
