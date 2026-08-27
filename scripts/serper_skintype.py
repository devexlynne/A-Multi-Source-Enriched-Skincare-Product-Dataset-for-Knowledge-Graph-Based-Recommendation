"""
===============================================================================
 SKIN TYPE FROM A SERPER SEARCH, ONE PRODUCT AT A TIME
===============================================================================
PUT YOUR KEY ON THE LINE MARKED "SERPER_KEY" BELOW, THEN RUN:

    py -m pip install requests
    py serper_skintype.py

===============================================================================
WHY THIS EXISTS

  Every free route was tested and failed on this network:

      search engines      blocked. DuckDuckGo does not connect at all, Bing,
                          Mojeek and Startpage return a captcha.
      brand websites      reachable, but the brand's DOMAIN could not be
                          identified for 3,194 products, because the tool that
                          normally resolves that is a search engine.
      retailer sites      INCIDecoder, Notino, LookFantastic, iHerb, YesStyle
                          all serve captchas. Only Boots answered.

  Three full passes over the brands' own sites reached 6.6%. Serper solves the
  one thing that was missing: it returns Google's results as structured data
  through an official API, so nothing is being scraped or impersonated.

WHAT THE FIRST 2,500-PRODUCT RUN SHOWED, AND WHAT THIS FIXES

  86.4% came back with an answer. But looking at WHERE the answers came from:

      brand or retailer site       925   42.8%
      social media / UGC           570   26.4%    <- Instagram, TikTok, Reddit
      marketplace                  373   17.3%
      third-party analysis site    293   13.6%

  Row 2 of that file cites an Instagram post. A supervisor clicking the first
  link would see instagram.com, and the whole argument collapses. So this
  version adds a DOMAIN POLICY:

      BLOCKED   instagram, facebook, tiktok, reddit, youtube, pinterest,
                lemon8, quora, ebay, aliexpress, etsy, wish
      TIER 1    the brand's own domain
      TIER 2    a recognised retailer
      TIER 3    an ingredient-analysis site
      anything else is ignored

  Serper returns ten results per query, so when the first hit is Instagram the
  script simply moves down the list instead of accepting it.

  Also fixed: "all skin types" was 63.2% of the previous answers and was being
  written into skin_type. It is a suitability claim, not a classification
  (Vendruscolo et al. 2025), so it now goes to universal_claim with a blank
  skin_type.

WHAT EVERY ROW GETS

  skin_type  sensitivity  universal_claim
  skin_type_tier        1 brand, 2 retailer, 3 analysis site
  skin_type_authority   manufacturer / retailer / analysis
  skin_type_source      the domain that answered
  skin_type_rule        which pattern fired
  skin_type_quote       the exact sentence
  skin_type_url         the page
  search_rank           which result it was

"""
#  SKIN TYPE FROM SERPER - HUMAN-COMMENTED VERSION
#
# This is the same search-and-extraction logic as the supplied script, with plain,
# human comments added so the workflow is easier to explain in a viva.
#
# The original API keys have deliberately been removed. They appeared in the
# uploaded file and should be revoked/rotated before this script is used again.
#
# One very important point:
#     This file does NOT know the official brand domain before it searches.
#     It does NOT use brand_domains.json and it does NOT build a site: query.
#
# Instead, it searches:
#     <brand> <product name> skin type
#
# Then, after Serper returns URLs, tier_of() checks whether the cleaned brand name
# appears inside a returned hostname. If it does, that result is treated as the
# manufacturer's website.
#
# This means this file is the earlier serper_skintype.py pass. The later
# serper_direct.py shown in the screenshot is a different script that already had
# a brand-domain cache and could therefore build site:<domain> queries.
#
import os
import re
import csv
import json
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# -----------------------------------------------------------------------------
# SERPER KEYS
# -----------------------------------------------------------------------------
# Put valid replacement keys here before running the script.
#
# The program starts with the first key. If Serper reports that the key can no
# longer be used, retire_key() moves to the next one and retries the same query.
#
# The real keys from the uploaded file are intentionally not reproduced here.
SERPER_KEYS = [
    'PASTE_KEY_1_HERE',
    # 'PASTE_KEY_2_HERE',
]


# -----------------------------------------------------------------------------
# FILES AND RUN SETTINGS
# -----------------------------------------------------------------------------
DATASET = 'SKINCARE_DATASET.csv'
OUT = 'serper_skintype_results.csv'

