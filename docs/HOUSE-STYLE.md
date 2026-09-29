# Y-Squre house style — working document

Internal. Not for publication. For content-writer, content-reviewer, web-developer.

Canonical sources, in priority order:
1. `docs/SITE-BRIEF.md` — voice, proof posture, banned words, prohibited claims.
2. The shipped copy itself — `/about/`, `/editorial-policy/`, `/blog/2026/09/26/*.html`,
   `/disclaimer/`. When a rule and the shipped pages disagree, the brief wins; comment,
   do not quietly follow the page.

---

## 1. The voice, in five lines

- Sober, not cold. Plain words, short sentences, concrete nouns.
- The reader is an adult with a position. Never perform enthusiasm.
- State the number, then the source, in the same sentence.
- Say what would prove you wrong. This is not optional garnish; it is the product.
- No throat-clearing. First sentence is the finding.

## 2. Annotated examples

These are drawn from the shipped site, not from a hypothetical. They are the standard.

### 2.1 GOOD — attribution in the sentence itself

> "We do not present opinion as reporting, and we do not present a source's claim as our own
> verification. Where we report what another outlet or an official body said, we say so in
> the sentence."

Why it works: it states a rule and then demonstrates it in the same breath. No hedging
adverb, no "we believe". The prohibition is concrete enough to be auditable.

### 2.2 GOOD — a refusal written as a fact about the practice

> "We do not manage money, sell products, or accept a commission for a view."

Why it works: three concrete negations, each naming a specific thing a reader might otherwise
assume. It is checkable. Nothing here is a slogan.

### 2.3 BAD — the banned-words fingerprint

> "In today's fast-paced and volatile environment, we leverage our cutting-edge expertise to
> empower investors with a bespoke, holistic and seamless approach that unlocks your financial
> potential."

Every clause is a defect:

| phrase | why it fails |
|---|---|
| "In today's fast-paced" | throat-clearing; zero information |
| "volatile environment" | unstated, unsourced, and true of every day since 2008 |
| "leverage our expertise" | banned word; also "leverage" used in the financial sense on a research site is a category error |
| "cutting-edge" | banned; meaningless |
| "empower" | banned; also implies the reader lacks agency |
| "bespoke, holistic, seamless" | three banned words, each substituting a mood for a description |
| "unlock your financial potential" | implied guaranteed outcome; a prohibited claim, not just a style problem |

This is the sentence the whole banned list exists to catch. If a paragraph reads like the
table above, it is not finished.

### 2.4 BAD — a number with no source

> "Global markets have seen significant volatility, with the S&P 500 up 24% over the past
> eighteen months, and investors are increasingly seeking diversification."

The 24% is real and checkable. As written it is unsourced, so it is a defect. The fix is not
to soften the number; it is to attach it:

> "The S&P 500 rose 24% over the eighteen months to 30 June 2026 (S&P Dow Jones Indices,
> total price return)."

If you cannot attach the source, cut the sentence. Do not keep the number and hedge it.

### 2.5 BAD — a forecast wearing a finding's clothes

> "The Fed will cut rates in the second quarter, bringing the policy rate to 3.25%."

The site does not publish point forecasts on named instruments. Convert it to a conditional
with its own falsification point:

> "A first cut becomes consistent with the current inflation path only if the core series
> prints below [value] for two consecutive months. Below that, the easing case holds; above
> it, the hold case does. We will publish the reading either way."

## 3. Banned-words checklist — run this before handoff

Mechanical. Grep the draft for each term. Zero hits required, case-insensitive.

- [ ] unlock
- [ ] leverage (except where the noun is literal debt/financial leverage, in which case
      name the instrument)
- [ ] seamless
- [ ] game-changing
- [ ] cutting-edge
- [ ] revolutionary
- [ ] one-stop
- [ ] world-class
- [ ] bespoke solutions
- [ ] in today's fast-paced
- [ ] journey
- [ ] elevate
- [ ] empower
- [ ] passionate about
- [ ] obsessed with
- [ ] synergies
- [ ] holistic
- [ ] robust solution

Second pass, same standard — these are the usual hiding places:

- [ ] delve, tapestry, testament to, navigate the landscape, at the forefront of,
      ever-evolving, exciting times, unlock the potential, wealth creation, financial
      freedom, your financial future, take control of, put you first, one-on-one,
      bespoke, turnkey, end-to-end, holistic approach, peace of mind

## 4. Prohibited claims — not style, compliance

The site is not SEBI-registered. Any of these is a ship-blocker regardless of how well the
prose reads.

- [ ] no guaranteed, assured, protected or risk-free outcomes
- [ ] no "beat the market", "outperform", "alpha" as a promise
- [ ] no implication of SEBI registration, fiduciary duty, or custody of client assets
- [ ] no specific price target on a named listed security
- [ ] no unsourced market size, growth rate, or survey statistic
- [ ] no CTA phrased as a funnel promise (no signup pitch; the only contact is the email
      address in the footer)

## 5. Structural requirements for a research note

- [ ] leads with the finding, not the approach
- [ ] every number carries a series ID, publisher, or dated source
- [ ] contains an explicit falsification point — the observation that would prove the read wrong
- [ ] states where the data is thin, stale, or contradictory
- [ ] ends on a conclusion, a monitoring trigger, or a question worth watching
- [ ] carries one of the four site labels: News, Analysis, Explainer, Research Note

## 6. Word-count discipline

Report the count against target in the handoff. Do not pad to hit a floor — a short note that
says everything it needs to is the better artefact. If a section will not reach its target
without filler, cut the section and say so in the handoff.
