/* Общий скрипт сайта: резервная подгрузка картинок, меню языка, модалка «Get in touch». */
(function () {
  "use strict";

  /* 1. Картинка не нашлась локально (assets/cases/…) — берём её с текущего портфолио.
        Слушатель на capture-фазе, поэтому ловит и ленивые картинки; скрипт стоит в <head>. */
  document.addEventListener("error", function (e) {
    var img = e.target;
    if (!img || img.tagName !== "IMG" || !img.dataset.remote || img.dataset.fallback) return;
    img.dataset.fallback = "1";
    img.src = img.dataset.remote;
  }, true);

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  /* 2. Меню языка (флаг в шапке) */
  function initLangMenu() {
    var btn = document.querySelector(".flag[aria-controls]");
    if (!btn) return;
    var pop = document.getElementById(btn.getAttribute("aria-controls"));
    if (!pop) return;
    function set(open) {
      pop.hidden = !open;
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }
    btn.addEventListener("click", function (e) { e.stopPropagation(); set(pop.hidden); });
    document.addEventListener("click", function (e) { if (!pop.hidden && !pop.contains(e.target)) set(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !pop.hidden) { set(false); btn.focus(); }
    });
  }

  /* 3. Модалка контактов: все кнопки Get in touch ([data-contact]) */
  function initModal() {
    var dlg = document.getElementById("contact-modal");
    if (!dlg || typeof dlg.showModal !== "function") return;   // без поддержки <dialog> остаётся якорь #contacts
    var opener = null;
    /* При блокировке прокрутки скроллбар пропадает и страница расширяется на его ширину (контент «уезжает» вправо).
       Компенсируем отступом справа ровно на ширину скроллбара; на закрытии возвращаем как было. */
    function open(from) {
      opener = from || null;
      var sbw = window.innerWidth - document.documentElement.clientWidth;
      if (sbw > 0) document.body.style.paddingRight = sbw + "px";
      document.body.classList.add("is-modal");
      dlg.showModal();
    }
    function close() { if (dlg.open) dlg.close(); }
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest("[data-contact]");
      if (t) { e.preventDefault(); open(t); return; }
      if (e.target.closest && e.target.closest("[data-modal-close]")) { close(); return; }
      if (e.target === dlg) {                                 // клик по подложке (::backdrop)
        var r = dlg.getBoundingClientRect();
        if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) close();
      }
    });
    dlg.addEventListener("close", function () {
      document.body.classList.remove("is-modal");
      document.body.style.paddingRight = "";
      if (opener && opener.focus) opener.focus();
    });
  }

  ready(function () {
    initLangMenu();
    initModal();
  });
})();
