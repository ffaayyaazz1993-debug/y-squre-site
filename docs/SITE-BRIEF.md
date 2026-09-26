# Y-Square — Site Brief

Canonical for every worker. If a card contradicts this document, the card is wrong or the brief is
stale — comment on the card, don't silently improvise.

## Identity

- **Brand:** Y-Square
- **Domain:** y-squre.com (GoDaddy registrar, BigRock hosting + DNS)
- **Category:** independent investment research & advisory
- **Positioning line:** Investment research, grounded in macro reality.
- **Not:** a broker, a fund, a trading platform, a finfluencer, an SEBI-registered investment
  adviser. No custody of client money, no execution, no product sales.

## What we sell

| Service | Buyer question it answers | Deliverable shape |
|---|---|---|
| Macro Research | "What regime are we in?" | Rates, inflation, credit cycles, currency regimes, policy turns — with actionable summaries |
| Equity Research | "Is this business actually any good?" | Cash flows, moats, management quality, defensible valuation ranges |
| Portfolio Advisory | "How should I hold it?" | Asset allocation and construction vs horizon, liquidity, risk tolerance |
| Risk Management | "How do I not blow up?" | Scenario stress-testing, position sizing, drawdown discipline |

## Method (three steps, always stated the same way)

1. **Map the cycle** — where are we, and what is the market pricing? Primary data, not punditry.
2. **Build the thesis** — macro view → concrete thesis with explicit assumptions, catalysts, and
   falsification points.
3. **Size and manage risk** — every idea carries a position size, a stop-logic, a review trigger.
   We change our mind when the data changes, and we say so.

## Who we talk to

Primary guess (to be validated by `marketing-analyst` before it hardens into copy): investors and
allocators with real capital who have been burned by commentary-as-product. They already know
macro is the driver. They do not need macro explained — they need to know what it means for
positions they hold.

That assumption is provisional. Do not write copy that hard-codes it until the analyst has
delivered a segmentation.

## Proof posture (non-negotiable)

- Primary sources, always cited. FRED, NBER, central banks, BEA, BLS first.
- Scenario analysis over single-point forecasts.
- Position sizing and risk before return chasing.
- Plain language. No jargon as a substitute for thinking.
- Independent — no product placement, no issuer-favourable calls.

## Voice

Direct, sober, unsentimental. Writes like an analyst talking to another adult, not a brand
talking to a customer. Short sentences. Concrete nouns. Real numbers. No hype, no fear-mongering,
no "in today's fast-paced world", no em-dash-heavy AI cadence, no "unlock / leverage / seamless /
game-changing". If a claim cannot be sourced, it does not ship.

## Claims the site may not make

- guaranteed / risk-free / assured returns
- beat the market, outperform, alpha generation as a promise
- any implication of SEBI registration, fiduciary duty, or client-asset custody
- specific price targets on named listed securities
- unsourced market sizes, growth rates, survey statistics

## Banned words

unlock, leverage (as in "leverage our expertise"), seamless, game-changing, cutting-edge,
revolutionary, one-stop, world-class, bespoke solutions, in today's fast-paced, journey, elevate,
empower, passionate about, obsessed with, synergies, holistic, robust solution

## Current site state

Single page, six anchor sections, all copy drafted. It is a positioning page, not a content
machine. Known gaps:

- `#insights` holds three "in preparation" placeholder cards — no real content
- No `robots.txt`, no `sitemap.xml`
- No JSON-LD structured data (Organization, ProfessionalService, FAQPage candidates)
- No OG/Twitter card images
- No legal pages: privacy policy, terms, disclaimer page (footer has an inline disclaimer only)
- No contact form — email only
- No analytics beyond AdSense
- Site **is deployed and live** on BigRock (`66.116.229.73`, docroot `/home2/a1790256/public_html`,
  Apache, Let's Encrypt wildcard TLS). DNS resolved 23 Sep 2026. Nothing outstanding on hosting.
- `ads.txt` is **AdSense-authorized**. The `google-adsense-account` meta tag and the loader script
  are both live in `<head>`. Remaining AdSense work is Google's own review queue.
- `robots.txt` and `sitemap.xml` are live at the domain root.

## Order of work (proposed)

1. `marketing-analyst`: segmentation + positioning + keyword map.
2. `content-writer`: insights section real content, seeded by macro-econ cycle state.
3. `web-developer`: multi-page split, JSON-LD, OG tags, legal pages.
4. Contact form + privacy policy (required before AdSense approval for lead-gen).
5. Iterate on SEO metadata from the keyword map.

Deploy is done — do not plan, brief, or block on hosting work.

## Compliance note

Y-Square is **not SEBI-registered**. The footer disclaimer is a real constraint on what the site
can promise, not boilerplate. Any new copy that strains against it is a defect. The market-risk
and no-advice language must survive every edit.
