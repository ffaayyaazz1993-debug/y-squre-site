"""Country capitals, and what each country page is actually about.

Why this file exists
--------------------
The image gate matches a country page on its capital, because that is what
rejects "Arabian Horse Center" on a Kuwait page and a Tokyo embassy on a
Mauritania page. But no capital data existed anywhere in the project, so the
gate fell back to matching the country name alone. Three pages -- France,
Tunisia and the United States -- therefore shipped with no image for no reason
at all, the country name being common in unrelated descriptions.

CAPITALS is the missing data. Adding it is what lets those pages be matched on
their actual subject.

CONCEPT_SUBJECT is a separate rule for articles that are about a mechanism
rather than a place. "Currency depreciation" is not a place, so a place gate can
never pass it and the article shipped imageless even though Commons holds a
perfectly good photograph of euro banknotes -- the article's own subject.

A concept page may carry a photograph of the substance it explains. That is not
a stock filler: a photograph of banknotes on an article about currency is the
subject, and a photograph of a city would not be.
"""

# Capital city, plus the alternative spellings that appear in Commons metadata.
import re

CAPITALS = {
    "france": ("Paris", ["paris"]),
    "germany": ("Berlin", ["berlin"]),
    "switzerland": ("Bern", ["bern", "zürich", "zurich", "geneva", "geneve"]),
    "united-kingdom": ("London", ["london"]),
    "bahrain": ("Manama", ["manama"]),
    "kuwait": ("Kuwait City", ["kuwait city", "kuwait"]),
    "oman": ("Muscat", ["muscat"]),
    "qatar": ("Doha", ["doha"]),
    "saudi-arabia": ("Riyadh", ["riyadh", "jeddah"]),
    "united-arab-emirates": ("Abu Dhabi", ["abu dhabi", "dubai"]),
    "algeria": ("Algiers", ["algiers", "alger"]),
    "egypt": ("Cairo", ["cairo"]),
    "libya": ("Tripoli", ["tripoli", "benghazi"]),
    "morocco": ("Rabat", ["rabat", "casablanca"]),
    "sudan": ("Khartoum", ["khartoum"]),
    "tunisia": ("Tunis", ["tunis"]),
    "mauritania": ("Nouakchott", ["nouakchott"]),
    "canada": ("Ottawa", ["ottawa", "toronto"]),
    # "Washington" on its own is NOT accepted: it matches Washington State, and
    # a lumberjack exhibition in the Evergreen State got through on that basis.
    # The D.C. forms, plus the cities that genuinely depict this economy, are
    # the only spellings that count.
    "united-states": ("Washington", ["washington d.c.", "washington dc",
                                     "new york city", "new york", "chicago"]),
    "mexico": ("Mexico City", ["mexico city", "ciudad de méxico"]),
    "china": ("Beijing", ["beijing", "shanghai"]),
    "india": ("New Delhi", ["new delhi", "mumbai", "delhi"]),
    "japan": ("Tokyo", ["tokyo"]),
    "russia": ("Moscow", ["moscow", "st petersburg", "saint petersburg"]),
    "brunei": ("Bandar Seri Begawan", ["bandar seri begawan"]),
    "cambodia": ("Phnom Penh", ["phnom penh"]),
    "indonesia": ("Jakarta", ["jakarta"]),
    "laos": ("Vientiane", ["vientiane"]),
    "malaysia": ("Kuala Lumpur", ["kuala lumpur"]),
    "myanmar": ("Naypyidaw", ["naypyidaw", "yangon"]),
    "philippines": ("Manila", ["manila"]),
    "singapore": ("Singapore", ["singapore"]),
    "thailand": ("Bangkok", ["bangkok"]),
    "timor-leste": ("Dili", ["dili"]),
    "vietnam": ("Hanoi", ["hanoi", "ho chi minh"]),
    "australia": ("Canberra", ["canberra", "sydney", "melbourne"]),
    "new-zealand": ("Wellington", ["wellington", "auckland", "christchurch"]),
}

