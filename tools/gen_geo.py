"""Build /assets/data/geography.json — the single source of truth for the
Y-Square geographic and topical taxonomy.

This one file drives:
  - the desktop mega-menu markup        (generated into every page)
  - the mobile accordion                (same markup, CSS/JS transform)
  - the region and subregion pages      (generated from the same data)
  - the client-side search index        (regions searchable by name)
  - the sitemap                         (walked from the same tree)

Edit here, re-run, redeploy. Nothing else needs to change.

Classification is deliberately editorial rather than canonical: several
countries legitimately sit in more than one subregion (Austria, Germany,
Switzerland, Poland, Slovenia, Russia, Mauritania, Ethiopia...). Each keeps
its PRIMARY subregion here; the duplication the brief allows is expressed by
`also` links rather than by duplicating the country row, so the nav stays
navigable instead of turning into a 200-row list.
"""

import json, os

ROOT = r"C:\Users\ffaay\y-squre-site"
OUT = os.path.join(ROOT, "assets", "data", "geography.json")


def R(slug, name, lede, sections, also=None):
    return {"slug": slug, "name": name, "path": f"/geopolitics/{slug}/",
            "lede": lede, "sections": sections, "also": also or []}


def S(slug, name, countries, scope):
    return {"slug": slug, "name": name,
            "countries": [{"name": c, "anchor": slugify(c)} for c in countries],
            "scope": scope}


def slugify(text):
    """Stable, URL-safe anchor for a country name.

    Deterministic on purpose: the sitemap, the mega-menu links and the
    country table on the subregion page must all agree, and this file is
    regenerated often. Do not make it depend on anything outside itself.
    """
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in " -'’":
            keep.append("-")
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


