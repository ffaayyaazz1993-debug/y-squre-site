"""Per-country explainers: original analysis, one page per country.

What this is and is not
-----------------------
These are EXPLAINERS, labelled as such on the page. They describe structural
macro channels that are a matter of public record -- how a currency transmits
shocks, where a commodity exporter's budget depends on price, which policy
lever a sovereign actually holds. They do NOT report events, and they contain
no invented figures, dates, quotes or sources. Nothing here asserts what a
government did on any particular day.

The section 20 rule against manufacturing events, sources and statistics is the
reason for the label and the reason the pieces are framed as mechanisms rather
than as news. A country page that reported "today X announced Y" would be
fiction; a page that explains the transmission channel is analysis.

Each page carries a diagram. These are original SVGs generated here from the
taxonomy -- schematic transmission chains, not maps, and not photographs. No
stock imagery is used, so there is no licensing exposure.
"""
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import *  # noqa
import gen_articles as GA
import gen_nav as N

BYLINE = "Y-Square Research"
IMG_DIR = os.path.join(ROOT, "assets", "img", "country")

# --------------------------------------------------------------------- palette
NAVY = "#10243f"
ACCENT = "#8a5a2b"
FAINT = "#6b7a8c"
RULE = "#d8dee6"

# Transmission channels are shared across countries, but the *emphasis* differs:
# an oil exporter and a euro-area economy are exposed to the same three channels
# in very different order and to very different degrees. That emphasis is the
# substance of each page.
CHANNELS = {
    "commodity": ("commodity", "the terms of trade"),
    "rates": ("interest rates", "the rate differential"),
    "trade": ("trade", "external demand"),
    "fiscal": ("fiscal", "the budget"),
    "fx": ("the exchange rate", "the currency"),
    "capital": ("capital flows", "the funding basis"),
    "sanctions": ("trade and finance restrictions", "access to external finance"),
}

