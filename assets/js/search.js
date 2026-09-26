/* Y-Square — search.js
   Static-hosting search over headline, category, summary and tags.
   No database, no server round-trip.

   To move server-side later, replace loadIndex()/runQuery() with a fetch to
   an API returning the same article shape. The render + ranking code is
   unchanged. */
(function () {
  'use strict';
  var YSQ = window.YSQ || {};
  var u = (YSQ.utils = YSQ.utils || {});

  var index = null;
  var resultsEl, queryEl, countEl;

  function loadIndex() {
    if (index) return Promise.resolve(index);
    // The index ships as a JS file, so it loads without a network round-trip
    // that a same-origin fetch of JSON would need.
    return new Promise(function (resolve) {
      if (window.YSQ_ARTICLES) { index = window.YSQ_ARTICLES; return resolve(index); }
      var s = document.createElement('script');
      s.src = '/assets/js/articles.js?v=' + (YSQ.config ? YSQ.config.searchIndexVersion : '1');
      s.onload = function () { index = window.YSQ_ARTICLES || { articles: [] }; resolve(index); };
      s.onerror = function () { index = { articles: [] }; resolve(index); };
      document.head.appendChild(s);
    });
  }

  /* Weighted scoring. A title hit outranks a body hit; an exact title
   * substring outranks a scattered word match. */
  function score(article, terms) {
    var title = (article.title || '').toLowerCase();
    var summary = (article.summary || '').toLowerCase();
    var topics = (article.topics || []).join(' ').toLowerCase();
    var section = (article.sectionLabel || '').toLowerCase();
    var region = (article.region || '').toLowerCase();
    var type = (article.typeLabel || '').toLowerCase();
    var total = 0;

    for (var i = 0; i < terms.length; i++) {
      var t = terms[i], hit = 0;
      if (title.indexOf(t) >= 0) { hit += title.indexOf(t) === 0 ? 14 : 10; }
      if (topics.indexOf(t) >= 0) hit += 6;
      if (section.indexOf(t) >= 0) hit += 5;
      if (type.indexOf(t) >= 0) hit += 4;
      if (summary.indexOf(t) >= 0) hit += 3;
      if (region.indexOf(t) >= 0) hit += 2;
      if (!hit) return -1;           // every term must match somewhere (AND)
      total += hit;
    }
    return total;
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function render(list, q) {
    if (!resultsEl) return;
    if (!q) { resultsEl.innerHTML = ''; resultsEl.setAttribute('hidden', ''); return; }

    if (!list.length) {
      resultsEl.removeAttribute('hidden');
      resultsEl.innerHTML = '<div class="empty-state"><strong>No matches for &ldquo;' +
        esc(q) + '&rdquo;</strong>The index covers published articles only. ' +
        'Try a broader term, or browse the sections from the navigation above.</div>';
      if (countEl) countEl.textContent = '';
      return;
    }

    var html = list.map(function (a) {
      var stamp = a.published ? u.stamp(a.published) : '';
      return '<article class="index-row">' +
        '<div class="index-when">' + (a.typeLabel || 'Article') + '</div>' +
        '<div><h3><a href="' + esc(a.url) + '">' + esc(a.title) + '</a></h3>' +
        '<p>' + esc(a.summary || '') + '</p>' +
        '<span class="meta">' + esc(a.sectionLabel || '') +
        (stamp ? '<span class="meta-sep">/</span>' + esc(stamp) : '') +
        (a.readingTime ? '<span class="meta-sep">/</span>' + esc(a.readingTime) : '') +
        '</span></div></article>';
    }).join('');

    resultsEl.removeAttribute('hidden');
    resultsEl.innerHTML = '<div class="index-list">' + html + '</div>';
    if (countEl) {
      countEl.textContent = list.length + (list.length === 1 ? ' result' : ' results');
    }
  }

  function runQuery(q) {
    var terms = String(q || '').toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) { render([], ''); return; }
    loadIndex().then(function (ix) {
      var hits = (ix.articles || []).map(function (a) {
        return { a: a, s: score(a, terms) };
      }).filter(function (h) { return h.s >= 0; });
      hits.sort(function (x, y) { return y.s - x.s; });
      render(hits.map(function (h) { return h.a; }), q);
    });
  }

  function init() {
    resultsEl = u.$('#search-results');
    queryEl = u.$('#search-query');
    countEl = u.$('#search-count');
    if (!resultsEl || !queryEl) return;

    var form = u.$('#search-form');
    u.on(form, 'submit', function (e) {
      e.preventDefault();
      runQuery(queryEl.value);
    });

    u.on(queryEl, 'input', u.debounce(function () { runQuery(queryEl.value); }, 180));

    // Deep link: /?q=term
    var m = /[?&]q=([^&]+)/.exec(window.location.search);
    if (m) {
      queryEl.value = decodeURIComponent(m[1].replace(/\+/g, ' '));
      runQuery(queryEl.value);
    }
  }

  YSQ.search = { run: runQuery, loadIndex: loadIndex };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