# Six products can be processed at the same time.
WORKERS = 6

# Even though Serper returns ten search results, the script opens at most three
# accepted pages for one product. Search snippets are checked before pages are
# opened, so some products may require zero page downloads.
PAGES = 3

# Stop waiting after 15 seconds for either Serper or a source page.
TIMEOUT = 15

# False means search every input row. True means search only rows whose existing
# skin_type is empty and which are not already marked as a universal claim.
ONLY_MISSING = False


# These headers make ordinary source-page requests resemble a normal browser
# request. They are not used for the Serper POST request, which has its own API
# headers inside serper().
HEAD = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
}


# These are the columns written for every searched product. Keeping the quote,
# URL, source, tier and rule beside the final label makes the result traceable.
FIELDS = [
    'product_id',
    'brand',
    'name',
    'skin_type',
    'sensitivity',
    'universal_claim',
    'skin_type_tier',
    'skin_type_authority',
    'skin_type_source',
    'skin_type_rule',
    'skin_type_quote',
    'skin_type_url',
    'search_rank',
    'pages_opened',
    'status',
]


# -----------------------------------------------------------------------------
# DOMAIN POLICY
# -----------------------------------------------------------------------------
# A returned URL is not trusted just because Google ranked it. The hostname has
# to pass this policy first.

# Social media, marketplaces and general user-content sites are rejected.
BLOCK = re.compile(
    r'(instagram|facebook|tiktok|reddit|youtube|pinterest|lemon8|quora|'
    r'twitter|x\.com|ebay|aliexpress|etsy|wish\.com|dhgate|alibaba|'
    r'tripadvisor|linkedin|blogspot|wordpress\.com|medium\.com)',
    re.I,
)

# These known shop names are accepted as tier 2 retailers.
RETAILER = re.compile(
    r'(sephora|ulta|boots|douglas|lookfantastic|cultbeauty|dermstore|'
    r'feelunique|notino|amazon|walmart|target|superdrug|beautybay|'
    r'yesstyle|stylevana|oliveyoung|jolse|iherb|sokoglam|'
    r'skinsociety|sohaticare|feel22|nexuscare|zeinacare|mazenonline)',
    re.I,
)

# These sites are accepted as tier 3 analysis sources.
ANALYSIS = re.compile(
    r'(incidecoder|skincarisma|cosdna|beautypedia|paulaschoice)',
    re.I,
)


# -----------------------------------------------------------------------------
# SKIN-TYPE WORDS AND EXTRACTION PATTERNS
# -----------------------------------------------------------------------------

# The keys are words the parser looks for. The values are the normalised labels
# written to the output file.
#
# Notice two deliberate assumptions in the original logic:
#   - the word "oil" maps to Oily;
#   - the word "acne" also maps to Oily.
TYPE_WORDS = {
    'dry': 'Dry',
    'oily': 'Oily',
    'oil': 'Oily',
    'combination': 'Combination',
    'combo': 'Combination',
    'normal': 'Normal',
    'acne': 'Oily',
}


# Phrases such as "all skin types" are stored as universal claims instead of a
# specific Dry/Oily/Normal/Combination classification.
UNIVERSAL = re.compile(
    r'\b(all skin types?|every skin type|any skin type|universal)\b',
    re.I,
)


# These patterns look for a label-like field, for example:
#     Skin Type: Dry, Sensitive
#
# The second pattern tries to recognise the same idea inside an HTML table.
FIELD_PAT = [
    re.compile(
        r'skin[\s_-]*type[^a-z0-9]{0,4}\s*[:\-]\s*([A-Za-z ,/&+-]{3,60})',
        re.I,
    ),
    re.compile(
        r'<t[hd][^>]*>\s*skin\s*type\s*</t[hd]>\s*'
        r'<t[hd][^>]*>\s*([^<]{3,60})',
        re.I | re.S,
    ),
]


# This is the stronger sentence rule. It matches wording such as:
#     suitable for dry skin
#     formulated for oily skin
#     ideal for combination skin
#     made for sensitive skin
#
# "good" is not in this particular pattern.
SUIT_PAT = re.compile(
    r'\b(?:suitable|suited|recommended|formulated|designed|ideal|perfect|great|made)'
    r'\s+(?:for|to)\s+([a-z ,/&+-]{3,70}?)\s*skin\b',
    re.I,
)


