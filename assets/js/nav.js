/* Y-Square — nav.js
   Mega-menu + mobile accordion behaviour.

   The header MARKUP is generated at build time from assets/data/geography.json
   (see gen_nav.py), so it is in the served HTML and readable by crawlers with
   no JavaScript. This file only adds interaction on top of it:

     - hover opens a panel; the pointer may travel down into the panel without
       it closing (the classic reason naive hover menus feel broken)
     - click toggles, so touch and keyboard work
     - Escape closes and returns focus to the trigger
     - Arrow keys move between top-level triggers
     - outside click closes
     - one panel open at a time

   Progressive enhancement: with JS off, every trigger is a real <a href> to
   the section landing page, and the panels are plain <div>s in the document
   flow. Nothing is hidden behind JS that is not also hidden from screen
   readers (visibility, not display:none, is what gates the open state).
*/
(function () {
  'use strict';
  var YSQ = window.YSQ = window.YSQ || {};
  var u = YSQ.utils = YSQ.utils || {};

  u.$ = u.$ || function (sel, ctx) { return (ctx || document).querySelector(sel); };

  // Local escaper. main.js owns an esc, but nav.js must not assume it: if
  // nav.js ever loads without main.js, calling u.esc() throws inside the
  // accordion build and silently kills the rest of init(), including the
  // burger handler. A throw in the middle of init is invisible until you
  // notice the mobile menu does nothing.
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  u.$$ = u.$$ || function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  var CLOSE_MS = 120;

  function init() {
    var nav = u.$('[data-nav]');
    if (!nav) return;
    if (nav.getAttribute('data-nav-ready')) return;
    nav.setAttribute('data-nav-ready', '1');

    var triggers = u.$$('.nav-trigger', nav);
    var panels = {};
    triggers.forEach(function (t) {
      var p = u.$('#' + t.getAttribute('aria-controls'));
      if (p) panels[t.getAttribute('aria-controls')] = { trigger: t, panel: p };
    });

    var openId = null;
    var closeTimer = null;

    function isOpen(id) { return openId === id; }

    function open(id, focusFirst) {
      if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
      Object.keys(panels).forEach(function (k) {
        var on = k === id;
        panels[k].panel.setAttribute('data-open', on ? 'true' : 'false');
        panels[k].trigger.setAttribute('aria-expanded', on ? 'true' : 'false');
      });
      openId = id;
      if (focusFirst) {
        var first = u.$('a, button', panels[id].panel);
        if (first) first.focus();
      }
    }

    function close(restoreFocus) {
      if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
      Object.keys(panels).forEach(function (k) {
        panels[k].panel.setAttribute('data-open', 'false');
        panels[k].trigger.setAttribute('aria-expanded', 'false');
      });
      var was = openId;
      openId = null;
      if (restoreFocus && was && panels[was]) panels[was].trigger.focus();
    }

    // Closing is deferred by a beat so the pointer can cross the gap between
    // the trigger and the panel without the panel vanishing underneath it.
    function scheduleClose() {
      if (closeTimer) clearTimeout(closeTimer);
      closeTimer = setTimeout(function () { close(false); }, CLOSE_MS);
    }

    function cancelClose() { if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; } }

    triggers.forEach(function (t) {
      var id = t.getAttribute('aria-controls');
      var p = panels[id] && panels[id].panel;
      if (!p) return;

      t.addEventListener('mouseenter', function () { open(id, false); });
      t.addEventListener('focus', function () { if (openId) open(id, false); });

      t.addEventListener('click', function (e) {
        // On desktop, the first click opens rather than navigating. Following
        // activation (Enter on an open trigger) still follows the link.
        if (isOpen(id)) { e.preventDefault(); close(false); }
        else { e.preventDefault(); open(id, false); }
      });

      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); open(id, true); }
        else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
          e.preventDefault();
          var i = triggers.indexOf(t);
          triggers[(i - 1 + triggers.length) % triggers.length].focus();
        } else if (e.key === 'ArrowRight') {
          e.preventDefault();
          var j = triggers.indexOf(t);
          triggers[(j + 1) % triggers.length].focus();
        } else if (e.key === 'Escape') { close(true); }
      });

      p.addEventListener('mouseenter', cancelClose);
      p.addEventListener('mouseleave', scheduleClose);
      p.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(true); });
    });

    nav.addEventListener('mouseleave', scheduleClose);
    nav.addEventListener('mouseenter', cancelClose);

    document.addEventListener('click', function (e) {
      if (openId && !nav.contains(e.target)) close(false);
    });

    nav.addEventListener('focusout', function (e) {
      if (openId && !nav.contains(e.relatedTarget)) close(false);
    });

    // Build the mobile accordion FROM the mega-panels.
    //
    // The region > subregion > country tree ships once, in the panels. Building
    // the accordion from that DOM avoids shipping a 46KB duplicate of it in
    // every page, and guarantees the two navigations can never disagree.
    u.$$('.mobile-menu[data-build="mega"]').forEach(function (mm) {
      var list = u.$('.acc-list-root', mm);
      if (!list) return;
      list.innerHTML = '';
      list.classList.remove('acc-fallback');

      function leaf(label, href) {
        var li = document.createElement('li');
        li.className = 'acc-leaf';
        var a = document.createElement('a');
        a.href = href; a.textContent = label;
        li.appendChild(a);
        return li;
      }

      function node(label, href, kids, id) {
        var li = document.createElement('li');
        li.className = 'acc-item';
        var btn = document.createElement('button');
        btn.className = 'acc-trigger';
        btn.setAttribute('aria-expanded', 'false');
        btn.setAttribute('aria-controls', id);
        btn.innerHTML = esc(label) +
          '<svg class="acc-caret" width="9" height="6" viewBox="0 0 9 6" aria-hidden="true">' +
          '<path d="M0 0l4.5 6L9 0z" fill="currentColor"/></svg>';
        var panel = document.createElement('div');
        panel.className = 'acc-panel';
        panel.id = id;
        panel.setAttribute('data-open', 'false');
        var ul = document.createElement('ul');
        ul.className = 'acc-list';
        kids.forEach(function (k) { ul.appendChild(k); });
        panel.appendChild(ul);
        li.appendChild(btn);
        li.appendChild(panel);
        return li;
      }

      var seq = 0;
      // One accordion root per top-level section, matching the desktop order.
      var roots = [];
      roots.push(leaf('Latest', '/latest/'));
      u.$$('.primary-nav .nav-item, .topic-nav .nav-item').forEach(function (item) {
        var trig = u.$('.nav-trigger', item);
        var panel = trig && u.$('#' + trig.getAttribute('aria-controls'));
        if (!trig || !panel) return;
        var kids = [];
        u.$$('.mega-group, .mega-cols-topic .mega-list', panel).forEach(function (grp) {
          if (grp.classList.contains('mega-cols-topic')) {
            u.$$('li', grp).forEach(function (li) {
              var a = u.$('a', li);
              if (a) kids.push(leaf(a.textContent.trim(), a.getAttribute('href')));
            });
            return;
          }
          var nameA = u.$('.mega-group-name', grp);
          var kids2 = [];
          u.$$('a', grp).forEach(function (a) {
            if (a === nameA) return;
            kids2.push(leaf(a.textContent.trim(), a.getAttribute('href')));
          });
          if (nameA) {
            kids.push(node(nameA.textContent.trim(),
                            nameA.getAttribute('href'),
                            kids2, 'acc-' + (seq++)));
          }
        });
        roots.push(node(trig.textContent.trim(), trig.getAttribute('href'),
                        kids, 'acc-' + (seq++)));
      });
      roots.forEach(function (n) { list.appendChild(n); });
    });

    // Mobile accordion: independent of the desktop mega-menu logic.
    u.$$('[data-accordion]').forEach(function (acc) {
      u.$$('.acc-trigger', acc).forEach(function (t) {
        var panel = u.$('#' + t.getAttribute('aria-controls'), acc);
        if (!panel) return;
        t.addEventListener('click', function (e) {
          e.preventDefault();
          var on = t.getAttribute('aria-expanded') === 'true';
          t.setAttribute('aria-expanded', on ? 'false' : 'true');
          panel.setAttribute('data-open', on ? 'false' : 'true');
        });
      });
    });

    // Mobile menu open/close
    var burger = u.$('[data-burger]');
    var mobile = u.$('.mobile-menu');   // NOT [data-mobile-menu]: the markup has no such attribute,
                                       // so the old selector silently matched nothing and the burger
                                       // never bound. It looked alive because the legacy
                                       // navigation.js still flips aria-expanded on the same button.
    if (burger && mobile) {
      burger.addEventListener('click', function () {
        var on = burger.getAttribute('aria-expanded') === 'true';
        burger.setAttribute('aria-expanded', on ? 'false' : 'true');
        mobile.setAttribute('data-open', on ? 'false' : 'true');
        mobile.setAttribute('aria-hidden', on ? 'true' : 'false');
        document.documentElement.setAttribute('data-menu-open', on ? '' : 'true');
      });
      mobile.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { burger.setAttribute('aria-expanded', 'false');
          mobile.setAttribute('data-open', 'false'); mobile.setAttribute('aria-hidden', 'true');
          document.documentElement.removeAttribute('data-menu-open'); burger.focus(); }
      });
      mobile.addEventListener('click', function (e) {
        if (!e.target.closest('a, button')) return;
      });
    }
  }

  /* Publish the header's real height as --header-h on :root.

     The sticky ad slot pins itself to this. The header is not one height --
     the region row wraps to a different number of lines at different widths,
     and a sweep found six distinct heights between 320px and 1440px -- so the
     only version of this number that cannot be wrong is the one measured from
     the rendered element. A hardcoded media-query value was wrong at four of
     those six widths, which left the ad floating below the nav, or hidden
     under it, in exactly the position an ad-blocked slot would occupy.

     Kept in the file that already owns the header, rather than in a second
     stylesheet that would have to be kept in sync by hand. */
  function publishHeaderHeight() {
    var h = document.querySelector('.site-header');
    if (!h) return;
    var px = Math.round(h.getBoundingClientRect().height);
    if (px > 0) document.documentElement.style.setProperty('--header-h', px + 'px');
  }

  function initHeaderHeight() {
    publishHeaderHeight();
    window.addEventListener('resize', publishHeaderHeight);
    window.addEventListener('orientationchange', publishHeaderHeight);
    // Web fonts land after first paint and change the masthead height, so
    // measure again once they have. Without this the offset is briefly wrong
    // on a slow connection, which is where a sticky ad visibly jumps.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(publishHeaderHeight)['catch'](function () {});
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initHeaderHeight);
  else initHeaderHeight();
}());
