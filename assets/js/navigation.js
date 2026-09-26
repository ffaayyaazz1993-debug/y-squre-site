/* Y-Square — navigation.js
   Mobile menu + search bar toggle. No dependencies. */
(function () {
  'use strict';
  var YSQ = window.YSQ || {};
  var u = (YSQ.utils = YSQ.utils || {});

  function init() {
    var toggle = u.$('.nav-toggle');
    var list = u.$('.nav-list');
    var sbToggle = u.$('.search-toggle');
    var bar = u.$('.searchbar');

    if (toggle && list) {
      u.on(toggle, 'click', function () {
        var open = list.classList.toggle('open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      });

      // Close the drawer when a destination is chosen, and on Escape.
      u.$$('a', list).forEach(function (a) {
        u.on(a, 'click', function () {
          list.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
        });
      });
      u.on(document, 'keydown', function (e) {
        if (e.key === 'Escape' && list.classList.contains('open')) {
          list.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.focus();
        }
      });
    }

    if (sbToggle && bar) {
      u.on(sbToggle, 'click', function () {
        var open = bar.hasAttribute('hidden');
        if (open) { bar.removeAttribute('hidden'); }
        else { bar.setAttribute('hidden', ''); }
        sbToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open) { var i = u.$('input[type="search"]', bar); if (i) i.focus(); }
      });
    }

    // "/" focuses search, the convention on wire sites.
    u.on(document, 'keydown', function (e) {
      if (e.key !== '/' || e.metaKey || e.ctrlKey) return;
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      var box = u.$('.searchbar');
      var btn = u.$('.search-toggle');
      if (box && btn) { e.preventDefault(); btn.click(); }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
