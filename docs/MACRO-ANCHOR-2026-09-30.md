# MACRO ANCHOR — 30 September 2026

**For:** Y-Square first Insights entry. Factual spine. Not copy.
**Prepared by:** macro-econ profile. FRED data pulled live 30 Sep 2026, 11:38–11:52 IST.
**Cycle detector:** v3 refined (`econ_detector_fallback.py`), run 30 Sep 2026 on a fully refreshed
44-series cache. Raw output in Appendix A.

Every number carries a FRED series ID or a dated primary-source citation. Where the data is thin or
the methods disagree, it says so.

---

## 1. Cycle state, right now

**The US is in a late expansion with a tightening policy stance and an unresolved inflation
problem. The v3 detector classifies it as `Recovery / Improving`, and that label is the weakest
of the outputs it produced — the honest read is narrower than the label.**

Detector output, unedited:

| Field | Value |
|---|---|
| Cycle state | Recovery |
| Cycle direction | Improving |
| Composite score | +0.60 / 100 |
| 3-month momentum | +14.00 |
| 6-month momentum | +9.84 |
| Recession probability | 2.3% (probit: 0.029) |
| Ensemble score | +49.68 / 100 |
| Ensemble regime | Expansion |
| Model disagreement | 96.0 — MODERATE, methods diverge |
| Breadth | 28 of 44 indicators rising (63.6%) |
| Markov P(Expansion) | 0.983 |
| Spectral cycle phase | contraction, z = +0.090 |
| Indicators scored | 44 / 44 |

### Why the label is weaker than it sounds

The detector's own disagreement index is 96.0 on a 100 scale, and the components do not agree:

| Method | Score |
|---|---|
| Markov regime component | +96.64 |
| Probit component | +94.30 |
| Diffusion / breadth | +27.20 |
| **Composite** | **+0.60** |
| Spectral cycle-phase component | **−5.00** |

Two models say strongly expansion, two say flat-to-negative. The composite of +0.60 is
effectively zero — the middle of the detector's own range. The spectral method, which reads the
cycle's level rather than its regime, puts the economy in a **contraction** phase with a z-score of
+0.090.

So the regime classification is `Expansion` and recession probability is low, while the *level* of
the cycle reads flat. Different statements; both are in the output.

### Category scores

| Category | Score | |
|---|---|---|
| Business | +44.30 | strongest |
| Financial | +26.12 | |
| Credit | +11.76 | |
| Labor | +8.45 | |
| Growth | +3.28 | flat |
| Fiscal | −2.22 | |
| Housing | −4.41 | |
| Consumers | −21.79 | |
| Inflation | −22.30 | |
| External | −24.42 | |
| **Monetary** | **−36.00** | weakest |

The weakest category is Monetary — which is consistent with a central bank that has just raised
rates.

### The indicators doing the work