# This is the benefit-style rule. It matches wording such as:
#     good for dry skin
#     works for dry skin
#     beneficial for oily skin
#
# It does NOT include the word "used". Therefore "used for dry skin" does not
# match this pattern.
#
# Important limitation of the original code: it does not test for negation.
# Consequently, "not good for dry skin" still contains the substring
# "good for dry skin" and would incorrectly be accepted as Dry.
BENEFIT_PAT = re.compile(
    r'\b(?:good|great|works?|helps?|benefits?|targets?|treats?|effective|beneficial)'
    r'\s+(?:for|on|with)?\s*([a-z ,/&+-]{3,70}?)\s*skin\b',
    re.I,
)


def n_types(p):
    """Count how many main skin-type ideas appear in a piece of text."""

    t = str(p).lower()
    return sum(
        bool(re.search(r'\b' + w, t))
        for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv')
    )


def parse_types(text):
    """
    Convert the words inside a matched phrase into the dataset labels.

    Examples:
        "dry skin"              -> ("Dry", "")
        "oily sensitive skin"  -> ("Oily", "Sensitive")
        "dry and oily skin"    -> ("Combination", "")

    Sensitivity is kept separately from the oil/dry/normal axis.
    """

    t = str(text).lower()

    # Build a set of every normalised type word found in the text.
    f = {
        label
        for word, label in TYPE_WORDS.items()
        if re.search(r'\b' + re.escape(word), t)
    }

    # "Sensitive" is detected separately, even when no dry/oily type is found.
    sens = 'Sensitive' if re.search(r'\bsensitiv', t) else ''

    # If both dry and oily are named, the original code normalises that pair to
    # Combination rather than saving two separate labels.
    if 'Dry' in f and 'Oily' in f:
        return 'Combination', sens

    if 'Combination' in f:
        return 'Combination', sens

    # If several remaining labels somehow occur, this order decides the winner.
    for label in ('Oily', 'Dry', 'Normal'):
        if label in f:
            return label, sens

    return '', sens


def sentence(flat, a, b):
    """Try to recover the complete sentence surrounding a regex match."""

    # Look backward for the latest sentence/list separator before the match.
    i = max(
        flat.rfind('.', 0, a),
        flat.rfind('|', 0, a),
        flat.rfind('•', 0, a),
        0,
    )

    # Look forward for the next full stop or pipe. If neither exists, use the
    # remainder of the text.
    j = min(
        [x for x in (flat.find('.', b), flat.find('|', b)) if x != -1]
        or [len(flat)]
    )

    return flat[i:j + 1].strip(' .|•').strip()


def build(phrase, quote, strength, rule):
    """
    Turn one matched phrase into the small record later written to the CSV.

    The strength argument is passed by extract(), but the original function
    never stores or uses it. The output records only the human-readable rule
    name, such as "declared field" or "ingredient benefit".
    """

    # If four or more main types are named, or the wording explicitly says
    # "all skin types", treat it as a universal marketing claim.
    if (
        n_types(phrase) >= 4
        or n_types(quote) >= 4
        or UNIVERSAL.search(str(phrase))
        or UNIVERSAL.search(str(quote))
    ):
        return {
            'skin_type': '',
            'sensitivity': '',
            'universal_claim': '1',
            'skin_type_rule': rule + ' (all skin types)',
            'skin_type_quote': quote[:220],
        }

    # Otherwise, parse the specific dry/oily/normal/combination and sensitivity
    # words found inside the phrase.
    st, sn = parse_types(phrase)

    # A regex may match grammatically while containing no recognised type word.
    # In that case, ignore this match and keep looking.
    if not (st or sn):
        return None

    return {
        'skin_type': st,
        'sensitivity': sn,
        'universal_claim': '',
        'skin_type_rule': rule,
        'skin_type_quote': quote[:220],
    }