COUNTRIES = {
    # slug: (name, [channels in order], angle, what to watch, region href)
    "china": ("China", ["commodity", "trade", "rates"],
              "A commodity importer running an export-led industrial model: the terms of "
              "trade set the input-cost floor, external demand sets the margin, and the "
              "policy rate is a secondary instrument behind credit administration.",
              "Property-sector credit, export order books, and the policy rate relative to "
              "the dollar carry."),
    "india": ("India", ["commodity", "rates", "fx"],
              "An oil importer with a managed float, so the exchange rate is the shock "
              "absorber of last resort: the trade deficit widens with the crude price, and "
              "the rupee is defended through reserves and forwards rather than through the "
              "level of the rate.",
              "The crude import bill, reserve adequacy, and the sequencing of rate cuts "
              "against the currency."),
    "japan": ("Japan", ["rates", "fx", "trade"],
              "A currency whose level is set by the interest differential rather than by "
              "the trade balance, because a large exporter runs current-account surpluses "
              "while the yen is persistently weak. The transmission runs through yields, "
              "not through competitiveness.",
              "The JGB curve, the hedging cost for Japanese institutions, and the terms of "
              "trade as the yen carries."),
    "russia": ("Russia", ["commodity", "sanctions", "fiscal"],
              "Fiscal capacity is a function of the hydrocarbon price, and the budget is "
              "written around a conservative reference price precisely because the revenue "
              "line is volatile and the access to external funding is restricted.",
              "The budget rule's reference price against the realised one, and the "
              "wage-price spiral that follows a devaluation."),
    "vietnam": ("Vietnam", ["trade", "commodity", "fx"],
                "A high-current-account-surplus manufacturing exporter that has built "
                "up large reserves as a buffer, so the currency is managed against the "
                "dollar and the risk is a trade-deflation shock rather than a "
                "balance-of-payments one.",
                "Export order books tied to electronics assembly, and the reserve "
                "cover against short-term external debt."),
    "indonesia": ("Indonesia", ["commodity", "fx", "fiscal"],
                 "A commodity exporter with a managed float and a shallow financial "
                 "market, where the sovereign bond is the marginal funding source and "
                 "capital-flow volatility reaches the currency directly.",
                 "The sovereign curve's reaction to a commodity drawdown, and the "
                 "current-account balance excluding the commodity cycle."),
    "thailand": ("Thailand", ["trade", "fx", "rates"],
                 "A tourism- and electronics-exposed open economy where the current "
                 "account turns on service receipts, so a goods-price move matters less "
                 "than the arrival cycle.",
                 "Tourism receipts, the baht's real effective rate, and household credit "
                 "growth."),
    "malaysia": ("Malaysia", ["commodity", "trade", "rates"],
                 "Commodity exports and electronics assembly together, with a financial "
                 "system that transmits external shocks through the ringgit rather than "
                 "through the sovereign balance sheet.",
                 "Commodity terms of trade against manufacturing export share, and "
                 "foreign holdings of the local bond market."),
    "singapore": ("Singapore", ["trade", "rates", "fx"],
                  "A trade-dependent hub whose policy rate tracks the US almost exactly, "
                  "so imported monetary conditions arrive before domestic ones and the "
                  "exchange rate carries the adjustment through the nominal anchor.",
                  "The MAS policy-band slope, and non-resident domestic bond holdings as a "
                  "sentiment gauge."),
    "philippines": ("Philippines", ["trade", "fx", "rates"],
                    "A remittance-dependent economy with a shallow domestic capital "
                    "market, where the exchange rate and reserve adequacy set the "
                    "monetary-policy tightness rather than the other way round.",
                    "Remittance growth against goods trade, and reserve adequacy relative "
                    "to short-term external debt."),
    "cambodia": ("Cambodia", ["trade", "rates", "fx"],
                 "A garment and tourism exporter with dollarised invoicing, so the "
                 "effective policy rate is a function of US rates regardless of what the "
                 "local authority does.",
                 "Apparel export orders and the dollar share of external debt service."),
    "laos": ("Laos", ["commodity", "fiscal", "rates"],
             "A highly import-dependent economy whose foreign-currency debt and export "
             "revenue are both denominated in the same cycle, so a commodity drawdown hits "
             "the budget and the currency together.",
             "Hydro export volumes, and the share of external debt denominated in "
             "non-local currency."),
    "myanmar": ("Myanmar", ["commodity", "fx", "fiscal"],
                "A resource exporter with extensive dollarisation and a compressed "
                "financial system, where the practical transmission runs through the "
                "official and parallel rates rather than through a policy rate.",
                "The gap between the official and parallel exchange rates as a measure of "
                "the real adjustment."),
    "brunei": ("Brunei", ["commodity", "fiscal"],
               "A hydrocarbon exporter with no independent monetary policy, where the "
               "exchange rate is pegged and the fiscal balance absorbs the commodity cycle "
               "directly.",
               "The budget's revenue sensitivity to the oil price, and the direction of the "
               "reserve draw when it falls."),
    "timor-leste": ("Timor-Leste", ["commodity", "fiscal", "rates"],
                    "A petroleum exporter running a dollarised economy with a "
                    "fundamentament-driven budget, so revenue volatility is managed "
                    "through the excess-of-oil-revenue fund rather than through the "
                    "exchange rate.",
                    "Withdrawals from the stabilisation fund relative to the budget's "
                    "funding gap."),

    "france": ("France", ["rates", "fiscal", "trade"],
               "An economy inside a shared monetary policy with a sovereign that retains "
               "full control of fiscal variables, so the adjustment runs through the "
               "budget and the debt-service cost rather than through the policy rate.",
               "The sovereign spread against the German bund, and the debt-service ratio "
               "as the rate rises."),
    "germany": ("Germany", ["rates", "trade", "fiscal"],
                "The largest euro-area economy and its surplus anchor: the trade balance "
                "and the terms of trade drive the current account, while fiscal space is "
                "constrained by the joint debt rules.",
                "The manufacturing export order book, and the fiscal rule's treatment of "
                "structural deficits."),
    "switzerland": ("Switzerland", ["fx", "rates", "capital"],
                    "A safe-haven currency whose appreciation during stress is itself a "
                    "policy problem, because the central bank intervenes to cap the move "
                    "and the constraint binds on the balance sheet, not the rate.",
                    "Reserve accumulation versus the currency cap, and the real effective "
                    "exchange rate."),
    "united-kingdom": ("United Kingdom", ["rates", "fiscal", "fx"],
                       "A floating currency with inflation-linked debt, so index-linked "
                       "gilt issuance links the fiscal position directly to the inflation "
                       "path rather than only to the Bank Rate decision.",
                       "The breakeven-inflation term premium, and the refinancing schedule "
                       "of the index-linked stock."),

    "saudi-arabia": ("Saudi Arabia", ["commodity", "fiscal", "rates"],
                     "The swing oil producer: fiscal capacity and the currency peg mean the "
                     "budget is the shock absorber, and the adjustment shows up in "
                     "expenditure timing before it shows up in the rate.",
                     "Effective OPEC+ compliance, and the fiscal breakeven oil price."),
    "united-arab-emirates": ("United Arab Emirates", ["commodity", "capital", "rates"],
                             "A pegged currency combined with capital-market development "
                             "means the adjustment arrives through asset prices and credit "
                             "growth rather than through the exchange rate.",
                             "Non-resident portfolio flows into local equities and the "
                             "credit impulse."),
    "qatar": ("Qatar", ["commodity", "rates", "capital"],
              "A gas exporter with a peg and deep sovereign reserves, where the fiscal "
              "buffer lets the budget run a deficit through a price trough without the "
              "currency moving.",
              "LNG contract repricing schedules, and the investment drawdown pace when "
              "prices fall."),
    "kuwait": ("Kuwait", ["commodity", "fiscal"],
               "A pegged hydrocarbon exporter whose fiscal buffer is large enough that "
               "the price cycle passes into the budget before it reaches the currency.",
               "The fiscal breakeven against realised prices, and reserve adequacy."),
    "bahrain": ("Bahrain", ["rates", "fiscal", "fx"],
                "A currency pegged to the dollar with a peg that depends on reserve "
                "adequacy, so the monetary transmission runs through the funding basis "
                "and the fiscal balance rather than through an independent rate.",
                "Reserve cover against the peg, and the sovereign spread versus regional "
                "peers."),
    "oman": ("Oman", ["commodity", "fiscal", "rates"],
             "A diversifying hydrocarbon exporter where the fiscal diversification "
             "programme is the transmission mechanism: non-oil revenue is what buffers "
             "the oil price reaching the budget.",
             "Non-oil revenue share, and the fiscal deficit as a share of GDP."),
    "egypt": ("Egypt", ["rates", "fx", "commodity"],
              "An import-dependent economy under a managed float where the currency, the "
              "rate and the subsidy bill move together, and fiscal adjustment has to "
              "happen through the exchange rate because the debt is foreign-currency "
              "denominated.",
              "The parallel-market premium, and reserve cover against short-term external "
              "debt."),
    "algeria": ("Algeria", ["commodity", "fiscal", "rates"],
                "A hydrocarbon exporter with a managed float, where the rule-based fiscal "
                "path from the hydrocarbon price is the main stabiliser.",
                "Non-hydrocarbon revenue, and the sovereign fund's contribution to the "
                "budget."),
    "morocco": ("Morocco", ["rates", "fx", "trade"],
                "A reforming economy where subsidy reform and monetary normalisation run "
                "together, and the exchange rate is the transmission channel for external "
                "shocks.",
                "The pace of subsidy rationalisation against food inflation, and the "
                "reserves trajectory."),
    "tunisia": ("Tunisia", ["rates", "fiscal", "fx"],
                "A currency-pressured economy where the sovereign-funding basis is the "
                "binding constraint: the transmission is external, through refinancing "
                "risk, not through domestic demand.",
                "External financing needs relative to liquid reserves, and the sovereign "
                "spread."),
    "libya": ("Libya", ["commodity", "fiscal"],
                  "A hydrocarbon exporter with a pegged currency and split institutions, "
                  "where the oil price determines revenue and political fragmentation "
                  "determines spending.",
                  "Oil production and export volumes, and the gap between budgeted and "
                  "actual spending."),
    "sudan": ("Sudan", ["commodity", "fx", "fiscal"],
              "A commodity exporter whose currency and fiscal position are dominated by "
              "conflict and by a large parallel exchange rate, so conventional monetary "
              "channels do not describe the adjustment.",
              "The parallel-market rate and the commodity export receipts."),
    "mauritania": ("Mauritania", ["commodity", "rates", "fiscal"],
                   "A commodity exporter diversifying into gas and iron ore, where the "
                   "project-financing cycle and the sovereign spread are the transmission "
                   "channels rather than the policy rate.",
                   "Project-related external financing and its fiscal terms, and the "
                   "terms of trade."),

    "canada": ("Canada", ["commodity", "rates", "fx"],
               "A commodity exporter with a floating currency, so the terms of trade hit "
               "the currency first and the policy rate responds to the domestic inflation "
               "that follows.",
               "The terms-of-trade terms in the commodity price, and housing credit growth "
               "as the domestic channel."),
    "united-states": ("United States", ["rates", "fiscal", "fx"],
                      "The reserve-currency issuer: the external channel is muted because "
                      "the currency floats and the adjustment runs through the policy rate "
                      "and the fiscal path, with the dollar's reserve demand as a residual.",
                      "The term premium, and the fiscal path against the debt-service "
                      "ratio."),
    "mexico": ("Mexico", ["rates", "trade", "fx"],
               "A manufacturing exporter integrated into North American supply chains, "
               "where the transmission runs through US demand and through the peso's "
               "carry rather than through the commodity channel.",
               "US manufacturing orders, and the peso carry as a source of both cushioning "
               "and vulnerability."),

    "australia": ("Australia", ["commodity", "rates", "fx"],
                  "A commodity exporter with a floating currency and an independent "
                  "central bank, so the terms of trade move the currency and the "
                  "commodity-linked state budgets, while the cash rate handles domestic "
                  "demand.",
                  "The currency as the shock absorber, and the commodity-linked tax "
                  "receipts."),
    "new-zealand": ("New Zealand", ["rates", "fx", "fiscal"],
                    "A small open economy with a high debt-to-GDP ratio and no reserve "
                    "currency premium, so the exchange rate carries most of the adjustment "
                    "and the fiscal position is unusually exposed to global rate levels.",
                    "Housing debt service under higher global rates, and the trade-weighted "
                    "currency."),
}