| Indicator | Series | Value | As of |
|---|---|---|---|
| Real GDP (SAAR) | GDPC1 | 24,269.6, +1.48% q/q | 2026 Q2 |
| Real GDP prior qtr | GDPC1 | +2.09% q/q | 2026 Q1 |
| Gross domestic income | GDI | 32,245.1 | 2026 Q2 |
| Industrial production | INDPRO | 103.07, +1.4% y/y | Aug 2026 |
| Nonfarm payrolls | PAYEMS | 159,075k, **+162k m/m** | Aug 2026 |
| Payroll 3-mo avg | PAYEMS | +71k | Jun–Aug 2026 |
| Payroll 12-mo avg | PAYEMS | +50k | Sep 2025–Aug 2026 |
| Unemployment rate | UNRATE | 4.1% (unchanged) | Aug 2026 |
| Labour participation | CIVPART | 61.6% | Aug 2026 |
| Job openings | JTSJOL | 7,079k | Aug 2026 |
| Initial claims (4-wk avg, weekly) | ICSA | ~197–198k | w/e 19 Sep 2026 |
| Core CPI y/y | CPILFESL | **+2.45%** | Aug 2026 |
| Headline CPI y/y | CPIAUCSL | **+3.35%** | Aug 2026 |
| Headline PCE y/y | PCEPI | **+3.70%** | Jul 2026 |
| Core PCE y/y | PCEPILFE | **+3.34%** | Jul 2026 |
| Core PCE 3-mo annualised | PCEPILFE | +3.05% | Jul 2026 |
| Effective fed funds (monthly avg) | FEDFUNDS | 3.63% | Aug 2026 |
| Effective fed funds (daily) | DFF | **3.88%** | 28 Sep 2026 |
| 10-yr Treasury | DGS10 | **5.24%** | 28 Sep 2026 |
| 2-yr Treasury | DGS2 | **4.92%** | 28 Sep 2026 |
| 10s2s curve | T10Y2Y | +0.37pp | 29 Sep 2026 |
| 30-yr mortgage | MORTGAGE30US | 7.03% | 24 Sep 2026 |
| Baa–10yr spread | BAA10Y | 1.46pp | 28 Sep 2026 |
| HY OAS | BAMLH0A0HYM2 | **3.02pp** | 28 Sep 2026 |
| Financial conditions index | NFCI | −0.555 | 18 Sep 2026 |
| Housing starts | HOUST | 1,275k units, −1.2% y/y | Aug 2026 |
| Building permits | PERMIT | 1,403k | Aug 2026 |
| Existing home sales | HSN1F | 684k | Aug 2026 |
| New home sales | HSN1F | MSACSR 8.5 → HSN1F 684k | Aug 2026 |
| Consumer sentiment | UMCSENT | 51.7 | Aug 2026 |
| Personal saving rate | PSAVERT | 3.0% | Jul 2026 |
| Retail sales | RETAILSMNSA | 677,249 | Jul 2026 |
| Revolving credit / borrowers | BUSLOANS | 2,945.1bn | Aug 2026 |
| S&P 500 | SP500 | 7,670.84 (−1.64% from 13 Aug high) | 29 Sep 2026 |
| VIX | VIXCLS | 16.07 | 28 Sep 2026 |
| WTI crude | DCOILWTICO | **$96.41, +53.1% y/y** | 22 Sep 2026 |
| Broad dollar | DTWEXBGS | 120.33 | 25 Sep 2026 |
| Federal debt | GFDEBTN | $39.07tn | 2026 Q1 |
| Debt/GDP | derived | **161.6%** | 2026 Q1 |

### Staleness — exact, not hand-waved

Cache refreshed live at 11:41 IST on 30 Sep 2026. All 44 series returned, 0 failures, 7 series
advanced since the previous pull. Observed-lag by publication cycle, which is normal and not a
defect:

| Lag class | Series | Reason |
|---|---|---|
| **1 quarter behind** | GDPC1, GDI, CP, COMPRNFB, W068RCQ027SBEA | Quarterly GDP; Q3 not released until late Oct |
| **2 quarters for debt** | GFDEBTN | Q1 2026 is the latest published |
| **1 month behind** | All monthly series through Aug 2026 | Sep CPI/payrolls release Oct |
| **1 month behind** | PCEPI, PCEPILFE, RETAILSMNSA, PSAVERT | BEA monthly, July is latest |
| **2–8 days** | Weekly/daily market series | Normal |

**Two genuine caveats, flagged rather than hidden:**

1. **The detector's policy-rate input is one hike stale.** FEDFUNDS last prints August at 3.63%. On
   16 September 2026 the FOMC **raised** the target range 25bp to 3.75–4.00% on a 12–0 vote
   (Federal Reserve, FOMC statement, 16 Sep 2026); the daily effective rate (DFF) is 3.88% as of
   28 Sep. The detector scored Monetary at −36.00 on the pre-hike monthly average. **A hike pushes
   that score more negative, not less** — the weakest of eleven categories is stale in the
   direction that flatters it.

2. **The real-consumer-spending series is unusable this quarter.** W068RCQ027SBEA prints +7.21% q/q
   in 2026 Q1 and −4.03% in Q2, against a normal range of roughly +0.4% to +3.0%. A swing that size
   in a chained-dollar series is a chain-weighting or revision artefact, not behaviour.
   **Do not cite it.** Nominal PCE (+$36.2bn m/m in July) is the usable read.

---

## 2. The three forces that matter most

### Force 1 — Monetary policy has turned restrictive again, and it is the only major force moving against growth

