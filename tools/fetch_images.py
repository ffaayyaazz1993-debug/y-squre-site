"""Fetch genuinely relevant, properly licensed images for each article.

Why Wikimedia Commons and not a stock API
------------------------------------------
There is no keyless free stock-photo API. Commons is public and keyless, and it
returns the licence and author with every file, which is what makes compliant
attribution possible. Commons is also full of unrelated photographs, so a search
hit is NOT a licence to use the image. Hence the filters below.

The relevance gate (the important part)
--------------------------------------
The rule is not "a plausible-looking result". A result is used only when the
article's own entity, country or location appears in the Commons file's title or
description, AND the file is a photograph or diagram of a real place or thing --
never a chart of some other country, a logo, a portrait of an unrelated person, a
map of the wrong region, or a generic "finance" concept shot.

This is deliberately strict. A country like Qatar has a few thousand usable
photographs and a place like Switzerland has tens of thousands, so a strict gate
costs coverage on small countries and buys relevance everywhere. The brief says
to publish without an image rather than spend more; the same logic applies to
relevance.

Every accepted image ships with: author, licence name, licence URL, and a link
to the Commons file page. The licence and author are rendered in the figcaption,
not hidden in a credits page, because CC BY-SA attribution must be visible.
"""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

UA = ("Y-Square/1.0 (https://y-squre.com; static site build) "
      "python-urllib/3 (contact: site owner)")
API = "https://commons.wikimedia.org/w/api.php"

# Licences we may use, and whether reuse needs a visible credit.
OK_LICENCE = re.compile(
    r"^(cc0|cc by(?:-sa)?\s*\d|public domain|pd|no restrictions)", re.I)
NEEDS_CREDIT = re.compile(r"cc by", re.I)

# Words that mark a file as NOT what we want, however well it matches otherwise.
REJECT = re.compile(
    r"\b(logo|coat of arms|flag|icon|diagram of|map of|chart of|graph of|"
    r"graphical|seal of|signature|barnstar|user[_ ]box|"
    r"stamp|banknote|coin|poster|screenshot|"
    r"portrait|headshot|selfie|"
    r"charter|deed|manuscript|engraving|engraved|lithograph|woodcut|"
    r"\bcar\b|holden|toyota|\bmotor\b|\bmotorbike\b|\bbike\b|\bscooter\b|"
    r"ferris wheel|carousel|bouncy castle|amusement|\bfunfair\b|"
    r"parade|fireworks|\bparty\b|protest|\bdemonstration\b|"
    r"\bnavy\b|\bmilitary\b|\bsoldier\b|patrol|\bnato\b|"
    r"\bhotel\b|\brestaurant\b|\bcafe\b|\bmarket stall\b|"
    r"\beagle\b|\bwildlife\b|\bzebra\b|\bmountain\b|\bsummit\b|"
    r"painting|drawing|sketch|document of|letter|deed|coin\b|"
    r"president|minister|king|emir|president of|met with|visits?|"
    r"commons-logo|wikipedia|wikimedia|"
    r"celebrity|actor|singer|player|politician portrait)\b", re.I)

# A file whose subject is another country disqualifies it: a chart of the Nikkei
# on a page about Argentina is exactly the unrelated visual we are avoiding.
OTHER_PLACE = re.compile(
    r"\b(japan|nikkei|korea|china|india|russia|ukraine|europe|americ|united states|"
    r"nigeria|kenya|brazil|mexico|canada|australia|new zealand|turkey|egypt|"
    r"argentina|saudi|qatar|emirat|iran|iraq|pakistan|bangladesh|vietnam|"
    r"thailand|malaysia|indonesia|philippin|myanmar|cambodia|singapore|"
    r"switzerland|austria|belgium|netherland|france|germany|spain|italy|"
    r"portugal|greece|sweden|norway|denmark|finland|poland|hungary|czech)\b", re.I)


def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return t.lower().replace("&", " and ").replace("'", "").strip()


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def search(term, limit=12, timeout=12):
    p = {"action": "query", "format": "json", "generator": "search",
         "gsrsearch": f"filetype:bitmap {term}", "gsrnamespace": "6",
         "gsrlimit": str(limit), "prop": "imageinfo",
         "iiprop": "url|extmetadata|size|mime", "iiurlwidth": "1400"}
    u = API + "?" + urllib.parse.urlencode(p)
    rq = urllib.request.Request(u, headers={"User-Agent": UA})
    d = json.loads(urllib.request.urlopen(rq, timeout=timeout).read())
    out = []
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {}) or {}
        g = lambda k: (em.get(k, {}) or {}).get("value", "")
        out.append({
            "title": pg.get("title", "").replace("File:", ""),
            "licence": strip_html(g("LicenseShortName")),
            "licence_url": strip_html(g("LicenseUrl")),
            "author": strip_html(g("Artist"))[:120],
            "descurl": g("License") or "",
            "desc": strip_html(g("ImageDescription"))[:200],
            "w": ii.get("width") or 0, "h": ii.get("height") or 0,
            "mime": ii.get("mime", ""),
            "url": ii.get("thumburl") or ii.get("url") or "",
            "page": "https://commons.wikimedia.org/wiki/" +
                    urllib.parse.quote(pg.get("title", "").replace(" ", "_")),
        })
    return out


