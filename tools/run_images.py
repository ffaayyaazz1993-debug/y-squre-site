"""Run the image fetch over every article and emit assets/img/manifest.json.

Manifest shape: { article_path: [ {url, page, author, licence, licence_url, title} ] }

Attribution is stored per image so the page generator can render it. A file with
no author string is dropped rather than shown with a blank credit, because
"Photo: " with nothing after it is not a credit.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_images import fetch_for, slug
import fetch_images
import image_subjects as IMG_SUBJ
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
        (["banknote", "euro note", "euro banknote", "bank note", "currency note"],
         "the article explains how a currency loses value, so the currency is "
         "the subject. Not a place: a street in Tokyo is a picture of Tokyo, "
         "not a picture of depreciation.",
         ["japan"]),
}

# Spellings Commons actually uses. "Washington" alone also matches Washington
# State, so the D.C. forms are listed too, and for the United States the
# alternative cities that genuinely depict its economy.
def build_page_ban(country_name):
    """Cities and states that must not stand in for THIS country page.

    Kept separate from the global ban because a city can be the subject of one
    page and disqualifying on another: New York belongs on the United States
    page and is not a reason to reject it there, while Zurich is not the
    subject of the Switzerland page."""
    slug = None
    for sl, (name, *_rest) in GCP.COUNTRIES.items():
        if name == country_name:
            slug = sl
            break
    cities = IMG_SUBJ.DISALLOWED.get(slug or "", [])
    if not cities:
        return None
    return r"\b(?:" + "|".join(re.escape(c) for c in cities) + r")\b"


def build_place_regex(terms):
    """One alternation over every accepted spelling of the capital, so a file
    titled "Washington, D.C." and one titled "New York" both satisfy the place
    gate for the United States, while a disallowed city never does."""
    alts = [t for t in terms[1:] if t]
    if not alts:
        return None
    body = "|".join(re.escape(a) for a in alts)
    return re.compile(r"\b(?:" + body + r")\b", re.I)


def capital_terms(name):
    """[country, capital, ...accepted spellings] for the gate."""
    terms = [name, CAPITALS[name]]
    for cap, alts in IMG_SUBJ.CAPITALS.values():
        if cap == CAPITALS[name]:
            terms += alts
            break
    seen, out = set(), []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out

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


def used_urls(manifest, exclude=()):
    """Every image file already claimed by another page.

    The same photograph appearing on two pages is a visible defect on /latest/,
    where both cards sit next to each other in the same rail. Two articles about
    the same institution will otherwise match the same obvious building, so the
    second one has to be told to look elsewhere."""
    out = set()
    for path, imgs in manifest.items():
        if path in exclude:
            continue
        for g in imgs:
            out.add(g["url"].split("?")[0])
    return out


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
        terms = capital_terms(name)
        jobs.append((f"explainer/{sl}/macro-transmission.html", terms, banned, name))

    for path, terms, banned, label in jobs:
        if path in manifest and len(manifest[path]) >= 1:
            print(f"  cached  {path:<52} {len(manifest[path])}")
            continue
        # The place gate needs a regex, not a single string, because a capital
        # has several spellings ("Washington" / "Washington, D.C." / "New
        # York"). Passing only the first one rejected files titled with the
        # others. build_place_regex turns the accepted set into one alternation
        # so the file has to name one of them, and no disallowed city counts.
        place_re = build_place_regex(terms)
        page_ban = build_page_ban(label)
        taken = used_urls(manifest, exclude=(path,))
        raw, meta = fetch_for(path, terms, banned, want=WANT + 3, budget_s=BUDGET,
                              place=place_re, page_ban=page_ban)
        # Drop anything already used on another page, then take the first WANT.
        raw = [g for g in raw if g["url"].split("?")[0] not in taken]
        got = raw[:WANT]
        clean = []
        for g in got:
            if not g["author"]:
                print(f"    dropped (no author): {g['title'][:48]}")
                continue
            clean.append({k: g[k] for k in
                          ("url", "page", "author", "licence", "licence_url", "title")})
        for g in raw[WANT:]:
            print(f"    skipped (already used elsewhere): {g['title'][:44]}")
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