The FOMC raised the target range to 3.75–4.00% on 16 September 2026, stating "Inflation remains
elevated. Today's policy action will support a timelier return to the Committee's 2 percent goal"
(Federal Reserve, FOMC statement, 16 Sep 2026). The 10-year Treasury is 5.24%, the 30-year
mortgage 7.03% (DGS10, 28 Sep; MORTGAGE30US, 24 Sep). The 10s2s curve is positive at +0.37pp
(T10Y2Y, 29 Sep) — no longer inverted, but it has a poor hit rate as a recession signal and should
not be cited as one on its own.

With core PCE at 3.34% and headline CPI at 3.35%, the policy rate is roughly **+0.5pp above** core
inflation — a genuinely positive real policy rate.

*Portfolio implication:* duration is being repriced against the holder, not for them. The bond
market is not offering the usual recession hedge; any thesis leaning on Treasuries to cushion a
drawdown must clear that hurdle.

*What would falsify this read:* core PCE below 2.5% y/y for two consecutive months, or a subsequent
FOMC statement dropping the "inflation remains elevated" language — either would mean the Committee
sees disinflation the market has not. A second hike would confirm it instead, with the 10-year above
5.5% and the curve bear-flattening.

### Force 2 — The labour market is cooling slowly and quietly, without breaking

Payroll gains collapsed from +214k (March) to +31k (June) and +21k (July) before a +162k August
rebound: a 3-month average of +71k against a 12-month average of +50k (PAYEMS). Unemployment has
been flat at 4.1% for two months. Job openings fell from 7,240k in January to 7,079k in August
(JTSJOL). Initial claims sit near 197–198k (ICSA, w/e 19 Sep). Average hourly earnings of all
private employees are $41.70, +1.71% y/y (AWHMAN, Aug 2026).

The +162k August print is real and came with +55k of upward revisions to June and July (BLS,
Employment Situation, released 4 Sep 2026, USDL-26-1435). But one strong month against a 12-month
average of +50k is not a trend reversal. **This is a labour market no longer adding workers at
speed, not one shedding them.**

*Portfolio implication:* the classic late-cycle signal — low hiring, low firing. That combination
historically precedes a slowdown by several quarters, and is why the composite sits near zero
despite the regime model calling expansion.

*What would falsify this read:* two consecutive payroll prints below zero with a negative 3-month
average, or unemployment rising through 4.5%. Either converts "slow cooling" into "contraction" and
invalidates the 2.3% probability. Conversely, three consecutive months
above +150k would mean the slowdown thesis is wrong and the August print was the start of something.

### Force 3 — An energy shock is running straight into an inflation problem the Fed has just decided to fight

WTI crude averaged $96.41 on 22 September 2026, **+53.1% y/y** against $62.99 a year earlier
(DCOILWTICO), having traded as high as $107.02 in the preceding fortnight. Headline CPI at 3.35% and
headline PCE at 3.70% run roughly 90bp above their core counterparts — an energy pass-through
signature.

Reporting attributes the move to Middle East supply disruption and a stalemate in US-Iran talks,
with Strait of Hormuz transit in question (*The National*, 28 Sep 2026; *Daily Post*, 29 Sep 2026,
citing a Monday spike to $107 on a rejected truce proposal). **Treat the causal attribution as
secondary reporting, not established fact** — the price series is primary and citable; the
geopolitical cause is not. The Chair's September press conference indicated most advanced
economies face price pressures and that their central banks "are making their own judgments"
(*Federal Reserve*, transcript, 16 Sep 2026). This is not a US-only problem.

*Portfolio implication:* the one force where policy, inflation, and growth all push the same way —
toward a worse mix. An energy shock holding headline inflation above 3% forces the Fed to stay tight
into a slowing labour market, the combination that historically produces the worst outcomes.

*What would falsify this read:* WTI sustained below $70 removes the headline impulse within two
quarters. Core PCE continuing to decelerate (3.05% three-month annualised in July, down from 3.46%
six-month) would show pass-through is not broadening into the core. A US-Iran settlement would do
the same faster.

---

## 3. The honest caveat

**Thin, stale, or contradictory:**

- **Methods disagree by 96 points.** Markov (+96.64) and probit (+94.30) say strong expansion;
  spectral (−5.00) says contraction; composite is +0.60. The `Recovery` label is the ensemble's
  verdict. Do not present it as unanimity.
- **Breadth is 63.6%, not overwhelming.** Sixteen of 44 indicators are falling.
- **The policy-rate input is stale in a flattering direction** (covered above) — the single most
  important caveat here.