TAXONOMY = {
    "version": "2026-09-27",
    "note": ("Editorial taxonomy. Subregion assignment is a publishing choice, not a "
             "geographic fact. 'also' lists a country's secondary placement without "
             "repeating it in the menu."),

    # ---------------------------------------------------------------- geographic
    "regions": [
        R("north-america", "North America",
          "Trade and tariff policy, alliance commitments, border and immigration policy, "
          "and the fiscal and monetary divergence across Canada, the United States and "
          "Mexico.",
          [S("canada-united-states-mexico", "Canada, United States & Mexico",
             ["Canada", "Mexico", "United States"],
             "USMCA compliance, tariff and trade-policy actions, and the monetary and "
             "fiscal divergence between the three.")]),

        R("latin-america", "Latin America & Caribbean",
          "Commodity export dependence, fiscal stress, monetary credibility and electoral "
          "and constitutional developments. Debt and capital-flow dynamics are the "
          "recurring transmission channel.",
          [S("south-america", "South America",
             ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
              "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"],
             "Commodity terms of trade, sovereign spreads and currency regimes."),
           S("central-america-latam", "Central America",
             ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras",
              "Nicaragua", "Panama"],
             "Canal and shipping exposure, remittance dependence, and fiscal stress."),
           S("caribbean-latam", "Caribbean",
             ["Antigua and Barbuda", "Bahamas", "Barbados", "Cuba", "Dominica",
              "Dominican Republic", "Grenada", "Haiti", "Jamaica",
              "Saint Kitts and Nevis", "Saint Lucia",
              "Saint Vincent and the Grenadines", "Trinidad and Tobago"],
             "Tourism dependence, energy import costs, and debt restructuring.")]),

        R("europe", "Europe",
          "Energy security, the sanctions architecture, fiscal fragmentation, and monetary "
          "policy divergence between the euro area and the periphery. Classified by "
          "geographic subregion; the placement of individual states is an editorial "
          "choice and is revised rather than treated as settled.",
          [S("western-europe", "Western Europe",
             ["Austria", "Belgium", "France", "Germany", "Ireland", "Luxembourg",
              "Netherlands", "Switzerland", "United Kingdom"],
             "Euro area policy, sovereign issuance and energy pricing. "
             "The UK is covered here; see the analysis section for sterling "
             "and gilt mechanics."),
           S("northern-europe", "Northern Europe",
             ["Denmark", "Finland", "Iceland", "Norway", "Sweden"],
             "Nordic policy divergence, energy exports, and currency hedging."),
           S("southern-europe", "Southern Europe",
             ["Andorra", "Cyprus", "Greece", "Italy", "Malta", "Portugal",
              "San Marino", "Spain", "Vatican City"],
             "Debt sustainability, bank-sovereign loops, and euro-area convergence. "
             "Balkan states are listed under Balkans & Southeastern Europe."),
           S("central-europe", "Central Europe",
             ["Austria", "Czechia", "Germany", "Hungary", "Liechtenstein", "Poland",
              "Slovakia", "Slovenia", "Switzerland"],
             "Industrial exposure, energy imports, and EU fiscal rules."),
           S("eastern-europe", "Eastern Europe",
             ["Belarus", "Moldova", "Romania", "Russia", "Ukraine"],
             "War economy, sanctions exposure, and currency management. "
             "Central European members appear under Central Europe."),
           S("balkans", "Balkans & Southeastern Europe",
             ["Albania", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Kosovo",
              "Montenegro", "North Macedonia", "Serbia", "Slovenia"],
             "EU accession process, energy interconnection, and political risk."),
           S("baltics", "Baltic States",
             ["Estonia", "Latvia", "Lithuania"],
             "Euro adoption, energy independence from Russia, and sanctions compliance."),
           ],
          also=["Faroe Islands and Greenland are tracked under Northern Europe where "
                "relevant to coverage."]),

        R("middle-east-north-africa", "Middle East & North Africa",
          "Conflict spillovers, energy chokepoints, sanctions regimes, and water and "
          "labour migration. Kept as distinct subregions because a single flat list "
          "hides the Gulf/Levant distinction that drives the pricing.",
          [S("gulf", "Gulf",
             ["Bahrain", "Kuwait", "Oman", "Qatar", "Saudi Arabia",
              "United Arab Emirates"],
             "Oil production policy, OPEC+ compliance, and regional capital flows."),
           S("levant", "Levant",
             ["Jordan", "Lebanon", "Palestinian territories", "Syria"],
             "Refugee and aid flows, reconstruction financing, and border economics."),
           S("north-africa", "North Africa",
             ["Algeria", "Egypt", "Libya", "Morocco", "Sudan", "Tunisia", "Mauritania"],
             "Sovereign debt, energy subsidies, and Mediterranean supply routes."),
           S("eastern-mediterranean", "Eastern Mediterranean",
             ["Cyprus", "Greece", "Israel", "Turkey"],
             "Maritime boundaries, energy transit, and military posture."),
           S("iran-iraq", "Iran & Iraq",
             ["Iran", "Iraq"],
             "Sanctions enforcement, oil exports, and militia-linked supply risk."),
           S("turkey-anatolia", "Turkey & Anatolia",
             ["Turkey"],
             "Inflation credibility, lira policy, and regional economic influence.")]),

        R("sub-saharan-africa", "Sub-Saharan Africa",
          "Commodity and debt dynamics, resource-exporter fiscal dependence, and regional "
          "trade blocs. Coverage is Sub-Saharan; North African states are covered under "
          "Middle East & North Africa.",
          [S("west-africa", "West Africa",
             ["Benin", "Burkina Faso", "Cabo Verde", "Cote d'Ivoire", "Gambia", "Ghana",
              "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Niger", "Nigeria",
              "Senegal", "Sierra Leone", "Togo"],
             "CFA franc arrangements, commodity terms of trade, and fiscal consolidation."),
           S("east-africa", "East Africa",
             ["Kenya", "Tanzania", "Uganda", "Rwanda", "Burundi", "Ethiopia",
              "South Sudan", "Malawi", "Zambia", "Zimbabwe"],
             "Inflation, exchange-rate regimes, and regional market integration."),
           S("horn-of-africa", "Horn of Africa",
             ["Djibouti", "Eritrea", "Ethiopia", "Somalia"],
             "Shipping-route risk, trade corridor disruption, and drought exposure."),
           S("central-africa", "Central Africa",
             ["Cameroon", "Central African Republic", "Chad",
              "Republic of the Congo", "Democratic Republic of the Congo",
              "Equatorial Guinea", "Gabon", "Sao Tome and Principe"],
             "Oil and mineral rents, and conflict-affected corridors."),
           S("southern-africa", "Southern Africa",
             ["Angola", "Botswana", "Eswatini", "Lesotho", "Mauritius",
              "Mozambique", "Namibia", "South Africa", "Zambia", "Zimbabwe"],
             "Currency crises, reserve accumulation, and power supply.")],
          also=["Mauritania also appears under North Africa, which is where its "
                "primary structural coverage sits."]),

        R("asia", "Asia",
          "Regional trade architecture, semiconductor and energy supply chains, maritime "
          "disputes, and currency policy across the largest growth block in the world.",
          [S("central-asia", "Central Asia",
             ["Kazakhstan", "Kyrgyzstan", "Tajikistan", "Turkmenistan", "Uzbekistan"],
             "Commodity export revenue, and trade corridors through Russia and China."),
           S("east-asia", "East Asia",
             ["China", "Japan", "Mongolia", "North Korea", "South Korea", "Taiwan"],
             "Semiconductor supply chains, export controls, and the yen/yuan regime."),
           S("south-asia", "South Asia",
             ["Afghanistan", "Bangladesh", "Bhutan", "India", "Maldives", "Nepal",
              "Pakistan", "Sri Lanka"],
             "Trade measures, energy import dependence, and reserve management."),
           S("southeast-asia", "Southeast Asia",
             ["Brunei", "Cambodia", "Indonesia", "Laos", "Malaysia", "Myanmar",
              "Philippines", "Singapore", "Thailand", "Timor-Leste", "Vietnam"],
             "Electronics assembly, critical-mineral processing, and ASEAN tariff policy."),
           S("caucasus", "Caucasus",
             ["Armenia", "Azerbaijan", "Georgia"],
             "Corridors and pipeline leverage, and the sanctions environment around the "
             "South Caucasus routes. The Gulf, Levant and Anatolia sit under Middle East "
             "& North Africa, which holds their structural coverage."),
           ]),

        R("oceania-pacific", "Oceania & Pacific",
          "Pacific security architecture, supply-chain reconfiguration, and the fiscal "
          "and climate exposure of small island states.",
          [S("australia-new-zealand", "Australia & New Zealand",
             ["Australia", "New Zealand"],
             "Commodity exports, RBA policy, and Pacific financing arrangements."),
           S("pacific-islands", "Pacific Islands",
             ["Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "Palau",
              "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu",
              "Papua New Guinea"],
             "Climate finance, shipping-route risk, and resource projects.")]),
    ],

    # ------------------------------------------------------------------ topical
    "topics": [
        {"slug": "global", "name": "Global", "path": "/geopolitics/global/",
         "lede": "Stories not primarily associated with one region.",
         "children": [
             {"slug": "world", "name": "World", "scope": "Cross-border developments with no single national home."},
             {"slug": "global-economy", "name": "Global Economy", "scope": "Global growth, trade-weighted output, and synchronised cycles."},
             {"slug": "global-trade", "name": "Global Trade", "scope": "Tariff action, supply chains, and trade agreement negotiation."},
             {"slug": "international-organizations", "name": "International Organizations", "scope": "WTO, IMF, UN and multilateral institution positions."},
             {"slug": "climate-energy", "name": "Climate & Energy", "scope": "Energy transition, grid investment, and carbon policy."},
             {"slug": "global-security", "name": "Global Security", "scope": "Defence posture, alliances, and arms transfers."},
             {"slug": "global-technology", "name": "Global Technology", "scope": "Export controls, semiconductor capacity, and platform regulation."}]},
        {"slug": "markets", "name": "Markets", "path": "/markets/",
         "lede": "How macro and geopolitical developments price into assets.",
         "children": [
             {"slug": "stocks", "name": "Stocks", "scope": "Equity index and single-name analysis."},
             {"slug": "indices", "name": "Indices", "scope": "Index construction, concentration and rebalancing."},
             {"slug": "bonds", "name": "Bonds", "scope": "Sovereign and corporate credit, curves and issuance."},
             {"slug": "commodities", "name": "Commodities", "scope": "Energy, metals and agricultural pricing."},
             {"slug": "currencies", "name": "Currencies", "scope": "FX regimes, carry, and cross-rates."},
             {"slug": "crypto", "name": "Crypto", "scope": "Digital assets as a macro and liquidity proxy."},
             {"slug": "companies", "name": "Companies", "scope": "Filings, guidance, and capital allocation."},
             {"slug": "sectors", "name": "Sectors", "scope": "Cross-company industry structure."}]},
        {"slug": "macro", "name": "Macro", "path": "/macro/",
         "lede": "The aggregate economy: prices, output, labour and policy.",
         "children": [
             {"slug": "inflation", "name": "Inflation", "scope": "Headline and core, supply versus demand drivers."},
             {"slug": "gdp", "name": "GDP", "scope": "Growth accounting and revisions."},
             {"slug": "interest-rates", "name": "Interest Rates", "scope": "Policy paths, curve shape and term premia."},
             {"slug": "monetary-policy", "name": "Monetary Policy", "scope": "Balance sheets, frameworks and credibility."},
             {"slug": "fiscal-policy", "name": "Fiscal Policy", "scope": "Budgets, debt sustainability and sovereign issuance."},
             {"slug": "employment", "name": "Employment", "scope": "Labour markets, wages and participation."},
             {"slug": "trade", "name": "Trade", "scope": "Tariffs, current accounts and re-exports."},
             {"slug": "currencies", "name": "Currencies", "scope": "Exchange-rate pass-through to prices."}]},
        {"slug": "research", "name": "Research", "path": "/research/",
         "lede": "Longer-form notes with stated methodology and named sources.",
         "children": [
             {"slug": "macro-research", "name": "Macro Research", "scope": "Cross-country macro frameworks."},
             {"slug": "geopolitical-research", "name": "Geopolitical Research", "scope": "Structural and thematic geopolitical work."},
             {"slug": "sector-research", "name": "Sector Research", "scope": "Industry structure and profitability."},
             {"slug": "market-research", "name": "Market Research", "scope": "Pricing behaviour and cross-asset allocation."},
             {"slug": "data-statistics", "name": "Data & Statistics", "scope": "Primary data notes and series construction."}]},
        {"slug": "blog", "name": "Blog", "path": "/blog/",
         "lede": "Analysis, opinion, explainers and commentary — labelled as opinion, never as reporting.",
         "children": [
             {"slug": "analysis", "name": "Analysis", "scope": "Our interpretation of data and events."},
             {"slug": "opinion", "name": "Opinion", "scope": "Argument and commentary, clearly held to our own view."},
             {"slug": "explainers", "name": "Explainers", "scope": "Mechanics, written to be understood."},
             {"slug": "commentary", "name": "Commentary", "scope": "Reactions to the week's developments."},
             {"slug": "research-notes", "name": "Research Notes", "scope": "Method-documented research documents."}]},
    ],

    # ------------------------------------------------------- content type labels
    "content_types": [
        {"id": "news", "label": "News", "desc": "Reporting on an event, attributed to its source."},
        {"id": "analysis", "label": "Analysis", "desc": "Our interpretation of events or data."},
        {"id": "explainer", "label": "Explainer", "desc": "An explanation of a mechanism."},
        {"id": "research", "label": "Research Note", "desc": "A longer document with a stated method."},
    ],
}


def count():
    geo = sum(len(r["sections"]) for r in TAXONOMY["regions"])
    countries = sum(len(s["countries"]) for r in TAXONOMY["regions"] for s in r["sections"])
    topics = sum(len(t["children"]) for t in TAXONOMY["topics"])
    return geo, countries, topics


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(TAXONOMY, f, indent=1, ensure_ascii=False)
        f.write("\n")
    g, c, t = count()
    print(f"  {OUT}  {os.path.getsize(OUT)}B")
    print(f"  {len(TAXONOMY['regions'])} regions / {g} subregions / {c} country rows")
    print(f"  {len(TAXONOMY['topics'])} topics / {t} topic children")
