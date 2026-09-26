/* Y-Square — cookie consent banner
 *
 * Purpose: record an explicit accept/decline choice before personalised
 * advertising cookies are used, and let the visitor change it later.
 *
 * How it works:
 *   - Choice stored in localStorage under 'ysq_consent'. Absent = undecided.
 *   - Banner injected once, hidden by default, shown only when undecided.
 *   - Accept  -> 'granted', and data-ads-consent="granted" on <html>.
 *   - Decline -> 'denied',  and data-ads-consent="denied"  on <html>.
 *   - The AdSense loader is never blocked. Declining does not remove ads; it
 *     records the choice. Which ads actually serve is governed by Google's own
 *     EU consent message (Privacy & Messaging in the AdSense console) — see the
 *     note above applyChoice() for why we do not fake an npa signal here.
 *
 * The footer "Cookie choices" link calls window.ysqResetConsent(), which clears
 * the stored value and re-opens the banner.
 *
 * No dependencies. Kept in its own file so the markup exists in exactly one
 * place and both pages stay in sync.
 */
(function () {
  'use strict';

  var KEY = 'ysq_consent';
  var MAX_AGE_DAYS = 180;

  function readChoice() {
    try {
      return window.localStorage.getItem(KEY);
    } catch (e) {
      // Storage blocked (private mode / strict privacy settings). Treat as
      // undecided and fall back to session-only so the visitor can still choose
      // without us persisting anything.
      return null;
    }
  }

  function writeChoice(value) {
    try {
      window.localStorage.setItem(KEY, value);
    } catch (e) {
      window.__ysqConsent = value; // in-memory only
    }
  }

  function clearChoice() {
    try {
      window.localStorage.removeItem(KEY);
    } catch (e) { /* nothing to clear */ }
  }

  function getChoice() {
    return readChoice() || window.__ysqConsent || null;
  }

  function buildBanner() {
    var el = document.createElement('div');
    el.className = 'consent-banner';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-live', 'polite');
    el.setAttribute('aria-label', 'Cookie consent');
    el.innerHTML =
      '<div class="consent-inner">' +
        '<p class="consent-text">' +
          'This site uses cookies. Google AdSense sets cookies to serve advertising, and with ' +
          'your permission, to tailor it to you. See our ' +
          '<a href="/privacy.html">Privacy Policy</a> for what we do and do not collect.' +
        '</p>' +
        '<div class="consent-actions">' +
          '<button type="button" class="btn-consent-accept" data-consent="granted">Accept</button>' +
          '<button type="button" class="btn-consent-decline" data-consent="denied">Decline</button>' +
        '</div>' +
      '</div>';
    return el;
  }

  function showBanner() {
    if (document.querySelector('.consent-banner')) { return; }
    var el = buildBanner();
    document.body.appendChild(el);
    // Next frame, so the transition has a starting state to animate from.
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

  /* Record the decline so page scripts and styles can react to it.
   *
   * We deliberately do NOT touch the adsbygoogle queue here. The loader is in
   * <head> and may not have run yet; pushing a hand-rolled object into it
   * produces an ad error rather than a non-personalised ad. Google supplies
   * genuine non-personalised ads via its own EU consent message (Privacy &
   * Messaging in the AdSense console), not via a client-side push.
   *
   * So declining here means: we remember the choice, and Google's own consent
   * handling is what governs which ads actually serve.
   */
  function applyChoice(choice) {
    if (choice === 'denied') {
      document.documentElement.setAttribute('data-ads-consent', 'denied');
    } else if (choice === 'granted') {
      document.documentElement.setAttribute('data-ads-consent', 'granted');
    }
  }

  function init() {
    var choice = getChoice();
    if (choice === 'granted' || choice === 'denied') {
      applyChoice(choice);   // returning visitor: no banner, honour the choice
    } else {
      showBanner();
    }
  }

  /* Footer link: forget the choice and ask again. */
  window.ysqResetConsent = function () {
    clearChoice();
    try { delete window.__ysqConsent; } catch (e) { /* noop */ }
    document.documentElement.removeAttribute('data-ads-consent');
    showBanner();
  };

  window.ysqConsentChoice = getChoice;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