- **Two cached series are unusable this cycle.** W068RCQ027SBEA (real PCE swings +7.21% then
  −4.03% q/q against a +0.4% to +3.0% norm — a chain-weight artefact). RETAILSMNSA (February 2026
  prints $564.7bn against $657.6bn in March; not credible, likely seasonal factors). Cite retail
  sales from the Census release, not this cache.
- **Headline CPI's short-run measure is unusable this quarter.** It rose 3.35% y/y while the last
  three months annualise to ~0.2%, because June printed −0.42% m/m. **Use the y/y.**
- **Debt is two quarters stale** (GFDEBTN 2026 Q1, subject to revision).
- **No primary source confirms the global picture.** Global manufacturing PMI 52.3, euro area
  composite 53.1, China official manufacturing PMI 50.1 (September) are S&P Global / NBS / Reuters
  survey and secondary reporting — **not FRED-citable**. Flag as secondary if used.
- **Chain-weighting:** any chained-dollar q/q figure here (GDP, real PCE) is revisable and not
  additive across quarters.

**Where I am extrapolating:**

- That the energy shock and the Fed's tightening will collide is a *mechanism* argument, not a
  forecast. It carries no probability and should not be given one.
- Linking labour-market cooling to the September pivot is my inference. The FOMC statement cites
  inflation, not labour-market weakness.
- The GDP path (+0.48% Q4 2025, +2.09% Q1 2026, +1.48% Q2 2026) is decelerating but positive.

**What I could not verify:**

- Whether September CPI or payroll prints are scheduled or delayed (BLS calendar not checked).
- The current SAHM rule reading — the 0.47% figure in secondary sources is dated April/May 2026 and
  I could not confirm it against a primary computation. **Do not cite it.**
- Any pending NBER announcement. The citable fact: last peak February 2020, last trough April 2020,
  no 2026 recession declared.

---

## 4. What is NOT to say

Each of these is tempting right now and unsupported by the data above.

1. **"The economy is in recovery."** The detector says `Recovery`, but its spectral component says
   contraction and its composite is +0.60. Say: regime models classify this as expansion while the
   cycle's level reads flat, with the methods disagreeing by 96 points.
2. **"Recession risk is low."** 2.3% is the probit model's output on a trained fit, not an observed
   fact, and it predates the September hike. Do not turn a model probability into reassurance.
3. **"The Fed is expected to..."** No unattributed forward guidance. The citable fact is what the
   Committee did on 16 September: rates raised to 3.75–4.00%, inflation described as elevated,
   unanimous 12–0 vote.
4. **"Inflation is heading back to target."** Core PCE is 3.34% y/y against a 2% target, at or
   above 3.05% three-month annualised. It is above target, not returning.
5. **"This is a soft landing."** A landing requires a descent. GDP is positive and decelerating;
   inflation is above target and the policy rate has just risen. Neither half is supported.
6. **"Housing is recovering."** Starts are 1,275k, down 1.2% y/y, permits 1,403k. Existing home
   sales rose to 684k from 643k — one month in a weak series, and Housing is the second-weakest
   category.
7. **"Consumer confidence is recovering."** UMCSENT printed 51.7 in August against 55.2 in July and
   56.6 in February. Volatile series, and it is down.
8. **"The S&P 500 is near its highs, so the economy is fine."** It is 1.64% below its 13 August
   high. Equity prices are not an economic indicator, and the site's method forbids the proxy.
9. **Any claim that credit is tight.** HY OAS at 3.02pp is around the 49th percentile of its own
   ten-year range — mid-range, not stressed. It has widened 42bp in a month: a direction, not yet a
   level. NFCI at −0.555 means conditions looser than average, not tighter.
10. **"Global growth is strengthening."** The PMI data supports a claim that global manufacturing
    momentum improved. It does not support a quantified growth forecast, and it is survey-based,
    not official statistics.
11. **Any price target, sector call, or outperformance claim on a named security.** Prohibited by
    the site brief.
12. **"Debt at 161.6% of GDP is unsustainable."** The ratio is a fact and is rising — up 1.5pp in a
    quarter, 4.9pp in a year. Sustainability is a judgment. State the number and direction, leave
    the verdict out.

---

## Appendix A — Raw detector output (auditable)

Run 30 Sep 2026, cache refreshed live immediately prior. Command:

```
cd C:/Users/ffaay/econ-cycle-detector
uv run --no-project --with numpy --with pandas --with scipy --with requests \
  python econ_detector_fallback.py
```

```
============================================================================
ECONOMIC CYCLE REGIME DETECTION REPORT — REFINED v3
============================================================================
Country/Region:       US
Analysis Date:        2026-09-30
Indicators scored:    44/44

CYCLE STATE:          Recovery
CYCLE DIRECTION:      Improving
COMPOSITE SCORE:      +0.60 / 100
3M MOMENTUM:          +14.00
6M MOMENTUM:          +9.84
RECESSION PROBABILITY: 2.3%
MODEL DISAGREEMENT:   MODERATE — methods diverge

CATEGORY SCORES
--------------------------------------------
  Business       :  +44.30 +████████
  Monetary       :  -36.00 -███████
  Financial      :  +26.12 +█████
  External       :  -24.42 -████
  Inflation      :  -22.30 -████
  Consumers      :  -21.79 -████
  Credit         :  +11.76 +██
  Labor          :   +8.45 +█
  Housing        :   -4.41 -
  Growth         :   +3.28 +
  Fiscal         :   -2.22 -

METHOD BREAKDOWN
--------------------------------------------
  Composite score:       +0.60
  Diffusion/breadth:    +27.20
  Markov component:     +96.64
  Probit component:     +94.30
  Cycle-phase component:  -5.00
  Method disagreement: 96.0 — MODERATE — methods diverge

DIFFUSION / BREADTH
--------------------------------------------
  Rising:   28 / 44 (63.6%)
  Falling:  16 / 44

MARKOV REGIME SWITCHING
--------------------------------------------
  P(Expansion): 0.983
  P(Recession): 0.017
  Expected duration: (21.5, 56.8)

RECESSION PROBABILITY MODEL
--------------------------------------------
  P(Recession): 0.029
  Status:       OK: trained on 363 months using 11 category factors

SPECTRAL CYCLE
--------------------------------------------
  Cycle phase:  contraction
  Cycle z-score: +0.090

INTERPRETATION
--------------------------------------------
  Cycle state is inferred from composite level, momentum and breadth.
  Recession probability is a separate risk measure, not the cycle state.
  Lead/lag weights are priors pending walk-forward estimation.
  Historical values should be evaluated with real-time data vintages
  before using the detector for production backtesting.

============================================================================
CYCLE: Recovery | ENSEMBLE: +49.68
============================================================================
```

## Appendix B — Sources

**Primary (FRED, series IDs in body):** GDPC1, GDI, INDPRO, TCU, COMPRNFB, UNRATE, PAYEMS,
CIVPART, ICSA, CCSA, JTSJOL, AWHMAN, CPIAUCSL, CPILFESL, PCEPI, PCEPILFE, FEDFUNDS, DFF, DGS10,
DGS2, T10Y2Y, MORTGAGE30US, BAMLH0A0HYM2, BUSLOANS, VIXCLS, SP500, BAA10Y, DTWEXBGS, HOUST,
PERMIT, CSUSHPISA, MSACSR, HSN1F, UMCSENT, PCE, RETAILSMNSA, PSAVERT, W068RCQ027SBEA, GFDEBTN,
FGEXPND, BOPGSTB, EXPGS, IMPGS, NETFI, DCOILWTICO, NFCI. Retrieved 30 Sep 2026.

**Primary (agencies):**
- Federal Reserve, FOMC statement, 16 Sep 2026 — federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm
- Federal Reserve, Chair Warsh press conference transcript, 16 Sep 2026
- BLS, The Employment Situation — August 2026, released 4 Sep 2026 (USDL-26-1435)
- NBER, Business Cycle Dating — last peak Feb 2020, last trough Apr 2020; no 2026 recession declared

**Secondary (corroboration only, not for headline numbers):**
- The National, 28 Sep 2026 — oil / US-Iran talks stalemate
- Daily Post, 29 Sep 2026 — WTI $107 Monday spike, $92 Tuesday
- S&P Global / State Street / Commerzbank / Daiwa — September flash PMIs (global, non-FRED)
- NBS China / Reuters, 30 Sep 2026 — China official manufacturing PMI 50.1

**Explicitly NOT cited and NOT to be used:** SAHM rule reading (unverified vintage), any
consensus forecast without attribution, any 2025 search-result GDP figures that conflict with FRED
GDPC1.