# For an article about a mechanism, the terms that identify its subject.
# Matched against Commons title + description, same as a capital is.
CONCEPT_SUBJECT = {
    "blog/2026/09/26/understanding-currency-depreciation.html": (
        ["banknote", "euro note", "euro banknote", "currency note", "paper currency"],
        "photographs of banknotes -- the article's own subject, not a place shot"),
    "research/2026/09/26/central-bank-balance-sheets.html": (
        ["federal reserve", "bank of england", "ecb", "central bank building"],
        "photographs of the institutions whose balance sheets the article explains"),
    "blog/2026/09/26/reading-central-bank-intent.html": (
        ["federal reserve", "bank of england", "ecb", "central bank building"],
        "photographs of the institutions whose intent the article reads"),
}

# Cities that must never stand in for a country page. Kept in step with
# OTHER_CITY in fetch_images.py; this is the capital-list half of the rule.
# Artwork and archival material are excluded from a page about a current
# economy, whatever they are of. A Daguerre print of the Boulevard du Temple
# and a Hiroshige woodblock of Nihonbashi are both genuine, well-licensed,
# correctly-titled photographs of the right place -- and neither shows anything
# about a modern macroeconomy. They are pictures of the past, standing in for
# the present, which is the same error as a generic stock filler.
# The year pattern is deliberately absent. "17 October 2019" appears in the
# title of a perfectly good modern photograph of Paris, and a bare 17xx-18xx
# match threw those away. Era is detected from what the file IS -- a named
# printmaker, a print medium, a dated artwork -- not from a number in the title.
ERA = re.compile(
    r"(daguerre|hiroshige|hokusai|utagawa|hiroshiga|"
    r"woodblock|woodcut|ukiyo-e|ukiyoe|"
    r"engraving|etching|lithograph|mezzotint|aquatint|"
    r"daguerreotype|albumen print|tintype|"
    r"antiquarian|antique print|"
    r"nineteenth century|18th century|17th century|"
    r"from the series|from the portfolio)", re.I)

# Events and people. A photograph of a lumberjack exhibition, a memorial
# commemoration or a pigeon in a park is a picture of an occasion, not of the
# country. These are genuine, correctly-titled, well-licensed files that pass
# every place and licence check and still say nothing about a macroeconomy.
EVENT = re.compile(
    r"(exhibition|\bfair\b|championship|tournament|\bmatch\b|festival|"
    r"concert|parade|demonstration|protest|commemoration|"
    r"memorial day|anniversary|\bfuneral\b|"
    r"\bpigeon\b|\bstatue\b|sculpture|monument|"
    r"portrait of|selfie)", re.I)

# Street works and construction are pictures of a building site, not of an
# institution. "Roadworks in Threadneedle Street" matched the Bank of England
# article because the street name matched, which is the whole failure in one
# example: correct place, wrong subject.
WORKS = re.compile(
    r"(roadworks|road work|construction|construction site|scaffolding|"
    r"scaffold|demolition|excavation|road closure|works on|"
    r"graffiti|derelict|abandoned building|demolished|"
    r"traffic|car park|parking|flytip|skip hire)", re.I)

DISALLOWED = {
    "france": ["nice", "lyon", "marseille", "bordeaux", "toulouse"],
    "united-kingdom": ["manchester", "liverpool", "edinburgh", "glasgow", "sheffield"],
    "switzerland": ["zurich", "zürich", "geneva", "geneve", "basel"],
    "united-states": ["utah", "texas", "california", "florida", "oregon", "kentucky"],
    "china": ["zhangjiajie", "huangshan", "guilin"],
    "japan": ["osaka", "kyoto", "nagoya"],
    "india": ["mumbai", "bangalore", "chennai", "kolkata"],
    "russia": ["vladivostok", "sochi"],
    "malaysia": ["penang", "johor", "kota kinabalu"],
    "thailand": ["chiang mai", "phuket", "krabi"],
    "australia": ["perth", "brisbane", "adelaide"],
    "vietnam": ["da nang", "hoi an", "phu quoc"],
    "indonesia": ["bandung", "surabaya", "medan", "bali"],
}