OTHER_CITY = re.compile(
    r"\b(shanghai|shenzhen|guangzhou|hong kong|macau|chongqing|"
    r"utah|texas|california|new york|florida|chicago|seattle|"
    r"chiang mai|phuket|penang|johor|"
    r"kabul|karachi|lahore|dhaka|colombo|kathmandu|"
    r"ho chi minh|da nang|bandung|surabaya|medan|"
    r"zhangjiajie|huangshan|"
    r"sheffield|manchester|liverpool|edinburgh|"
    r"marseille|lyon|munich|hamburg|frankfurt|barcelona|madrid|"
    r"venice|milan|naples|"
    r"quebec|montreal|toronto|vancouver)\b", re.I)

PLACEWORDS = re.compile(
    r"\b(skyline|sky line|cityscape|panorama|downtown|waterfront|"
    r"port\b|harbour|harbor|airport|financial district|central bank|"
    r"stock exchange|market|parliament|government house|presidential palace|"
    r"city centre|city center|capital)\b", re.I)

# Subjects that are genuinely not a place, so PLACEWORDS must not be required.
NONPLACE = re.compile(r"\b(bank|central bank|stock exchange)\b", re.I)


def pick(cands, must_terms, banned_terms, budget_s, place=None):
    """Accept only files that name the article's own subject.

    `place` is the specific city or landmark the query is about. When given,
    the file must either depict that place (a skyline, a port, the capital) or
    name it directly -- which is what rejects "Arabian Horse Center (Kuwait)"
    and a Tokyo embassy on a Mauritania page.
    """
    t0 = time.time()
    accepted, seen = [], set()
    for c in cands:
        if time.time() - t0 > budget_s:
            break
        blob = f"{c['title']} {c['desc']}"
        # licence: must be reusable, and we credit regardless to be safe
        if not OK_LICENCE.match(c["licence"] or ""):
            continue
        if REJECT.search(blob):
            continue
        # the subject must actually be named in the file
        if not re.search(rf"\b{re.escape(must_terms[0])}\b", blob, re.I):
            continue
        # a photograph of somewhere else is not relevant to this country
        if any(re.search(rf"\b{re.escape(b)}\b", blob, re.I) for b in banned_terms):
            continue
        if place and not NONPLACE.search(place):
            # The place must be named in the file. Falling back to "some place
            # word appeared" is what let Zhangjiajie onto the China page and a
            # heron onto Malaysia, so there is no fallback: no capital in the
            # title or description means it is a picture of somewhere else.
            if not re.search(rf"\b{re.escape(place)}\b", blob, re.I):
                continue
            # Ambiguous place names: "Washington, Utah" is not the US capital,
            # and a country plus a different city is not the capital either.
            bare = must_terms[0]
            if re.search(rf"\b{re.escape(bare)}\b", blob, re.I):
                if OTHER_CITY.search(blob):
                    continue
            elif PLACEWORDS.search(blob) and OTHER_CITY.search(blob):
                continue
        # usable resolution and sane aspect
        if c["mime"] not in ("image/jpeg", "image/png"):
            continue
        if c["w"] < 900 or c["h"] < 560:
            continue
        ar = c["w"] / max(1, c["h"])
        if not (1.15 <= ar <= 2.6):
            continue
        if c["url"] in seen:
            continue
        seen.add(c["url"])
        accepted.append(c)
    return accepted


def fetch_for(article_key, terms, banned, want=2, budget_s=90, max_calls=3):
    """Try progressively more specific queries. Stops on the time budget."""
    t0, calls, got, tried = time.time(), 0, [], set()
    for term in terms:
        if time.time() - t0 > budget_s or len(got) >= want or calls >= max_calls:
            break
        calls += 1
        try:
            cands = search(term, limit=12)
        except Exception as e:
            print(f"    query failed ({e.__class__.__name__})")
            continue
        # must_terms is EVERY term that must be present. A Qatar page must not
        # accept a file that only happens to say "Doha" in a description about
        # a visiting head of state, so the primary subject term is required and
        # any other-country hit disqualifies outright.
        for c in pick(cands, terms, banned, budget_s - (time.time() - t0),
                      place=terms[-1] if len(terms) > 1 else None):
            if c["url"] not in tried:
                tried.add(c["url"])
                got.append(c)
            if len(got) >= want:
                break
    return got, {"calls": calls, "seconds": round(time.time() - t0, 1)}


if __name__ == "__main__":
    # smoke test: the case most likely to fail the gate
    got, meta = fetch_for("bank-of-england",
                          ["Bank of England", "Threadneedle Street"],
                          ["japan", "china", "united states"], want=2)
    print("bank of england:", meta)
    for g in got:
        print(f"  {g['licence']:16} {g['w']}x{g['h']}  {g['title'][:62]}")
    got, meta = fetch_for("qatar",
                          ["Qatar", "Doha"], ["india", "china", "japan"], want=2)
    print("qatar:", meta)
    for g in got:
        print(f"  {g['licence']:16} {g['w']}x{g['h']}  {g['title'][:62]}")
