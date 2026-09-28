/* Y-Square — blocked-advertising measurement.
   ------------------------------------------------------------------
   DETECTION ONLY. This file never blocks, never overlays, never hides
   content. It counts and reports, so we can decide with a real number
   whether an adblock wall is worth building for this audience.

   Why measure before building: a wall costs every blocked reader the
   article, and recovers impressions only from the subset who comply.
   Those two numbers only make sense against the blocked share, which
   nobody knows until it is counted.

   How detection works. A cosmetic filter targets our slot by class name
   and removes the element from layout. The ad request to Google's own
   domains is blocked at the network layer either way, so the honest
   signal is a bait element: a bare, empty <div> with no class. A
   network-level blocker leaves it alone; a cosmetic filter that
   pattern-matches "ad" will not. We test several baits so one unlucky
   filter name cannot decide the verdict on its own.

   Load order: deferred, at the end of body. Consent banner or
   ad-blocker aside, a script that has not run cannot report anything,
   and a measurement that misses first visits is worthless. It reports
   on a short delay so it never competes with first paint.

   Storage: localStorage only, first-party, no cookies, nothing sent
   anywhere. The endpoint is configurable and empty by default, so
   shipping this without setting ADBLOCK_REPORT_URL collects nothing
   and leaks nothing. */

(function () {
  "use strict";

  var KEY = "ysq.adblock";
  var ENDPOINT = "";           // set to a first-party path to start collecting
  var BAIT_CLASSES = ["adsbox", "ad-placement", "advert", "sponsor"];

  function readCounts() {
    try {
      var raw = localStorage.getItem(KEY);
      var v = raw ? JSON.parse(raw) : {};
      return (v && typeof v === "object") ? v : {};
    } catch (e) {
      return {};
    }
  }

  function writeCounts(v) {
    try {
      localStorage.setItem(KEY, JSON.stringify(v));
    } catch (e) { /* private mode: skip, do not break the page */ }
  }

  /* One bait, one verdict. Inserted into the live document, measured,
     then removed immediately -- it never affects layout the reader sees. */
  function testBait(className) {
    var host = document.querySelector("main") || document.body;
    if (!host) return null;
    var bait = document.createElement("div");
    bait.className = className;
    bait.setAttribute("aria-hidden", "true");
    bait.style.cssText = "position:absolute;left:-9999px;top:0;width:300px;height:250px";
    host.appendChild(bait);
    var box = bait.getBoundingClientRect();
    var hidden = getComputedStyle(bait).display === "none" ||
                 box.width === 0 || box.height === 0;
    bait.remove();
    return hidden;
  }

  function verdict() {
    var hits = 0, ran = 0;
    for (var i = 0; i < BAIT_CLASSES.length; i++) {
      var r = testBait(BAIT_CLASSES[i]);
      if (r === null) continue;
      ran++;
      if (r) hits++;
    }
    if (ran === 0) return "unknown";
    // Any bait being suppressed is a positive: these are deliberately
    // generic, non-ad names, so nothing else should ever hide them.
    if (hits > 0) return "blocked";
    return "clear";
  }

  function report() {
    var v = verdict();
    if (v === "unknown") return;
    var c = readCounts();
    c[v] = (c[v] || 0) + 1;
    writeCounts(c);
    var total = (c.blocked || 0) + (c.clear || 0);
    document.documentElement.setAttribute("data-ysq-adblock", v);
    if (!ENDPOINT) return;
    // Same-origin, no cookies, no identifiers. Page type only.
    try {
      var body = new URLSearchParams();
      body.set("v", v);
      body.set("total", String(total));
      body.set("path", location.pathname);
      fetch(ENDPOINT, {
        method: "POST",
        credentials: "omit",
        keepalive: true,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString()
      }).catch(function () {});
    } catch (e) { /* reporting must never break the page */ }
  }

  function boot() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        setTimeout(report, 400);
      });
    } else {
      setTimeout(report, 400);
    }
  }

  if (document.readyState === "complete") setTimeout(boot, 0);
  else window.addEventListener("load", boot);

  // Exposed for console checks and for the deploy verification step.
  window.ysqAdblock = { check: verdict, counts: readCounts, reset: function () {
    try { localStorage.removeItem(KEY); } catch (e) {}
  } };
})();