def extract(text):
    """
    Search one snippet or webpage for an acceptable skin-type statement.

    The order matters:
        1. declared fields are checked first;
        2. explicit suitability wording is checked second;
        3. benefit wording is checked last.

    The first usable match is returned immediately.
    """

    # Remove script/style blocks, then collapse repeated whitespace. Other HTML
    # tags are not generally removed here, which explains why some older quotes
    # could still contain markup.
    flat = re.sub(
        r'\s+',
        ' ',
        re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', text),
    )

    # Strongest option: a page explicitly labels a Skin Type field.
    for pat in FIELD_PAT:
        m = pat.search(flat)
        if m:
            v = m.group(1).strip(' .,:;-')
            if len(v) <= 60:
                result = build(
                    v,
                    flat[max(0, m.start() - 20):m.end() + 20].strip(),
                    1,
                    'declared field',
                )
                if result:
                    return result

    # Next, try suitability wording, followed by benefit wording.
    for pat, strength, rule in (
        (SUIT_PAT, 2, 'suitability sentence'),
        (BENEFIT_PAT, 3, 'ingredient benefit'),
    ):
        for m in pat.finditer(flat):
            sen = sentence(flat, m.start(), m.end())

            # If sentence() captured an unusually long block, take a smaller
            # window around the match instead.
            if len(sen) > 400:
                sen = flat[max(0, m.start() - 120):m.end() + 160]

            result = build(sen, sen, strength, rule)
            if result:
                return result

    # Nothing in this text matched the approved wording rules.
    return None


# -----------------------------------------------------------------------------
# HTTP SESSION AND API-KEY STATE
# -----------------------------------------------------------------------------

# This session is reused when opening result pages. Serper requests themselves
# use requests.post() directly inside serper().
S = requests.Session()
S.headers.update(HEAD)

# Shared state used by the concurrent workers:
#   _key_i    = which Serper key is currently active
#   _dead     = keys already retired
#   _key_lock = prevents two threads changing the key index simultaneously
#   _stop     = tells main() that every key is exhausted
_key_i = 0
_dead = set()
_key_lock = threading.Lock()
_stop = threading.Event()


def current_key():
    """Return the currently active key safely across worker threads."""

    with _key_lock:
        return SERPER_KEYS[_key_i] if _key_i < len(SERPER_KEYS) else None


def retire_key(k, why):
    """Mark one key unusable and move the shared index to the next key."""

    global _key_i

    with _key_lock:
        # Another worker may already have retired the same key.
        if k in _dead:
            return

        _dead.add(k)

        if _key_i < len(SERPER_KEYS) and SERPER_KEYS[_key_i] == k:
            _key_i += 1
            left = len(SERPER_KEYS) - _key_i

            print(
                f'\n  key ...{k[-6:]} is finished ({why}).  '
                f'{left} key(s) left.'
                if left
                else f'\n  key ...{k[-6:]} is finished ({why}).  NO KEYS LEFT.'
            )


def bkey(b):
    """
    Make a simplified comparison form of a brand name.

    Example:
        "Paula's Choice" -> "paulaschoice"
    """

    return re.sub(r'[^a-z0-9]', '', str(b).lower())


def serper(query):
    """
    Send one query to Serper and return Google's organic results as tuples:
        (url, title, snippet)

    This function does not decide any skin type. It only performs retrieval.

    The original code treats HTTP 400, 401, 402, 403 and 429 alike and retires
    the key. That is broad: some of those statuses can represent authentication,
    permission, malformed-request or rate-limit problems rather than exhausted
    credits.
    """

    for _ in range(len(SERPER_KEYS) + 1):
        k = current_key()

        if not k:
            _stop.set()
            return [], 'no keys left'

        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers={
                    'X-API-KEY': k,
                    'Content-Type': 'application/json',
                },
                data=json.dumps({'q': query, 'num': 10}),
                timeout=TIMEOUT,
            )
        except Exception:
            return [], 'network error'

        if response.status_code in (400, 401, 402, 403, 429):
            retire_key(k, f'HTTP {response.status_code}')
            continue

        if response.status_code != 200:
            return [], response.status_code

        try:
            payload = response.json()
        except Exception:
            return [], 'bad json'

        # Only organic results are used. Other Serper sections are ignored.
        return [
            (
                item.get('link', ''),
                item.get('title', ''),
                item.get('snippet', ''),
            )
            for item in payload.get('organic', [])
        ], 200

    return [], 'all keys exhausted'


