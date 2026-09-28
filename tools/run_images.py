"""Run the image fetch over every article and emit assets/img/manifest.json.

Manifest shape: { article_path: [ {url, page, author, licence, licence_url, title} ] }

Attribution is stored per image so the page generator can render it. A file with
no author string is dropped rather than shown with a blank credit, because
"Photo: " with nothing after it is not a credit.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_images import fetch_for, slug
import gen_country_profiles as GCP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "manifest.json")
BUDGET = 90          # seconds per article, as specified
WANT = 2             # 1-3 images; we aim for 2 and accept fewer

# Concept articles. The subject is an institution or an idea, so the image must
# name that institution -- not a generic finance photograph.
CONCEPT = {
    "research/2026/09/26/central-bank-balance-sheets.html":
        (["Bank of England", "Threadneedle Street"],
         "central bank balance sheet is a chart; use the institution's building",
         ["japan", "china", "eurozone"]),
    "blog/2026/09/26/reading-central-bank-intent.html":
        (["Bank of England", "Threadneedle Street"],
         "same subject as the balance-sheet note",
         ["japan", "china", "eurozone"]),
    "blog/2026/09/26/understanding-currency-depreciation.html":
        (["Bank of Japan", "Nihonbashi", "Tokyo"],
         "a depreciating currency; the banknote-issuing institution is the subject",
         ["japan" ]),
}

# Every other article is a country explainer, so the country and its capital are
# the subject. Capital first, because it is the more reliable search term and it
# is the actual place photographed.
CAPITALS = {
    "China": "Beijing", "India": "New Delhi", "Japan": "Tokyo", "Russia": "Moscow",
    "Vietnam": "Hanoi", "Indonesia": "Jakarta", "Thailand": "Bangkok",
    "Malaysia": "Kuala Lumpur", "Singapore": "Singapore", "Philippines": "Manila",
    "Cambodia": "Phnom Penh", "Laos": "Vientiane", "Myanmar": "Naypyidaw",
    "Brunei": "Bandar Seri Begawan", "Timor-Leste": "Dili",
    "France": "Paris", "Germany": "Berlin", "Switzerland": "Bern",
    "United Kingdom": "London", "Saudi Arabia": "Riyadh",
    "United Arab Emirates": "Abu Dhabi", "Qatar": "Doha", "Kuwait": "Kuwait City",
    "Bahrain": "Manama", "Oman": "Muscat", "Egypt": "Cairo", "Algeria": "Algiers",
    "Morocco": "Rabat", "Tunisia": "Tunis", "Libya": "Tripoli", "Sudan": "Khartoum",
    "Mauritania": "Nouakchott", "Canada": "Ottawa", "United States": "Washington",
    "Mexico": "Mexico City", "Australia": "Canberra", "New Zealand": "Wellington",
}

# The countries this site covers, so a file about any OTHER country is rejected.
COVERED = {c.lower() for c in CAPITALS}


def run():
    manifest = {}
    if os.path.exists(OUT):
        manifest = json.load(open(OUT, encoding="utf-8"))

    jobs = []
    for path, (terms, _why, banned) in CONCEPT.items():
        jobs.append((path, terms, banned, "concept"))
    for sl, (name, _chans, _angle, _watch) in GCP.COUNTRIES.items():
        cap = CAPITALS.get(name)
        if not cap:
            print(f"  SKIP {name}: no capital mapped")
            continue
        banned = sorted(COVERED - {name.lower()})
        jobs.append((f"explainer/{sl}/macro-transmission.html", [name, cap], banned, name))

    for path, terms, banned, label in jobs:
        if path in manifest and len(manifest[path]) >= 1:
            print(f"  cached  {path:<52} {len(manifest[path])}")
            continue
        got, meta = fetch_for(path, terms, banned, want=WANT, budget_s=BUDGET)
        clean = []
        for g in got:
            if not g["author"]:
                print(f"    dropped (no author): {g['title'][:48]}")
                continue
            clean.append({k: g[k] for k in
                          ("url", "page", "author", "licence", "licence_url", "title")})
        if clean:
            manifest[path] = clean
        else:
            manifest[path] = []          # publish without, as specified
        print(f"  {'IMG ' if clean else 'none'} {path:<52} {len(clean)} "
              f"({meta['calls']} calls, {meta['seconds']}s)")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(manifest, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1)
    withimg = sum(1 for v in manifest.values() if v)
    print(f"\narticles: {len(manifest)} | with images: {withimg} | "
          f"published without: {len(manifest) - withimg}")


if __name__ == "__main__":
    run()
