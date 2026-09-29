/* Y-Squre — consent.js
   Cookie notice + stored preference.

   Scope, stated plainly so the privacy page can describe it accurately:
   this records the visitor's choice in localStorage. It does NOT gate Google's
   ad requests — Google's own certified consent message in the AdSense console
   is the authority on EU consent, and that is an account-side setting. We
   deliberately do not push a hand-rolled object into the adsbygoogle queue:
   that produces an ad error, not a non-personalised ad.

   The GPC (Global Privacy Control) signal is honoured — if the browser sends
   it and the visitor has not already chosen, we store "denied" and show no
   dialog. Under CCPA 7025 that signal is an opt-out request.

   Storage blocked (private mode) degrades to an in-memory choice for the
   session rather than failing silently.

   The footer "Cookie choices" link calls window.ysqResetConsent().
*/
(function () {
  'use strict';

  var KEY = 'ysq_consent';
  var BANNER_ID = 'consent-banner';

  function readChoice() {
    try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function writeChoice(v) {
    try { window.localStorage.setItem(KEY, v); } catch (e) { window.__ysqConsent = v; }
  }
  function clearChoice() {
    try { window.localStorage.removeItem(KEY); } catch (e) {}
    try { delete window.__ysqConsent; } catch (e) {}
  }
  function getChoice() { return readChoice() || window.__ysqConsent || null; }

  function gpcActive() {
    try { return navigator.globalPrivacyControl === true; } catch (e) { return false; }
  }

  function applyChoice(choice) {
    if (choice === 'granted' || choice === 'denied') {
      document.documentElement.setAttribute('data-ads-consent', choice);
    }
  }

  function buildBanner() {
    var el = document.createElement('div');
    el.className = 'cookie-banner';
    el.id = BANNER_ID;
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-live', 'polite');
    el.setAttribute('aria-label', 'Cookie consent');
    el.innerHTML =
      '<div class="wrap cookie-inner">' +
        '<p class="cookie-text">' +
          '<strong>This site uses cookies.</strong> Google AdSense sets cookies to measure and ' +
          'personalise advertising on this site and across the wider web. You can accept or ' +
          'decline; declining does not prevent access to any part of this site. See our ' +
          '<a href="/privacy/index.html">Privacy Policy</a> for detail.' +
        '</p>' +
        '<div class="cookie-actions">' +
          '<button type="button" class="btn-cookie-accept" data-consent="granted">Accept</button>' +
          '<button type="button" class="btn-cookie-decline" data-consent="denied">Decline</button>' +
        '</div>' +
      '</div>';
    return el;
  }

  function showBanner() {
    if (document.getElementById(BANNER_ID)) { return; }
    var el = buildBanner();
    document.body.appendChild(el);
    window.requestAnimationFrame(function () { el.classList.add('show'); });

    el.addEventListener('click', function (ev) {
      var btn = ev.target.closest ? ev.target.closest('[data-consent]') : null;
      if (!btn) { return; }
      var choice = btn.getAttribute('data-consent');
      writeChoice(choice);
      applyChoice(choice);
      el.classList.remove('show');
      window.setTimeout(function () { el.remove(); }, 300);
    });
  }

  function init() {
    // GPC with no prior choice is already a decision — do not ask again.
    if (gpcActive() && !getChoice()) {
      writeChoice('denied');
      applyChoice('denied');
      return;
    }
    var choice = getChoice();
    if (choice === 'granted' || choice === 'denied') {
      applyChoice(choice);
    } else {
      showBanner();
    }
  }

  window.ysqResetConsent = function () {
    clearChoice();
    document.documentElement.removeAttribute('data-ads-consent');
    showBanner();
    return false;
  };
  window.ysqConsentChoice = getChoice;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