def tier_of(url, brand):
    """
    Decide whether a returned hostname is trusted and assign its evidence tier.

    This is where this script recognises a possible manufacturer website. The
    script did not know the brand domain before searching.
    """

    # Pull only the hostname from a normal absolute URL.
    host = url.split('/')[2].lower() if '://' in url else ''

    # Missing and explicitly blocked hostnames are discarded.
    if not host or BLOCK.search(host):
        return 0, ''

    # Example:
    #   brand = "Paula's Choice"     -> paulaschoice
    #   host  = "paulaschoice.com"  -> paulaschoicecom
    # Since paulaschoice appears inside paulaschoicecom, it becomes tier 1.
    k = bkey(brand)
    if k and len(k) > 3 and k in re.sub(r'[^a-z0-9]', '', host):
        return 1, 'manufacturer'

    # If it is not recognised as the manufacturer, try the known retailer list.
    if RETAILER.search(host):
        return 2, 'retailer'

    # Finally, try the known analysis-site list.
    if ANALYSIS.search(host):
        return 3, 'analysis'

    # Every unknown domain is rejected in this version.
    return 0, ''


def do(row):
    """Search and process one product row from beginning to end."""

    pid = row['product_id']
    brand = row['brand']
    name = row['name']

    # Begin with an empty output record so every CSV row has the same columns.
    rec = {k: '' for k in FIELDS}
    rec.update(
        product_id=pid,
        brand=brand,
        name=name,
        status='no answer',
        pages_opened='0',
    )

    # This is the exact query used by THIS file.
    # There is no brand-domain cache and no site: restriction here.
    query = f'{brand} {name} skin type'
    results, code = serper(query)

    if code != 200:
        rec['status'] = f'serper {code}'
        return rec

    if not results:
        rec['status'] = 'no search results'
        return rec

    # Keep only results accepted by tier_of(). Results are later sorted so a
    # manufacturer page is considered before a retailer, and a retailer before
    # an analysis site. Within one tier, Google's original rank is preserved.
    ranked = []
    for rank, (url, title, snippet) in enumerate(results, 1):
        tier, authority = tier_of(url, brand)
        if tier:
            ranked.append((tier, rank, url, title, snippet, authority))

    ranked.sort(key=lambda x: (x[0], x[1]))

    if not ranked:
        rec['status'] = 'all results were blocked domains'
        return rec

    opened = 0

    # Only the first PAGES accepted/ranked results are considered.
    for tier, rank, url, title, snippet, authority in ranked[:PAGES]:
        # First try the snippet already returned by Serper. This does not require
        # a second Serper query or a source-page download.
        hit = extract(snippet) if snippet else None

        if not hit:
            # The snippet was insufficient, so try to open the real result page.
            opened += 1

            try:
                response = S.get(url, timeout=TIMEOUT)

                if response.status_code != 200:
                    continue

                # The raw HTML must contain the cleaned full brand name somewhere
                # within its first 200,000 characters. This check can reject real
                # pages when a brand is written differently on the page.
                cleaned_html = re.sub(
                    r'[^a-z0-9]',
                    '',
                    response.text[:200000].lower(),
                )
                if bkey(brand) not in cleaned_html:
                    continue

                hit = extract(response.text)

            except Exception:
                # A failed page is skipped and the next ranked result is tried.
                continue

        if hit:
            # Add the extracted label/claim and its sentence/rule.
            rec.update(hit)

            # Add the evidence metadata showing who answered and where.
            rec.update(
                skin_type_tier=str(tier),
                skin_type_authority=authority,
                skin_type_source=url.split('/')[2],
                skin_type_url=url,
                search_rank=str(rank),
                status='found',
            )
            break

    rec['pages_opened'] = str(opened)
    return rec


# -----------------------------------------------------------------------------
# MAIN PROGRAM
# -----------------------------------------------------------------------------

