/* Y-Squre market terminal enhancements — no network calls, no data claims. */
(function () {
  'use strict';

  function clock() {
    var el = document.querySelector('[data-mkt-clock]');
    if (!el) return;
    function tick() {
      var d = new Date();
      function fmt(tz) {
        try {
          return new Intl.DateTimeFormat('en-GB', {
            timeZone: tz, hour: '2-digit', minute: '2-digit',
            second: '2-digit', hour12: false
          }).format(d);
        } catch (e) { return '--:--:--'; }
      }
      el.textContent = 'UTC ' + fmt('UTC') + '  /  IST ' + fmt('Asia/Kolkata');
    }
    tick();
    setInterval(tick, 1000);
  }

  function tape() {
    var track = document.querySelector('.mkt-tape-track');
    if (!track || track.dataset.cloned === '1') return;
    // Duplicate once so the CSS -50% translate loops seamlessly.
    var items = Array.prototype.slice.call(track.children);
    items.forEach(function (node) {
      var clone = node.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      track.appendChild(clone);
    });
    track.dataset.cloned = '1';
  }

  function filters() {
    var bar = document.querySelector('[data-mkt-filters]');
    if (!bar) return;
    var rows = Array.prototype.slice.call(
      document.querySelectorAll('[data-mkt-quick] [data-desk]')
    );
    var buttons = Array.prototype.slice.call(bar.querySelectorAll('[data-filter]'));
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var want = btn.getAttribute('data-filter');
        buttons.forEach(function (b) {
          b.setAttribute('aria-pressed', String(b === btn));
        });
        rows.forEach(function (row) {
          var desk = row.getAttribute('data-desk') || '';
          row.hidden = !(want === 'all' || desk.indexOf(want) !== -1);
        });
      });
    });
  }

  function init() {
    clock();
    tape();
    filters();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