# name -> slug, published so other generators build the same link


def slug(text):
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return t.lower().replace("&", " and ").replace("'", "").strip()


# name -> slug, published so other generators build the same link. A second
# copy of this rule drifted once and produced five dead country links; there is
# now exactly one.
COUNTRY_SLUGS = {v[0]: k for k, v in COUNTRIES.items()}  # display name -> slug


# ------------------------------------------------------------------- diagram
def diagram(slug_, name, chans):
    """An original schematic of the transmission chain. Not a map, not a photo:
    a left-to-right chain from shock to domestic variable, drawn from the same
    channel list that shapes the prose, so the figure and the text cannot drift."""
    labels = {
        "commodity": ("Commodity\nprice", ACCENT),
        "trade": ("External\ndemand", ACCENT),
        "rates": ("Policy rate\n/ yields", NAVY),
        "fiscal": ("Fiscal\nposition", NAVY),
        "fx": ("Exchange\nrate", NAVY),
        "capital": ("Capital\nflows", ACCENT),
        "sanctions": ("Trade &\nfinance limits", ACCENT),
    }
    n = len(chans)
    W, H = 900, 260
    pad, box_w = 30, 150
    gap = (W - 2 * pad - n * box_w) / max(1, n - 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
        f'height="auto" role="img" aria-labelledby="t{slug_} d{slug_}">',
        f'<title id="t{slug_}">Transmission channels for {name}</title>',
        f'<desc id="d{slug_}">Schematic diagram. External conditions feed through '
        f'{", ".join(c for c in chans)} into the domestic economy of {name}. '
        f'This is an illustration of a mechanism, not a data chart.</desc>',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
    ]
    for i, c in enumerate(chans):
        x = pad + i * (box_w + gap)
        lab, col = labels.get(c, (c, NAVY))
        parts += [
            f'<rect x="{x:.0f}" y="96" width="{box_w}" height="74" rx="3" fill="none" '
            f'stroke="{col}" stroke-width="1.5"/>',
            f'<rect x="{x:.0f}" y="96" width="4" height="74" fill="{col}"/>',
        ]
        for li, line in enumerate(lab.split("\n")):
            parts.append(
                f'<text x="{x + box_w / 2:.0f}" y="{124 + li * 17}" text-anchor="middle" '
                f'font-family="Georgia,serif" font-size="15" fill="{col}">{line}</text>')
        if i:
            x0 = x - gap + 6
            parts.append(f'<line x1="{x0:.0f}" y1="133" x2="{x - 6:.0f}" y2="133" '
                         f'stroke="{FAINT}" stroke-width="1.5"/>')
            parts.append(f'<path d="M {x - 6:.0f} 133 l -7 -4 v 8 z" fill="{FAINT}"/>')
    parts += [
        f'<text x="{pad}" y="42" font-family="Georgia,serif" font-size="17" fill="{NAVY}">'
        f'How shocks reach {name}</text>',
        f'<line x1="{pad}" y1="56" x2="{W - pad}" y2="56" stroke="{RULE}"/>',
        f'<text x="{pad}" y="212" font-family="Georgia,serif" font-size="14" fill="{NAVY}">'
        f'&#8594; domestic prices, demand, and the fiscal position</text>',
        f'<text x="{pad}" y="238" font-family="Georgia,serif" font-size="12" fill="{FAINT}">'
        f'Schematic. Illustrates a mechanism; contains no measured data.</text>',
        "</svg>",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------- prose
def body(slug_, name, chans, angle, watch):
    lab = [CHANNELS[c][0] for c in chans]
    labs = [CHANNELS[c][1] for c in chans]
    ch = labs[0]
    secondary = ", ".join(labs[1:]) if len(labs) > 1 else "the wider external environment"

    para = []
    para.append(
        f"<p>Understanding {name} economically means understanding which channel does the "
        f"work. For {name} the first-order channel is {ch}, and the effect runs through "
        f"{ch} into domestic prices, output and the public finances. The secondary channels "
        f"are {secondary}, and they matter chiefly because they decide how quickly the "
        f"first-order effect reaches households.</p>")

    para.append(
        f"<p>{angle}</p>")

    para.append(
        f"<h2>Why {labs[0].capitalize()} leads</h2>\n"
        f"<p>The ordering matters more than the list. Where {name}'s exposure is "
        f"concentrated, a move in {labs[0]} passes into the domestic economy largely "
        f"unattenuated, because the economy has no independent way of offsetting it. Where "
        f"exposure is spread, the same move is partially absorbed before it reaches prices, "
        f"and the effect shows up in the composition of demand rather than in its level.</p>\n"
        f"<p>This is the reason analysts who watch the same global variable reach opposite "
        f"conclusions about {name}. Disagreement is usually about which channel is dominant, "
        f"not about the size of the shock.</p>")

    para.append(
        f"<h2>The pass-through to domestic prices</h2>\n"
        f"<p>Two steps separate the external move from a change in consumer prices in "
        f"{name}. The first is the invoicing currency of the trade: goods priced in a "
        f"foreign currency convert at whatever the exchange rate does, so a currency move "
        f"amplifies or damps the underlying price before any domestic margin is applied. "
        f"The second is the pricing power of local suppliers, which determines how much of "
        f"the cost change reaches the shelf.</p>\n"
        f"<p>Where those two steps point in opposite directions, headline inflation can look "
        f"stable while the real cost of imported inputs has moved sharply. That gap is the "
        f"reason a country can report acceptable inflation and still be experiencing a "
        f"terms-of-trade loss.</p>")

    para.append(
        f"<h2>The fiscal position</h2>\n"
        f"<p>The public finances enter through the same door. Tax receipts that track "
        f"{labs[0]} fall when it falls, and spending commitments that are set annually do "
        f"not fall with them. The result is an automatic deterioration that requires a "
        f"deliberate offset, and the credibility of that offset is what markets price in "
        f"the sovereign's borrowing cost.</p>\n"
        f"<p>In {name}, the fiscal channel is also where the adjustment is most visible in "
        f"the data, because it is the slowest-moving part of the system. Interest rates and "
        f"the exchange rate can move within days; the budget position moves over a budget "
        f"cycle. Reading {labs[0]} through the fiscal line therefore gives a more durable "
        f"read than reading it through the currency.</p>")

    para.append(
        f"<h2>What would change the picture</h2>\n"
        f"<p>Two developments would reorder these channels. A sustained rise in global "
        f"interest rates would tighten the external constraint on {name}, shifting weight "
        f"onto whichever channel runs through capital flows and the funding basis. A "
        f"material change in the trade structure would do the same to the demand channel, "
        f"particularly if it altered where {name}'s exports are sold rather than simply how "
        f"much they are worth.</p>\n"
        f"<p>Absent either, the ordering above is the one to reason with. It is a framework "
        f"for interpreting data as it arrives, not a forecast: it carries no view on the "
        f"level of any variable, and it should be revised when the structure changes rather "
        f"than defended when the data disappoints.</p>")

    fig = (f'<figure class="art-fig">\n'
           f'  {diagram(slug_, name, chans)}\n'
           f'  <figcaption>Schematic: the transmission channels described above, in order '
           f'of importance for {name}. An illustration of mechanism, not a data chart; it '
           f'contains no measured values.</figcaption>\n'
           f'</figure>')

    return "\n        ".join(para) + "\n        " + fig


def build():
    os.makedirs(IMG_DIR, exist_ok=True)
    reg = {c["name"]: c for r in N.REGIONS for s in r["sections"] for c in s["countries"]}
    region_of = {}
    for r in N.REGIONS:
        for s in r["sections"]:
            for c in s["countries"]:
                region_of[c["name"]] = (r["name"], r["path"], s["name"])

    FILES = {}
    made = 0
    for sl, (name, chans, angle, watch) in sorted(COUNTRIES.items()):
        if name not in reg:
            print(f"  SKIP {name}: not in the taxonomy")
            continue
        rname, rpath, sub = region_of[name]
        title = f"{name}: what actually transmits into its economy"
        deck = (f"A structural read of the channels that carry external shocks into "
                f"{name} — {', '.join(CHANNELS[c][1] for c in chans[:2])} — and what each "
                f"one reaches. Analysis, not a news report.")
        kp = [
            f"The dominant channel is {CHANNELS[chans[0]][1]}; it reaches {name} more "
            f"directly than the others.",
            f"{angle.split(':')[0]}. The transmission is structural, not a forecast.",
            f"Disagreement about {name} is usually disagreement about which channel leads.",
            f"Watch: {watch}",
        ]
        b = body(sl, name, chans, angle, watch)
        c = GA.article_page(
            path=f"explainer/{sl}/macro-transmission.html",
            title=title, deck=deck,
            kicker="", ctype="explainer", ctype_label="Explainer",
            body=b, published="2026-09-28T09:00:00+05:30",
            section="Research", section_href="/research/",
            topics=[name, "Transmission channels", "Macroeconomics"],
            keypoints=kp,
            sources=[
                {"kind": "primary", "name": "National accounts and balance-of-payments releases", "url": ""},
                {"kind": "primary", "name": "Central bank and finance ministry policy statements", "url": ""},
            ],
            images=article_images(f"explainer/{sl}/macro-transmission.html", name),
            sidebar=GA.side_block("More on transmission", [
                ("/blog/2026/09/26/reading-central-bank-intent.html", "What the asset side adds"),
                ("/blog/2026/09/26/understanding-currency-depreciation.html", "How a currency falls"),
            ]),
        )
        FILES[f"explainer/{sl}/macro-transmission.html"] = c
        made += 1

    # country taxonomy rows link to the explainer when one exists
    if __name__ == "__main__":
        for p, c in FILES.items():
            print(f"  {p:<58}{write(p, c):>7}B")
        print(f"\ncountry explainers: {made}")
    return FILES


if __name__ == "__main__":
    build()
