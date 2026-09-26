/* Y-Square — main.js
   Shared runtime. Vanilla ES5-compatible, no libraries, no trackers.
   Loaded with `defer` on every page. */
(function () {
  'use strict';

  var YSQ = window.YSQ = window.YSQ || {};

  YSQ.config = {
    siteName: 'Y-Square',
    // Bump when the article set changes so the client-side search index
    // cache is invalidated. A future server-side index supersedes this file.
    searchIndexVersion: '2026-09-26',
    searchIndexUrl: '/assets/js/articles.js',
    storageConsentKey: 'ysq_consent',
    storageConsented: 'granted',
    storageDenied: 'denied'
  };

  /* ---------- consent ---------------------------------------------------
   * One store, read by both the banner and the ad loader. Google AdSense's
   * own certified CMP is the authority on EU consent; this records the
   * visitor's choice locally so the UI can respect it and so the policy page
   * has something truthful to describe.
   *
   * A Global Privacy Control signal is treated as an opt-out request:
   * CCPA 7025 makes the browser signal legally equivalent to one. We honour
   * it before the banner is ever shown.
   * ------------------------------------------------------------------- */
  YSQ.consent = {
    gpcActive: function () {
      try { return navigator.globalPrivacyControl === true; } catch (e) { return false; }
    },
    get: function () {
      try { return localStorage.getItem(YSQ.config.storageConsentKey); }
      catch (e) { return null; }
    },
    set: function (value) {
      try { localStorage.setItem(YSQ.config.storageConsentKey, value); } catch (e) {}
      document.documentElement.setAttribute('data-consent', value);
    },
    clear: function () {
      try { localStorage.removeItem(YSQ.config.storageConsentKey); } catch (e) {}
      document.documentElement.removeAttribute('data-consent');
    }
  };

  // Record a GPC signal as a denial before anything renders.
  if (YSQ.consent.gpcActive() && !YSQ.consent.get()) {
    YSQ.consent.set(YSQ.config.storageDenied);
  }

  YSQ.utils = {
    // $ returns a single element; $$ returns an array.
    $: function (sel, root) { return (root || document).querySelector(sel); },
    $$: function (sel, root) {
      return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    },
    on: function (el, evt, fn) { if (el) el.addEventListener(evt, fn, false); },
    debounce: function (fn, wait) {
      var t;
      return function () {
        var ctx = this, args = arguments;
        clearTimeout(t);
        t = setTimeout(function () { fn.apply(ctx, args); }, wait || 150);
      };
    },
    // Absolute URL for canonical/OG tags.
    absolute: function (href) {
      try { return new URL(href, window.location.href).href; } catch (e) { return href; }
    },
    stripTags: function (html) {
      var d = document.createElement('div');
      d.innerHTML = html || '';
      return (d.textContent || d.innerText || '').replace(/\s+/g, ' ').trim();
    },
    // "26 September 2026, 16:30 IST"
    stamp: function (iso) {
      if (!iso) return '';
      var d = new Date(iso);
      if (isNaN(d.getTime())) return '';
      return d.toLocaleString('en-GB', {
        day: '2-digit', month: 'long', year: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Kolkata'
      }) + ' IST';
    },
    // "2 hours ago" — wire services lead with relative time, absolute after 7d.
    ago: function (iso, now) {
      if (!iso) return '';
      var t = new Date(iso).getTime();
      if (isNaN(t)) return '';
      var diff = Math.floor(((now || Date.now()) - t) / 1000);
      if (diff < 0) return 'just now';
      if (diff < 60) return diff + ' seconds ago';
      if (diff < 3600) { var m = Math.floor(diff / 60); return m + (m === 1 ? ' minute ago' : ' minutes ago'); }
      if (diff < 86400) { var h = Math.floor(diff / 3600); return h + (h === 1 ? ' hour ago' : ' hours ago'); }
      if (diff < 604800) { var d = Math.floor(diff / 86400); return d + (d === 1 ? ' day ago' : ' days ago'); }
      return YSQ.utils.stamp(iso).split(',')[0];
    }
  };

  /* ---------- reading time + date enhancement ----------
   * Scans [data-prose] and fills [data-readtime] / [data-stamp] slots so the
   * same markup works with or without JS. */
  YSQ.enhance = function () {
    var u = YSQ.utils;
    var now = Date.now();

    u.$$('[data-readtime]').forEach(function (el) {
      // Scope by nearest prose container, NOT by a data attribute value: the
      // attribute held a URL path, and document.querySelector('/research/...')
      // is a selector syntax error, which threw and aborted the whole pass.
      var scope = el.closest('.prose') || el.closest('article') || document;
      var text = u.stripTags(scope.innerHTML);
      var words = text ? text.split(/\s+/).length : 0;
      if (words > 40) {
        el.textContent = Math.max(1, Math.round(words / 220)) + ' min read';
      } else if (!el.textContent) {
        el.textContent = '1 min read';
      }
    });

    u.$$('[data-stamp]').forEach(function (el) {
      var s = u.stamp(el.getAttribute('data-stamp'));
      if (s) el.textContent = s;
    });

    u.$$('[data-ago]').forEach(function (el) {
      var a = u.ago(el.getAttribute('data-ago'), now);
      if (a) {
        el.textContent = a;
        // Absolute time in the tooltip, relative in the face — the wire convention.
        var abs = u.stamp(el.getAttribute('data-ago'));
        if (abs) el.setAttribute('title', abs);
      }
    });
  };

  /* ---------- mark the current nav item ---------- */
  YSQ.markNav = function () {
    var here = window.location.pathname.replace(/\/index\.html$/, '/');
    if (here === '') here = '/';
    YSQ.utils.$$('.nav-list a').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (href === here || (href !== '/' && here.indexOf(href) === 0)) {
        a.setAttribute('aria-current', 'page');
      }
    });
  };

  YSQ.init = function () {
    // Each pass is isolated: a throw in one must not stop the others from
    // running, or a single bad selector silently disables the whole page.
    try { YSQ.enhance(); } catch (e) { if (window.console) console.error('YSQ.enhance', e); }
    try { YSQ.markNav(); } catch (e) { if (window.console) console.error('YSQ.markNav', e); }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', YSQ.init);
  } else {
    YSQ.init();
  }
})();