def main():
    """Load the dataset, run concurrent searches, resume safely and report."""

    # Placeholder lines containing the word "paste" are not treated as keys.
    keys = [k for k in SERPER_KEYS if k and 'paste' not in k.lower()]

    if not keys:
        print('\n  STOP. Put at least one Serper key in the SERPER_KEYS list')
        print('  near the top of this file, then run again.\n')
        return

    SERPER_KEYS[:] = keys

    print(
        f'{len(keys)} Serper key(s) loaded. '
        f'the script rotates automatically when one runs out.'
    )

    # Read the complete source dataset into memory.
    rows = list(csv.DictReader(open(DATASET, encoding='utf-8')))

    if ONLY_MISSING:
        todo = [
            r
            for r in rows
            if not r.get('skin_type') and r.get('universal_claim') != '1'
        ]
        print(f'ONLY_MISSING is on: {len(todo):,} products still need a value')
        print('set ONLY_MISSING = False to re-search all 7,569')
    else:
        todo = rows
        print(f'searching all {len(todo):,} products')

    # Resume support: if an output row already exists for a product_id, that
    # product is skipped completely on the next run.
    #
    # Important limitation: this also skips rows previously saved as
    # "network error" or "no answer". A transient failure can therefore become
    # permanent unless those rows are removed or the resume logic is changed.
    done = set()
    if os.path.exists(OUT):
        done = {
            r['product_id']
            for r in csv.DictReader(open(OUT, encoding='utf-8'))
        }
        print(f'resuming, {len(done):,} already searched, they will be skipped')

    todo = [r for r in todo if r['product_id'] not in done]

    print(f'{len(todo):,} searches to run, {WORKERS} workers')
    print(f'that is {len(todo):,} of your Serper credits\n')

    # Append to an existing results file or create a new one with a header.
    new = not os.path.exists(OUT)
    f = open(OUT, 'a', newline='', encoding='utf-8')
    writer = csv.DictWriter(f, fieldnames=FIELDS)

    if new:
        writer.writeheader()

    found = 0
    universal_count = 0
    tiers = {}

    # Submit one future for every remaining product. as_completed() gives each
    # finished result back as soon as it is ready, regardless of input order.
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(do, row): row for row in todo}

        for i, future in enumerate(as_completed(futures), 1):
            try:
                rec = future.result()
            except Exception as error:
                row = futures[future]
                rec = {k: '' for k in FIELDS}
                rec.update(
                    product_id=row['product_id'],
                    brand=row['brand'],
                    name=row['name'],
                    status='error ' + str(error)[:50],
                )

            # If every key is gone, do not write this row. That way it can be
            # attempted again after replacement keys are added.
            if 'keys' in str(rec['status']).lower():
                continue

            writer.writerow(rec)
            f.flush()

            if rec['skin_type']:
                found += 1
                tier = rec['skin_type_tier']
                tiers[tier] = tiers.get(tier, 0) + 1

            if rec['universal_claim'] == '1':
                universal_count += 1

            if _stop.is_set() and i % 25 == 0:
                print('\n  >>> ALL KEYS ARE OUT OF CREDITS. stopping cleanly.')
                print('  >>> nothing was lost. add a new key and run again to continue.\n')
                break

            if i % 25 == 0 or i == len(todo):
                print(
                    f'  {i:6,}/{len(todo):,}  '
                    f'skin type {found:,} ({100 * found / i:.0f}%)  '
                    f'all-types {universal_count:,}  '
                    f'brand {tiers.get("1", 0):,} '
                    f'shop {tiers.get("2", 0):,} '
                    f'analysis {tiers.get("3", 0):,}  '
                    f'| {rec["brand"][:14]:14s} '
                    f'{rec["skin_type"] or rec["status"][:16]}'
                )

    f.close()

    # Re-read the complete accumulated output so the final statistics include
    # both this run and any rows written during earlier resumed runs.
    results = list(csv.DictReader(open(OUT, encoding='utf-8')))
    n = len(results)
    got = [r for r in results if r['skin_type']]
    universal_rows = [r for r in results if r['universal_claim'] == '1']

    print('\n' + '=' * 66)
    print(f'  searched                {n:,}')
    print(f'  real skin type          {len(got):,}  ({100 * len(got) / n:.1f}%)')
    print(
        f'  "all skin types"        {len(universal_rows):,}  '
        f'({100 * len(universal_rows) / n:.1f}%)  recorded as a claim'
    )
    print(f'  nothing usable          {n - len(got) - len(universal_rows):,}')

    print('\n  WHO ANSWERED  (blocked domains never used)')
    for tier, label in (
        ('1', 'the brand itself'),
        ('2', 'a retailer'),
        ('3', 'an analysis site'),
    ):
        count = sum(1 for r in got if r['skin_type_tier'] == tier)
        if count:
            print(
                f'     tier {tier}  {label:22s}{count:6,}  '
                f'({100 * count / len(got):.1f}%)'
            )

    print('\n  TOP SOURCES')
    from collections import Counter

    for domain, count in Counter(
        r['skin_type_source'] for r in got
    ).most_common(12):
        print(f'     {domain:34s}{count:5,}')

    print(f'\nwrote {OUT}')
    print('next:  py serper_apply.py')


if __name__ == '__main__':
    main()
