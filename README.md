# Y-Square — y-squre.com

Static marketing site for **Y-Square**, an independent investment research and advisory practice.

## Stack

Static HTML + CSS + a few lines of vanilla JS. No framework, no build step, no Django, no
`node_modules`. Deploy target: **Render.com** (static site). Registrar: GoDaddy.

## Layout

```
index.html    single page: #home #about #services #approach #insights #contact
style.css     design system — navy #0b1f3a base, gold #d4a937 accent, serif body
ads.txt       Google AdSense DIRECT record
robots.txt    crawl policy
sitemap.xml   URL list
docs/         site brief, SEO map, brand voice, compliance notes
```

## Design tokens (do not drift)

| Token | Value | Use |
|---|---|---|
| `--navy` | `#0b1f3a` | header, footer, hero base |
| `--navy-2` | `#12294b` | hero gradient mid |
| `--gold` | `#d4a937` | accent, primary button |
| `--gold-soft` | `#e8c96a` | hover states, eyebrow text |
| `--paper` | `#f7f8fa` | alternate section background |
| `--ink` | `#1c2536` | body text |
| `--muted` | `#5b6779` | secondary text |
| `--line` | `#e3e7ee` | borders |
| `--radius` | `10px` | corners |

Body font: Georgia serif. UI/headings: Segoe UI stack.

## Invariants — breaking any of these is a bug

1. **Footer disclaimer stays.** SEBI / market-risk disclaimer is compliance-critical. Never delete
   or weaken it.
2. **AdSense client id stays** `ca-pub-9461123152614358` when editing `<head>`.
3. **Two spellings are both correct:** domain `y-squre.com`, brand `Y-Square`. Never normalise
   one to the other.
4. **Contact email:** `ffaayyaazz1993@gmail.com`, reply promise 2 business days.
5. **No new runtime dependencies.** If a feature seems to need one, it is mis-scoped.

## DNS (applied by a human in GoDaddy — agents do not log in)

| Action | Type | Host | Value | TTL |
|---|---|---|---|---|
| DELETE | A | @ | GoDaddy Website Builder A records | — |
| ADD | A | @ | `216.24.57.1` | 1 Hour |
| EDIT | CNAME | www | `<service>.onrender.com` | 1 Hour |
| DELETE | TXT | @ | stray `216.24.57.1` | — |

No nameserver change, no MX, no AAAA. SSL is automatic once Render verifies the domain.

## Team

| Worker | Profile | Owns |
|---|---|---|
| Content writer | `content-writer` | page copy, insights, long-form drafts |
| Web developer | `web-developer` | HTML/CSS/JS, SEO metadata, structure, deploy prep |
| Marketing analyst | `marketing-analyst` | segments, positioning, messaging, keyword map |
| Macro analyst | `macro-econ` | macro grounding, cycle state, fact-checking claims |

Work is dispatched through the YSQUAREENTERP kanban board.
