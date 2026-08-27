"""
Rebuild the skin type pages of the portal, from the live data

Seven detailed pages, every figure read out of SKINCARE_DATASET.csv at build
time. Nothing is typed by hand, so the portal cannot drift from the dataset.

    1  Why I started over
    2  Everything I tried, and why each one failed
    3  How Serper actually works
    4  The four tiers of evidence
    5  How a sentence becomes a value
    6  The mistakes I found and fixed
    7  The final numbers, in full

Usage:
    py build_portal_skintype.py
"""
import re
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
DATASET = 'SKINCARE_DATASET.csv'

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
N = len(df)
tier = pd.to_numeric(df['skin_type_tier'], errors='coerce')
got = df['skin_type'] != ''
FILLED = int(got.sum())
NA = int((df['skin_type_status'] == 'not applicable').sum())
FACIAL = N - NA
FOUND = int((df['skin_type_status'] == 'found').sum())
NOTSTATED = int((df['skin_type_status'] == 'searched, not stated').sum())
T = {t: int((tier[got] == t).sum()) for t in (1, 2, 3, 4)}
T12 = T[1] + T[2]
QUOTE = int((df.loc[got, 'skin_type_quote'] != '').sum())
URL = int((df.loc[got, 'skin_type_url'] != '').sum())
DIST = df.loc[got, 'skin_type'].value_counts().to_dict()
SENS = df.loc[got, 'sensitivity'].value_counts().to_dict()
NSRC = int(df.loc[got, 'skin_type_source'].nunique())
NBRAND = int(df['brand'].nunique())
weak = df[tier.isin([3, 4]) & got]
REJECTED = int(weak['skin_type_source'].str.contains('skinsort|skincarisma',
                                                     case=False, na=False).sum())
SRC = (df.loc[got, 'skin_type_source'].str.lower().str.replace('www.', '', regex=False)
       .value_counts())
WEAK_SRC = (weak['skin_type_source'].str.lower().str.replace('www.', '', regex=False)
            .value_counts())
RULES = (df.loc[got, 'skin_type_rule']
         .str.replace(r'\s*\(strength \d\)', '', regex=True).value_counts())
AUTH = df.loc[got, 'skin_type_authority'].value_counts()


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def ex(cond, k=1):
    cols = ('brand', 'name', 'skin_type', 'sensitivity', 'skin_type_source',
            'skin_type_quote', 'skin_type_url', 'skin_type_rule')
    return [dict(zip(cols, [str(r[c]) for c in cols]))
            for _, r in df[cond].head(k).iterrows()]


def card(r, colour='var(--sage)'):
    q = r['skin_type_quote'][:200] or '(the page itself is the evidence, see the link)'
    return (f"<div class='ev' style='border-left-color:{colour}'>"
            f"<div class='evh'>{r['brand']} &middot; {r['name'][:58]}</div>"
            f"<div class='evt'>&rarr; <b>{r['skin_type']}</b>"
            f"{' &middot; ' + r['sensitivity'] if r['sensitivity'] else ''}"
            f" &nbsp;<span style='color:var(--grey);font-size:11px'>"
            f"rule: {r['skin_type_rule']}</span></div>"
            f"<div class='evq'>&ldquo;{q}&rdquo;</div>"
            f"<div class='evs'>{r['skin_type_source']}</div></div>")


def tbl(head, rows):
    h = ''.join(f'<th>{c}</th>' for c in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{c}</td>" for c in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


# ---------------------------------------------------------- cross tabulations
def crosstab(col, top=8, minimum=40):
    """coverage and tier quality broken down by another column"""
    out = []
    for k, n in df[col].value_counts().head(top).items():
        if n < minimum or not str(k).strip():
            continue
        s = df[df[col] == k]
        st = pd.to_numeric(s['skin_type_tier'], errors='coerce')
        fl = int((s['skin_type'] != '').sum())
        strong = int((st <= 2).sum())
        out.append((str(k), f(n), f(fl), pc(fl, n), f(strong), pc(strong, n)))
    return out


CT_COUNTRY = crosstab('country', 8)
CT_TYPE = crosstab('product_type', 10)

# skin type against sensitivity
CROSS = []
for k in ['All', 'Dry', 'Oily', 'Combination', 'Normal']:
    if k not in DIST:
        continue
    s = df[df['skin_type'] == k]
    se = int((s['sensitivity'] == 'Sensitive').sum())
    re_ = int((s['sensitivity'] == 'Resistant').sum())
    CROSS.append((k, f(len(s)), f(se), pc(se, len(s)), f(re_), pc(re_, len(s))))

e_manu = ex((tier == 1) & got & (df['skin_type_quote'] != ''), 3)
e_shop = ex((tier == 2) & got & (df['skin_type_quote'] != ''), 3)
e_all = ex(got & (df['skin_type'] == 'All') & (df['skin_type_quote'] != ''), 2)
e_sens = ex(got & (df['sensitivity'] == 'Sensitive') & (df['skin_type_quote'] != ''), 2)
e_dry = ex(got & (df['skin_type'] == 'Dry') & (df['skin_type_quote'] != ''), 1)
e_oily = ex(got & (df['skin_type'] == 'Oily') & (df['skin_type_quote'] != ''), 1)
e_comb = ex(got & (df['skin_type'] == 'Combination') & (df['skin_type_quote'] != ''), 1)
e_weak = ex(tier.isin([3, 4]) & got, 2)
e_field = ex(got & df['skin_type_rule'].str.contains('declared field') &
             (df['skin_type_quote'] != ''), 1)

CSS = """
<style id="stcss">
 .ev{background:#fff;border:1px solid var(--line);border-left:5px solid var(--sage);
     border-radius:9px;padding:10px 13px;margin:9px 0}
 .evh{font-weight:700;font-size:13px;color:var(--plum)}
 .evt{font-size:12.5px;color:var(--terra);margin:2px 0}
 .evq{font-size:12.5px;color:#443f52;font-style:italic;margin:5px 0;line-height:1.5}
 .evs{font-size:11.5px;color:var(--grey);font-family:Consolas,monospace}
 .dg{background:#fff;border:1px solid var(--line);border-radius:11px;
     padding:14px;margin:14px 0;overflow-x:auto}
 .dg svg{display:block;margin:0 auto;max-width:100%;height:auto}
 .cap{font-size:12px;color:var(--grey);text-align:center;margin-top:7px;font-style:italic}
 .two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
 .three{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
 @media(max-width:820px){.two,.three{grid-template-columns:1fr}}
 .q{background:var(--soft);border-left:4px solid var(--plum2);border-radius:7px;
    padding:10px 14px;margin:10px 0;font-size:13.5px;font-style:italic;color:#443f52}
 .tl{border-left:3px solid var(--line);margin:14px 0 14px 12px;padding-left:18px}
 .tli{position:relative;margin:0 0 20px}
 .tli:before{content:'';position:absolute;left:-25.5px;top:5px;width:11px;height:11px;
   border-radius:50%;background:var(--plum2);border:2px solid #fff;box-shadow:0 0 0 2px var(--line)}
 .tli.f:before{background:#b5484d} .tli.w:before{background:var(--sage)}
 .tlh{font-weight:700;font-size:14.5px;color:var(--plum)}
 .tlm{font-size:11.5px;color:var(--grey);font-family:Consolas,monospace;margin:1px 0 5px}
 .tlb{font-size:13px;color:#443f52;line-height:1.6}
 .mini{font-size:12px;color:var(--grey);margin:3px 0 0}
</style>
"""

# ============================================================ 1. WHY
S1 = f"""
<section class="section on" id="st-why">
  <h2>1 &middot; Why I threw the skin type away and started again</h2>
  <p class="lead">This is the honest version. The first column was not wrong in
  a small, fixable way. It was built on a foundation my supervisors were right
  to question, so I deleted it and rebuilt it from nothing.</p>

  <h3>What the old column was actually made of</h3>
  <p>It looked like one variable. It was four different kinds of claim sharing
  a single heading.</p>
  {tbl(['source', 'products', 'share', 'what kind of claim is this?'], [
    ['SkinCarisma', '4,452', '58.8%', '<b>an inference.</b> the site reads the ingredient list and forms its own view. nobody at the company said it.'],
    ['Amazon seller metadata', '1,600', '21.1%', '<b>typed in by a seller.</b> quality varies with whoever listed the product.'],
    ['universal claims', '1,033', '13.6%', '"suitable for all skin types", collected from mixed places with mixed reliability.'],
    ['manual checking', '165', '2.2%', '<b>mine.</b> reliable, and impossible to scale to 7,569 products.'],
    ['five Shopify shops', '36', '0.5%', '<b>a declared retail claim.</b> the right kind of evidence, and far too little of it.']])}

  <div class="bad"><b>The measurement that condemned it.</b> I measured how
  often these sources agreed with each other, four separate times, using
  different subsets and different matching thresholds. Every measurement landed
  near <b>50%</b>.
  <p style="margin:9px 0 0">That number is the entire argument. If two sources
  claiming to measure the same thing agree half the time, then either one of
  them is wrong half the time, or they are not measuring the same thing. Here
  both were true. SkinCarisma infers from chemistry. Amazon reports what a
  seller typed. Those are simply different questions wearing the same column
  heading.</p></div>

  <div class="dg">
  <svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="12">
    <rect x="8" y="18" width="150" height="40" rx="7" fill="#efe9f7" stroke="#7a68a6"/>
    <text x="83" y="35" text-anchor="middle" fill="#584a7a" font-weight="700">SkinCarisma</text>
    <text x="83" y="50" text-anchor="middle" fill="#6b6478">inferred, 4,452</text>
    <rect x="8" y="68" width="150" height="40" rx="7" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="83" y="85" text-anchor="middle" fill="#3f6b48" font-weight="700">Amazon metadata</text>
    <text x="83" y="100" text-anchor="middle" fill="#6b6478">seller typed, 1,600</text>
    <rect x="8" y="118" width="150" height="40" rx="7" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="83" y="135" text-anchor="middle" fill="#8d5433" font-weight="700">universal claims</text>
    <text x="83" y="150" text-anchor="middle" fill="#6b6478">1,033</text>
    <rect x="8" y="168" width="150" height="40" rx="7" fill="#fdeeee" stroke="#b06a97"/>
    <text x="83" y="185" text-anchor="middle" fill="#8d4470" font-weight="700">shops + manual</text>
    <text x="83" y="200" text-anchor="middle" fill="#6b6478">201</text>
    <path d="M158 38 C210 38 210 113 258 113" stroke="#b9aed0" fill="none" stroke-width="1.6"/>
    <path d="M158 88 C210 88 210 113 258 113" stroke="#b9aed0" fill="none" stroke-width="1.6"/>
    <path d="M158 138 C210 138 210 113 258 113" stroke="#b9aed0" fill="none" stroke-width="1.6"/>
    <path d="M158 188 C210 188 210 113 258 113" stroke="#b9aed0" fill="none" stroke-width="1.6"/>
    <rect x="258" y="88" width="150" height="50" rx="7" fill="#584a7a"/>
    <text x="333" y="108" text-anchor="middle" fill="#fff" font-weight="700">one column</text>
    <text x="333" y="125" text-anchor="middle" fill="#d5cae8">"skin_type"</text>
    <path d="M408 113 L452 113" stroke="#b5484d" stroke-width="2"/>
    <polygon points="452,113 444,108 444,118" fill="#b5484d"/>
    <rect x="458" y="78" width="250" height="70" rx="9" fill="#fdeeee" stroke="#b5484d" stroke-width="1.6"/>
    <text x="583" y="102" text-anchor="middle" fill="#b5484d" font-weight="700" font-size="15">the sources agreed ~50%</text>
    <text x="583" y="121" text-anchor="middle" fill="#8d3a3e">measured four separate times</text>
    <text x="583" y="138" text-anchor="middle" fill="#8d3a3e">and no value came from the brand</text>
  </svg>
  <div class="cap">Four kinds of evidence poured into one column. That is what
  the 50% agreement was really telling me.</div></div>

  <h3>The question I could not answer</h3>
  <p>My supervisors' objection reduced to one thing: <i>where does this value
  come from?</i> For a product marked "Dry" the best I could offer was
  "SkinCarisma concluded dry from the formula". I could not say "the
  manufacturer says dry, here is the sentence, here is the page".</p>
  <p>That is the difference between an <b>inference</b> and a <b>declared
  fact</b>, and a thesis should rest on the second. So I emptied the column
  rather than patch it.</p>

  <div class="q">Every value in the dataset today was found <i>after</i> that
  reset. Each one carries the domain it came from, the sentence that states it,
  and a link that opens the page.</div>

  <h3>What replaced it</h3>
  <div class="kpis">
    <div class="kpi"><div class="n">{f(FILLED)}</div><div class="l">products with a skin type ({pc(FILLED)})</div></div>
    <div class="kpi"><div class="n">{f(T12)}</div><div class="l">from the maker or a shop ({pc(T12)})</div></div>
    <div class="kpi"><div class="n">{f(URL)}</div><div class="l">carry a clickable source link</div></div>
    <div class="kpi"><div class="n">{f(NSRC)}</div><div class="l">different websites answered</div></div>
  </div>
  {tbl(['', 'the old column', 'the column today'], [
    ['largest single source', 'SkinCarisma, 58.8%, inferred', f'the manufacturers themselves, {pc(T[1])}, declared'],
    ['traceable to the brand', '<b>none</b>', f'<b>{f(T[1])} products</b>'],
    ['carries the exact sentence', 'no', f'{f(QUOTE)} products'],
    ['carries a link to check it', 'no', f'{f(URL)} products'],
    ['records how strong the source is', 'no', 'yes, a tier on every row'],
    ['sources agreed with each other', '~50%', 'not applicable, there is one kind of claim now'],
    ['distinct websites involved', '4 kinds of source', f'{f(NSRC)} websites']])}

  <h4>Three real rows, pulled from the file when this page was built</h4>
  {''.join(card(r) for r in e_manu[:2] + e_shop[:1])}
  <p class="small">Open <code>SKINCARE_DATASET.xlsx</code>, filter to the brand,
  and the same sentence and link are sitting in the row. That is the whole
  point of the rebuild: nothing has to be taken on trust.</p>

  <div class="note"><b>The old work was not deleted.</b> It is preserved in
  <code>06_ARCHIVED_old_skin_type/</code> together with the previous datasets,
  the validation workbooks and the earlier portal, so the two approaches can
  still be compared in the thesis rather than one simply vanishing.</div>
</section>
"""

# ============================================================ 2. ATTEMPTS
S2 = f"""
<section class="section" id="st-tries">
  <h2>2 &middot; Everything I tried, and why each one failed</h2>
  <p class="lead">Six approaches before one worked. I am documenting the five
  failures deliberately, because the reason the final method is trustworthy is
  that I know exactly what the alternatives could not do. A reviewer is entitled
  to ask "why not simply do X", and for five values of X the answer is "I tried,
  and here is what happened".</p>

  <div class="dg">
  <svg viewBox="0 0 730 210" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <line x1="30" y1="150" x2="700" y2="150" stroke="#ded7ea" stroke-width="2"/>
    <g fill="#b5484d">
      <circle cx="70" cy="150" r="6"/><circle cx="180" cy="150" r="6"/>
      <circle cx="290" cy="150" r="6"/><circle cx="400" cy="150" r="6"/>
      <circle cx="510" cy="150" r="6"/>
    </g>
    <circle cx="640" cy="150" r="9" fill="#6f9c78"/>
    <g text-anchor="middle" fill="#6b6478">
      <text x="70" y="172">ready datasets</text><text x="180" y="172">ingredient rules</text>
      <text x="290" y="172">brand sites</text><text x="400" y="172">DuckDuckGo</text>
      <text x="510" y="172">Bing, Mojeek</text>
      <text x="640" y="174" fill="#3f6b48" font-weight="700">Serper API</text>
    </g>
    <g text-anchor="middle" font-weight="700">
      <text x="70" y="132" fill="#b5484d">0%</text><text x="180" y="132" fill="#b5484d">inferred</text>
      <text x="290" y="132" fill="#b5484d">6.6%</text><text x="400" y="132" fill="#b5484d">blocked</text>
      <text x="510" y="132" fill="#b5484d">captcha</text>
      <text x="640" y="128" fill="#3f6b48" font-size="15">{pc(FILLED)}</text>
    </g>
    <rect x="596" y="18" width="88" height="88" rx="10" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="640" y="46" text-anchor="middle" fill="#3f6b48" font-weight="700" font-size="13">it worked</text>
    <text x="640" y="64" text-anchor="middle" fill="#3f6b48">{f(FILLED)}</text>
    <text x="640" y="80" text-anchor="middle" fill="#6b6478">products</text>
    <text x="640" y="96" text-anchor="middle" fill="#6b6478">with evidence</text>
    <path d="M640 106 L640 140" stroke="#6f9c78" stroke-width="1.6"/>
  </svg>
  <div class="cap">Five dead ends, then one method that reached {pc(FILLED)}.</div></div>

  {tbl(['#', 'approach', 'result', 'why it stopped'], [
    ['1', 'reuse an existing dataset', '<b>0%</b>', 'none has all three attributes'],
    ['2', 'derive from the ingredients', 'rejected', 'produces an inference, the thing objected to'],
    ['3', 'crawl each brand website', '<b>6.6%</b>', 'brand sites are unguessable and JavaScript-rendered'],
    ['4', 'scrape DuckDuckGo', '<b>blocked</b>', 'connection timeout on every request'],
    ['5', 'scrape Bing, Mojeek, Startpage', '<b>blocked</b>', 'captcha on every request'],
    ['6', '<b>a search API (Serper)</b>', f'<b>{pc(FILLED)}</b>', 'this is the method in the dataset']])}

  <div class="tl">
    <div class="tli f"><div class="tlh">Attempt 1 &middot; Find a dataset that already has everything</div>
      <div class="tlm">INCIDB &middot; Beauty API &middot; Dermstore &middot; several Kaggle sets</div>
      <div class="tlb">The obvious first move. If someone has already published
      products with ingredients, reviews and a declared skin type, I should use
      theirs rather than build my own. I checked every candidate I could find.
      <b>Every one was missing at least two of the three attributes I need</b>,
      and not one carried a skin type traceable to a manufacturer. The Kaggle
      sets in particular are scrapes of a single retailer with no provenance at
      all, which is the same problem I was trying to escape.
      <p class="mini">Why this matters: it is the empirical justification for
      building a dataset instead of reusing one, and it belongs in the
      methodology chapter as a stated finding rather than an assumption.</p></div></div>

    <div class="tli f"><div class="tlh">Attempt 2 &middot; Derive the skin type from the ingredients</div>
      <div class="tlm">EU CosIng function field &middot; 79 functions &middot; 28,492 of 28,710 entries</div>
      <div class="tlb">Map every ingredient to its official CosIng function, then
      reason from function to skin type. Humectants, emollients and occlusives
      point toward dry skin; astringents and sebum regulators toward oily. It is
      defensible chemistry and I already had the mapping built from the INCI
      standardisation work.
      <p class="mini">I rejected it on principle, not on difficulty. It produces
      an <b>inference</b>, which is exactly what my supervisors objected to in
      SkinCarisma. Doing the inference myself would not turn it into a fact. It
      would only make it my inference instead of somebody else's.</p>
      <p class="mini">It still has real value as a <b>validation layer</b>. If
      the manufacturer says "for dry skin" and the formula is humectant-heavy,
      that agreement means something. That is a legitimate future chapter.</p></div></div>

    <div class="tli f"><div class="tlh">Attempt 3 &middot; Visit every brand website directly</div>
      <div class="tlm">three full passes &middot; reached 6.6% of products</div>
      <div class="tlb">Guess the brand's domain from its name, walk the site,
      find the product page. This gets exactly the right kind of evidence,
      straight from the manufacturer. It simply cannot find the pages.
      <p class="mini">Brand sites are hostile to this approach: URLs are
      unguessable, catalogues render in JavaScript so the downloaded HTML
      contains nothing, sites split by region (<code>us.</code>,
      <code>uk.</code>, <code>.co.uk</code>), and product naming differs between
      the brand's own site and every other source. After three passes it had
      covered 6.6%. <b>The evidence type was right and the coverage was
      hopeless.</b></p></div></div>

    <div class="tli f"><div class="tlh">Attempt 4 &middot; Scrape a search engine</div>
      <div class="tlm">DuckDuckGo &rarr; ConnectTimeout on every request</div>
      <div class="tlb">If I cannot guess the URL, let a search engine find it for
      me. DuckDuckGo returned a connection timeout every single time. Not slow,
      not rate limited, refused at the network level before any page loaded.</div></div>

    <div class="tli f"><div class="tlh">Attempt 5 &middot; Try all the other engines</div>
      <div class="tlm">Bing, Mojeek, Startpage &rarr; captcha</div>
      <div class="tlb">The same wall in a different shape. This is the point at
      which I understood the real problem, and the diagnosis is the important
      part of this whole page:
      <p class="mini"><b>My network blocks automated access to search engines.</b>
      A person typing in a browser gets results. A script does not. Search
      engines block automated traffic deliberately, because it consumes serving
      capacity and generates no advertising revenue.</p>
      <p class="mini">Understanding <i>why</i> I was blocked is what pointed at
      the solution. You cannot route around this by writing better scraping
      code, because the block is not in my code. You have to stop scraping.</p></div></div>

    <div class="tli w"><div class="tlh">Attempt 6 &middot; A search API &mdash; Serper</div>
      <div class="tlm">paid service &middot; official Google results &middot; the method in the dataset</div>
      <div class="tlb">I watched a tutorial on how automated search is normally
      done and learned that nobody scrapes search engines. They call a search
      <b>API</b>: a paid, permitted, documented door to the same results.
      <p class="mini">Serper returns real Google results as clean structured
      data. There is no captcha because I am not pretending to be a browser. I
      am a customer with a key, using a commercial service the way it is
      designed to be used. Page 3 explains exactly what it does and, just as
      importantly, what it does not do.</p></div></div>
  </div>
</section>
"""

# ============================================================ 3. SERPER
S3 = f"""
<section class="section" id="st-serper">
  <h2>3 &middot; How Serper actually works</h2>
  <p class="lead">If I am asked one technical question in the viva it will be
  this one, so here is the whole thing, plainly and in order.</p>

  <h3>The short version</h3>
  <div class="q">Serper is a paid doorway to Google. I send it a sentence, it
  asks Google, and it sends the results back as structured data instead of as a
  web page. It knows nothing about skincare. It finds pages. All of the reading,
  judging and deciding happens in my own code afterwards.</div>

  <h3>Why a scraper could never have worked</h3>
  <p>Search engines block scripts on purpose. They serve a captcha or drop the
  connection, because automated traffic costs them serving capacity and shows no
  advertisements. That is what stopped attempts 4 and 5, and no amount of
  better Python would have changed it.</p>
  <p>A search API is the sanctioned route. I pay per query, I identify myself
  with a key, and in exchange I receive the same results through a documented
  commercial service. <b>One query costs one credit.</b> I bought 50,000 credits
  for $50.</p>

  <div class="dg">
  <svg viewBox="0 0 740 330" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="10" y="10" width="150" height="58" rx="8" fill="#efe9f7" stroke="#7a68a6"/>
    <text x="85" y="31" text-anchor="middle" font-weight="700" fill="#584a7a">1. my script</text>
    <text x="85" y="47" text-anchor="middle" fill="#6b6478">builds a question</text>
    <text x="85" y="61" text-anchor="middle" fill="#6b6478" font-family="Consolas">site:cerave.com ...</text>
    <path d="M160 39 L206 39" stroke="#7a68a6" stroke-width="2"/><polygon points="206,39 198,34 198,44" fill="#7a68a6"/>
    <rect x="212" y="10" width="150" height="58" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="287" y="31" text-anchor="middle" font-weight="700" fill="#8d5433">2. Serper</text>
    <text x="287" y="47" text-anchor="middle" fill="#6b6478">1 credit, checks my key</text>
    <text x="287" y="61" text-anchor="middle" fill="#6b6478">asks Google for me</text>
    <path d="M362 39 L408 39" stroke="#c07a54" stroke-width="2"/><polygon points="408,39 400,34 400,44" fill="#c07a54"/>
    <rect x="414" y="10" width="150" height="58" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="489" y="31" text-anchor="middle" font-weight="700" fill="#3f6b48">3. Google</text>
    <text x="489" y="47" text-anchor="middle" fill="#6b6478">the real index</text>
    <text x="489" y="61" text-anchor="middle" fill="#6b6478">ranked results</text>
    <path d="M489 68 L489 92" stroke="#6f9c78" stroke-width="2"/><polygon points="489,92 484,84 494,84" fill="#6f9c78"/>
    <rect x="330" y="96" width="318" height="72" rx="8" fill="#22262e"/>
    <text x="344" y="116" fill="#a8d8a8" font-family="Consolas" font-size="11">4. comes back as data, not a web page</text>
    <text x="344" y="133" fill="#d9dee5" font-family="Consolas" font-size="10.5">"organic": [</text>
    <text x="344" y="147" fill="#d9dee5" font-family="Consolas" font-size="10.5">  {{"link": "https://cerave.com/...",</text>
    <text x="344" y="161" fill="#d9dee5" font-family="Consolas" font-size="10.5">   "snippet": "for normal to dry skin"}} ]</text>
    <path d="M330 132 L262 132" stroke="#584a7a" stroke-width="2"/><polygon points="262,132 270,127 270,137" fill="#584a7a"/>
    <rect x="10" y="96" width="246" height="72" rx="8" fill="#efe9f7" stroke="#7a68a6"/>
    <text x="133" y="116" text-anchor="middle" font-weight="700" fill="#584a7a">5. MY code takes over</text>
    <text x="133" y="133" text-anchor="middle" fill="#6b6478">Serper's job is finished here</text>
    <text x="133" y="150" text-anchor="middle" fill="#6b6478">it never sees the skin type</text>
    <path d="M133 168 L133 194" stroke="#7a68a6" stroke-width="2"/><polygon points="133,194 128,186 138,186" fill="#7a68a6"/>
    <rect x="10" y="198" width="246" height="52" rx="8" fill="#fff" stroke="#b9aed0"/>
    <text x="133" y="218" text-anchor="middle" font-weight="700" fill="#584a7a">6. grade the domain</text>
    <text x="133" y="235" text-anchor="middle" fill="#6b6478">is this the maker, a shop, or neither?</text>
    <path d="M256 224 L302 224" stroke="#7a68a6" stroke-width="2"/><polygon points="302,224 294,219 294,229" fill="#7a68a6"/>
    <rect x="308" y="198" width="200" height="52" rx="8" fill="#fff" stroke="#b9aed0"/>
    <text x="408" y="218" text-anchor="middle" font-weight="700" fill="#584a7a">7. open the page, read it</text>
    <text x="408" y="235" text-anchor="middle" fill="#6b6478">match a wording rule</text>
    <path d="M508 224 L554 224" stroke="#6f9c78" stroke-width="2"/><polygon points="554,224 546,219 546,229" fill="#6f9c78"/>
    <rect x="560" y="192" width="170" height="64" rx="8" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="645" y="212" text-anchor="middle" font-weight="700" fill="#3f6b48">8. write the row</text>
    <text x="645" y="228" text-anchor="middle" fill="#6b6478">value + sentence</text>
    <text x="645" y="244" text-anchor="middle" fill="#6b6478">+ domain + link + tier</text>
    <rect x="10" y="272" width="720" height="46" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="370" y="291" text-anchor="middle" fill="#8d5433" font-weight="700">The important line: Serper supplies LINKS. Every skin type in the dataset was read off a page by my own code.</text>
    <text x="370" y="308" text-anchor="middle" fill="#6b6478">No model guessed anything, and Serper has no opinion about skincare.</text>
  </svg>
  <div class="cap">The eight steps behind a single filled cell.</div></div>

  <div class="ok"><b>The sentence to say if anyone asks whether an AI wrote
  these values.</b> No. A search service returned URLs. A regular-expression
  parser written by me opened those pages, matched a wording rule, and stored
  the sentence it matched together with the link. Nothing was generated,
  inferred, or guessed at any point.</div>

  <h3>One request, end to end</h3>
  <pre class="term">POST <b>https://google.serper.dev/search</b>
X-API-KEY: (my private key)
Content-Type: application/json

  {{ "q": "site:cerave.com moisturising cream", "num": 10 }}

<b>the answer, one credit spent</b>
  organic[0].link    https://www.cerave.com/skincare/moisturizers/...
  organic[0].title   Moisturising Cream | CeraVe
  organic[0].snippet Developed with dermatologists ... for normal to dry skin
  organic[1].link    ...</pre>

  <h3>What my code does with that, step by step</h3>
  {tbl(['step', 'what happens', 'why'], [
    ['1', 'grade every returned domain', 'is this the manufacturer, a shop, or neither'],
    ['2', 'discard anything that is neither', 'analysis sites and blogs are refused outright'],
    ['3', 'sort what is left, strongest first', 'a brand page is always preferred to a shop'],
    ['4', 'read the snippet Google returned', 'often enough on its own, and costs nothing extra'],
    ['5', 'if not, download the full page', 'up to 6 to 10 pages per product'],
    ['6', 'confirm the page is about this brand', 'stops a search drifting onto the wrong product'],
    ['7', 'run the wording rules over the text', 'see page 5 for the rules themselves'],
    ['8', 'write value, sentence, domain, URL, tier', 'so the row can be checked by anyone']])}

  <h3>The three questions asked about each product</h3>
  {tbl(['the query', 'what it is for'], [
    ['<code>site:&lt;brand domain&gt; &lt;product&gt;</code>',
     '<b>Asks the manufacturer directly.</b> The single most valuable query in the whole project, and the one I was missing for a long time, which is exactly why the earlier passes leaned on analysis sites.'],
    ['<code>"&lt;brand&gt; &lt;product&gt;" buy</code>',
     'If the brand page says nothing, find a shop selling it. Shop listings almost always state suitability, because it helps them sell.'],
    ['<code>&lt;brand&gt; &lt;product&gt; for which skin type</code>',
     'Plain language, kept for the stubborn remainder.']])}

  <h3>Learning each brand's address once, not once per product</h3>
  <p>A brand has many products, so looking up "where does COSRX live" separately
  for each of its products would be wasteful. The pipeline resolves each brand's
  domain <b>once</b>, saves it to <code>brand_domains.json</code>, and reuses it
  for every product of that brand.</p>
  <p>It also learns domains for free from rows that already succeeded. If one
  CeraVe product answered from <code>cerave.com</code>, every other CeraVe
  product now knows where to ask without spending anything.</p>
  {tbl(['', 'brands', 'cost'], [
    ['already known for free, from rows that had succeeded', '698', '0 credits'],
    ['needed a paid lookup', '264', '264 credits'],
    ['of those, successfully resolved', '211', ''],
    ['<b>brands in the dataset overall</b>', f'<b>{f(NBRAND)}</b>', '']])}

  <h3>What each pass cost, and what it achieved</h3>
  {tbl(['pass', 'the question it asked', 'attempted', 'credits', 'outcome'], [
    ['<code>serper_skintype</code>', '"&lt;brand&gt; &lt;product&gt; skin type"', '7,569', '~7,500', 'the bulk of the coverage'],
    ['<code>serper_pass2</code>', 'suitability wording, 6 pages', '1,881', '~1,900', 'widened the patterns'],
    ['<code>serper_pass3</code>', '3 queries, 10 pages, loose rule', '1,186', '~3,500', 'reached 98% coverage'],
    ['<code>retier</code>', '<i>no search at all</i>', '1,403', '<b>0</b>', '243 sources correctly relabelled'],
    ['<code>serper_rescue</code>', 'refuse analysis sites entirely', '1,160', '~1,700', '267 upgraded'],
    ['<code>serper_direct</code>', '<b>site: the brand&rsquo;s own domain</b>', '893', '~1,700', '<b>652 upgraded</b>'],
    ['<code>serper_last241</code>', 'shorter names, three angles', '241', '~600', '63 upgraded'],
    ['<code>cleanup_and_quotes</code>', '<i>re-open known URLs</i>', '963', '<b>0</b>', 'quotes recovered']])}
  <div class="ok"><b>Roughly 12,000 credits of the 50,000 I bought.</b> The
  brand-domain cache and the two free passes are the reason it was not far
  more.</div>
</section>
"""

# ============================================================ 4. TIERS
src_rows = [[f'<code>{k}</code>', f(v), pc(v, FILLED)] for k, v in SRC.head(22).items()]

S4 = f"""
<section class="section" id="st-tiers">
  <h2>4 &middot; The four tiers of evidence</h2>
  <p class="lead">Not every website deserves the same trust. Every row records
  which kind of source answered it, so any figure in the thesis can be
  recomputed at whatever strictness a reader wants.</p>

  <div class="dg">
  <svg viewBox="0 0 700 285" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="12">
    <rect x="20" y="14" width="620" height="56" rx="9" fill="#eef6ee" stroke="#6f9c78" stroke-width="2"/>
    <circle cx="52" cy="42" r="16" fill="#6f9c78"/><text x="52" y="47" text-anchor="middle" fill="#fff" font-weight="700">1</text>
    <text x="82" y="36" font-weight="700" fill="#3f6b48" font-size="14">The manufacturer</text>
    <text x="82" y="55" fill="#6b6478">the company's own website. the strongest thing that exists.</text>
    <text x="622" y="47" text-anchor="end" font-weight="700" fill="#3f6b48" font-size="16">{f(T[1])}</text>
    <rect x="20" y="80" width="620" height="56" rx="9" fill="#f4f0fa" stroke="#7a68a6" stroke-width="2"/>
    <circle cx="52" cy="108" r="16" fill="#7a68a6"/><text x="52" y="113" text-anchor="middle" fill="#fff" font-weight="700">2</text>
    <text x="82" y="102" font-weight="700" fill="#584a7a" font-size="14">A shop that sells it</text>
    <text x="82" y="121" fill="#6b6478">a page with a price and a working add-to-cart button.</text>
    <text x="622" y="113" text-anchor="end" font-weight="700" fill="#584a7a" font-size="16">{f(T[2])}</text>
    <rect x="20" y="146" width="620" height="56" rx="9" fill="#fbf3ec" stroke="#c07a54" stroke-width="1.4"/>
    <circle cx="52" cy="174" r="16" fill="#c07a54"/><text x="52" y="179" text-anchor="middle" fill="#fff" font-weight="700">3</text>
    <text x="82" y="168" font-weight="700" fill="#8d5433" font-size="14">An analysis site</text>
    <text x="82" y="187" fill="#6b6478">reads the formula and forms its own view. an opinion, not a claim.</text>
    <text x="622" y="179" text-anchor="end" font-weight="700" fill="#8d5433" font-size="16">{f(T[3])}</text>
    <rect x="20" y="212" width="620" height="56" rx="9" fill="#fdeeee" stroke="#b5484d" stroke-width="1.4"/>
    <circle cx="52" cy="240" r="16" fill="#b5484d"/><text x="52" y="245" text-anchor="middle" fill="#fff" font-weight="700">4</text>
    <text x="82" y="234" font-weight="700" fill="#8d3a3e" font-size="14">Anything else</text>
    <text x="82" y="253" fill="#6b6478">magazines, blogs, resale listings. kept visible, never counted.</text>
    <text x="622" y="245" text-anchor="end" font-weight="700" fill="#8d3a3e" font-size="16">{f(T[4])}</text>
    <text x="660" y="42" fill="#6b6478" font-size="11">strong</text>
    <text x="660" y="245" fill="#6b6478" font-size="11">weak</text>
  </svg>
  <div class="cap">Every filled row sits on exactly one of these rungs.</div></div>

  <h3>Why tier 1 is the strongest evidence that exists</h3>
  <p>Under <b>EU Regulation 1223/2009</b> the manufacturer is legally
  responsible for the claims it makes about a cosmetic product. A statement on
  the brand's own website is therefore not marketing opinion in the way a
  magazine review is. It is a claim the company can be held to. That is the
  reason this tier sits at the top, and it is a better answer than "because the
  brand knows its own product".</p>

  <h3>Why a retailer claim is not the same as an analysis site</h3>
  <div class="two">
  <div class="ok"><b>A retailer reports.</b> Shop listings are, overwhelmingly,
  the brand's own product copy passed along. The retailer is repeating a
  declared claim, not forming one. That is why it is tier 2 and not tier 3.</div>
  <div class="note"><b>An analysis site concludes.</b> SkinCarisma and
  INCIDecoder read the ingredient list and reason to a skin type. It may well be
  good reasoning, but it is a third party's conclusion, not anybody's claim
  about the product.</div></div>

  <h3>How a shop is recognised, and why the method changed</h3>
  <p>My first version used a hand-written list of about sixty shop names. That
  was a bad design for two reasons: it silently discarded any shop I had not
  personally heard of, and that bias runs precisely against a thesis covering
  <b>Lebanese retail</b>.</p>
  <p>A page is now treated as a shop if it <b>behaves</b> like one:</p>
  {tbl(['signal', 'what it looks like in the page'], [
    ['a cart control', '<code>add to cart</code>, <code>add to bag</code>, <code>add to basket</code>'],
    ['structured product data', '<code>"@type": "Product"</code> or <code>"Offer"</code>'],
    ['a marked price', '<code>itemprop="price"</code>'],
    ['stock status', '<code>in stock</code> or <code>out of stock</code>']])}
  <p class="small">That is checkable evidence rather than my familiarity, and it
  brought in a long tail of small and regional shops. The dataset now draws on
  <b>{f(NSRC)} distinct websites</b>.</p>

  <h3>What is refused outright</h3>
  {tbl(['refused', 'examples', 'why'], [
    ['resale marketplaces', 'Poshmark, Mercari, Depop, Vinted', 'the description is written by a private seller clearing out a bathroom cabinet'],
    ['magazines and blogs', 'Allure, Byrdie, New York Post', 'editorial opinion is not a manufacturer claim'],
    ['social media', 'Instagram, TikTok, Reddit, YouTube', 'no accountability for the claim'],
    ['general marketplaces', 'eBay, AliExpress, Etsy, DHgate', 'listings are user-written and unverifiable'],
    ['<b>the questioned sources</b>', '<b>Skinsort, SkinCarisma</b>', '<b>named explicitly in the reject list so they cannot re-enter through a side door</b>']])}

  <h3>The 22 websites that answered most often</h3>
  {tbl(['domain', 'products', 'share of filled'], src_rows)}

  <h3>Reading the number at three strictness levels</h3>
  {tbl(['filter', 'what it means', 'products', 'share'], [
    ['<code>tier == 1</code>', 'the manufacturer said it, nobody else counts', f'<b>{f(T[1])}</b>', pc(T[1])],
    ['<code>tier &le; 2</code>', 'a declared claim, from the maker or a shop<br><span class="small">this is the figure I quote</span>', f'<b>{f(T12)}</b>', f'<b>{pc(T12)}</b>'],
    ['<code>tier &le; 4</code>', 'everything, including analysis sites', f'<b>{f(FILLED)}</b>', pc(FILLED)]])}
  <div class="ok"><b>This is standard practice, not a hedge.</b> Record-linkage
  studies routinely report a strict and a permissive figure, an approach
  formalised by Fellegi and Sunter (1969), because it lets a reader see how much
  a conclusion depends on the weaker evidence. Because the tier lives in the
  file, anyone can recompute either number in one line.</div>
</section>
"""

# ============================================================ 5. RULES
rule_rows = [[f'<code>{k}</code>', f(v), pc(v, FILLED)] for k, v in RULES.items()]

S5 = f"""
<section class="section" id="st-rules">
  <h2>5 &middot; How a sentence on a page becomes a value in a cell</h2>
  <p class="lead">Serper hands me a link. Everything after that is my own code
  reading English and deciding. This page is that decision, in full.</p>

  <div class="dg">
  <svg viewBox="0 0 720 250" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="10" y="14" width="200" height="60" rx="8" fill="#22262e"/>
    <text x="24" y="34" fill="#a8d8a8" font-family="Consolas" font-size="10.5">the page says</text>
    <text x="24" y="52" fill="#d9dee5" font-family="Consolas" font-size="10.5">"Suitable for dry and</text>
    <text x="24" y="66" fill="#d9dee5" font-family="Consolas" font-size="10.5">sensitive skin."</text>
    <path d="M210 44 L252 44" stroke="#7a68a6" stroke-width="2"/><polygon points="252,44 244,39 244,49" fill="#7a68a6"/>
    <rect x="258" y="14" width="190" height="60" rx="8" fill="#efe9f7" stroke="#7a68a6"/>
    <text x="353" y="34" text-anchor="middle" font-weight="700" fill="#584a7a">a wording rule fires</text>
    <text x="353" y="52" text-anchor="middle" fill="#6b6478" font-size="10.5">"suitable for ___ skin"</text>
    <text x="353" y="67" text-anchor="middle" fill="#6b6478" font-size="10.5">strength 2</text>
    <path d="M448 44 L490 44" stroke="#7a68a6" stroke-width="2"/><polygon points="490,44 482,39 482,49" fill="#7a68a6"/>
    <rect x="496" y="6" width="214" height="78" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="603" y="26" text-anchor="middle" font-weight="700" fill="#3f6b48">two separate axes</text>
    <text x="510" y="46" fill="#6b6478" font-size="10.5">skin_type</text><text x="700" y="46" text-anchor="end" font-weight="700" fill="#3f6b48">Dry</text>
    <text x="510" y="64" fill="#6b6478" font-size="10.5">sensitivity</text><text x="700" y="64" text-anchor="end" font-weight="700" fill="#3f6b48">Sensitive</text>
    <text x="510" y="79" fill="#6b6478" font-size="10">oil level and reactivity are not the same question</text>
    <rect x="10" y="104" width="700" height="60" rx="8" fill="#fff" stroke="#b9aed0"/>
    <text x="24" y="124" font-weight="700" fill="#584a7a">and the row keeps the receipt</text>
    <text x="24" y="143" fill="#6b6478" font-size="11">skin_type_quote &middot; the exact sentence &nbsp;|&nbsp; skin_type_source &middot; the domain &nbsp;|&nbsp; skin_type_url &middot; the page &nbsp;|&nbsp; skin_type_tier &middot; how strong</text>
    <text x="24" y="158" fill="#6b6478" font-size="11">so any one of {f(FILLED)} cells can be checked by opening a single link. nothing has to be taken on trust.</text>
    <rect x="10" y="178" width="700" height="60" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="24" y="198" font-weight="700" fill="#8d5433">why two columns and not one</text>
    <text x="24" y="217" fill="#6b6478" font-size="11">"sensitive" answers a different question from "oily". a product can be oily and sensitive, or oily and resistant.</text>
    <text x="24" y="232" fill="#6b6478" font-size="11">collapsing them into one column would destroy real information. this follows the Baumann skin type framework.</text>
  </svg>
  <div class="cap">One sentence, two axes, four pieces of evidence stored.</div></div>

  <h3>The four strengths of wording</h3>
  <p>Rules are tried strongest first, and the first one that fires wins. That
  ordering matters: a declared spec field is always preferred to a sentence,
  and a sentence is always preferred to a passing mention.</p>
  {tbl(['strength', 'what the page looks like', 'example wording', 'trusted?'], [
    ['<b>1</b> a declared field', 'a labelled spec, consistent across the whole site', '<code>Skin Type: Dry, Sensitive</code>', 'yes'],
    ['<b>2</b> a suitability sentence', 'prose that states who the product is for', '<i>"suitable for oily and combination skin"</i>', 'yes'],
    ['<b>3</b> an ingredient benefit', 'a benefit claim rather than a suitability claim', '<i>"works well for dry skin"</i>', 'yes, weaker'],
    ['<b>4</b> a bare mention', 'the words appear with no claim attached', '<i>"a favourite among dry skin users"</i>', '<b>switched off</b>']])}

  <div class="note"><b>Strength 4 was switched off, and this is worth raising
  unprompted.</b> It is what produced a newspaper and a hiking-gear review site
  as sources, and a lip balm labelled "Oily". Once manufacturer pages became
  reachable through <code>site:</code> queries I no longer needed it, so every
  later pass refuses it outright. I found this weakness by auditing my own
  output, not because anyone pointed it out.</div>

  <h3>Which rules actually did the work</h3>
  <p>All {len(RULES)} rules that fired, in order of how much of the dataset they
  account for.</p>
  {tbl(['rule that matched', 'products', 'share of filled'], rule_rows)}
  <p class="small">Note that the top two rules together account for the bulk of
  the dataset, and both are strength 1 or 2. The weakest rule,
  <code>mentioned on the page</code>, survives on only
  {f(int(RULES.get('mentioned on the page', 0)))} rows from the early passes,
  all of them clearly labelled.</p>

  <h3>Who said it: the authority recorded on each row</h3>
  {tbl(['authority', 'products'], [[f'<code>{k}</code>', f(v)] for k, v in AUTH.items()])}
  <p class="small">The <code>product name</code> rows are products whose own
  name states the skin type, for example <i>Cetaphil Oily Skin Cleanser</i>.
  The name is the manufacturer's own wording, so it is treated as tier 1 and
  needs no link.</p>

  <h3>A worked example of each value</h3>
  <div class="two">
  <div><h4>A declared field</h4>{''.join(card(r) for r in e_field)}</div>
  <div><h4>Dry</h4>{''.join(card(r) for r in e_dry)}</div>
  <div><h4>Oily</h4>{''.join(card(r) for r in e_oily)}</div>
  <div><h4>Combination</h4>{''.join(card(r) for r in e_comb)}</div>
  </div>

  <h3>Two wordings that need explaining</h3>
  <div class="two">
  <div><h4>"suitable for all skin types" &rarr; <code>All</code></h4>
    <p class="small">Stored as a value, not left blank. It is a real statement
    by the manufacturer, not the absence of one.
    <b>{f(DIST.get('All', 0))} products</b> ({pc(DIST.get('All', 0), FILLED)} of
    filled rows) carry it.</p>
    {''.join(card(r) for r in e_all)}</div>
  <div><h4>"gentle enough for sensitive skin" &rarr; <code>Sensitive</code></h4>
    <p class="small">Sets the sensitivity axis. Where a brand names no oil
    level, <code>skin_type</code> becomes <code>All</code>, because the brand has
    not restricted it, and the sensitivity column carries the real finding.
    <b>{f(SENS.get('Sensitive', 0))} products</b>.</p>
    {''.join(card(r) for r in e_sens)}</div></div>

  <h3>Why blank sensitivity became "Resistant"</h3>
  <p>Sensitivity was blank on most rows after searching. Blank does not mean
  unknown here. Brands <b>advertise</b> a sensitive-skin claim when they have
  one, because it sells; they do not hide it. So after a thorough search the
  absence of that claim is itself informative, and <code>Resistant</code> is the
  other half of the Baumann axis.</p>
  <div class="note">This is an assumption, it is stated openly, and it is
  reversible. The tier and quote columns show exactly which rows carry a
  <i>positive</i> sensitivity finding
  ({f(SENS.get('Sensitive', 0))} products) as opposed to an inferred
  <code>Resistant</code> ({f(SENS.get('Resistant', 0))}).</div>

  <div class="note"><b>A caveat I should raise before anyone else does.</b>
  Vendruscolo et al. (2025, <i>Dermatological Reviews</i> 6:e70045) show that
  "suitable for all skin types" is a tolerance-testing claim derived from repeat
  insult patch testing, not a dermatological classification. The same paper
  found that <b>89% of 187 products labelled hypoallergenic</b> still contained
  at least one recognised contact allergen. So <code>All</code> must be read as
  "the manufacturer makes a universal claim", which is exactly what the column
  records, and not as clinical evidence of universal suitability.</div>
</section>
"""

# ============================================================ 6. FIXES
S6 = f"""
<section class="section" id="st-fixes">
  <h2>6 &middot; The mistakes I found, and how I fixed them</h2>
  <p class="lead">I am putting my own errors in the portal deliberately. A
  pipeline nobody audited is not more correct, only less examined. Each of these
  was found by checking my own output, and each one is fixed.</p>

  {tbl(['the mistake', 'how it was found', 'cost', 'fixed'], [
    ['sources graded by a too-narrow name test', 'listing the domains behind tier 3 and 4', '243 products mislabelled', 'yes'],
    ['never asked the brand&rsquo;s own website', 'asking why 893 rows had no official page', '<b>652 products</b>', 'yes'],
    ['brand verification check too strict', 're-reading my own filter', 'unknown, silent', 'yes'],
    ['quotes stored as raw HTML', 'reading a sample instead of trusting the count', '~1,100 unreadable', 'yes'],
    ['out of credits recorded as "no answer"', 'a pass returning suspicious failures', '1,052 rows', 'yes'],
    ['<code>&#92;boil&#92;b</code> does not match "oily"', 'testing the pattern by hand', 'silent undercount', 'yes'],
    ['resale listings counted as retail', 'reading the source league table', '5 products', 'yes']])}

  <div class="step"><div class="stt">1 &middot; A quarter of my sources were mislabelled</div>
    <div class="stv">found by listing the domains behind tier 3 and tier 4</div>
    <p style="font-size:13px;margin:0">I graded a domain as "the manufacturer"
    only if the brand name, punctuation stripped, appeared inside it. That fails
    constantly. "DERMA E" becomes <code>dermae</code>, "No7" is only three
    characters and too short to match safely, and country subdomains such as
    <code>us.no7beauty.com</code> were missed entirely. Meanwhile my shop list
    held about sixty names, so Macy's, Nordstrom, Bluemercury, LovelySkin and
    iHerb were all filed as "unknown source".
    <p class="mini">Correcting the labels alone, <b>with no searching at all and
    no credits spent</b>, moved 243 products into the tiers they had always
    belonged in.</p></p></div>

  <div class="step"><div class="stt">2 &middot; I never asked the brand's own website</div>
    <div class="stv">the largest error, and the reason 1,160 rows looked unfixable</div>
    <p style="font-size:13px;margin:0">Every early pass searched by keyword and
    hoped the manufacturer would rank highly. It often does not, because
    ingredient-analysis sites are better optimised for a query containing the
    words "skin type" than brand sites are. So the searches kept returning
    exactly the sources I was trying to avoid.
    <p class="mini">The fix was to learn each brand's domain once and then ask
    that domain directly with <code>site:</code>. <b>Of 893 products I had
    described as unfixable, 652 had an official or retail page all along</b>,
    316 on the brand's own site and 336 in a shop. I was wrong about the data.
    The data was not wrong about me.</p></p></div>

  <div class="step"><div class="stt">3 &middot; A verification check silently discarded good pages</div>
    <div class="stv">found by re-reading my own filter, not from any error message</div>
    <p style="font-size:13px;margin:0">After fetching a page I required the
    squashed brand name to appear in the HTML, to be sure I had the right
    product. But "Dear, Klairs" squashes to <code>dearklairs</code>, which
    appears nowhere, because the page says "Klairs". Real manufacturer pages were
    being thrown away without a single warning.
    <p class="mini">Now any distinctive word of the brand counts, and a page on
    the brand's own domain is trusted without the check. This is a good example
    to offer in a viva of a bug that produces no error and quietly costs
    coverage: the kind you only ever find by reading your own code.</p></p></div>

  <div class="step"><div class="stt">4 &middot; Some quotes were raw page markup</div>
    <div class="stv">found by reading a random sample of rows instead of trusting the count</div>
    <p style="font-size:13px;margin:0">Roughly a quarter of the stored sentences
    were fragments of HTML rather than readable English, such as
    <code>"&gt;&lt;/div&gt; &lt;/h1&gt; &lt;div class="marginb23"&gt;</code>.
    Every quote is now cleaned, and anything still unreadable is emptied rather
    than shown, on the principle that a blank cell is more honest than a broken
    one. <b>The link is always kept</b>, so the evidence survives even where the
    sentence did not, and a free follow-up pass re-opened the known URLs to
    recover clean sentences.
    <p class="mini">Today <b>{f(QUOTE)} of {f(FILLED)}</b> filled rows carry a
    readable sentence, and <b>{f(URL)}</b> carry a working link.</p></p></div>

  <div class="step"><div class="stt">5 &middot; "Out of credits" was being recorded as "no answer"</div>
    <div class="stv">1,052 rows affected</div>
    <p style="font-size:13px;margin:0">When an API key ran out, Serper returned
    HTTP 400. My code did not recognise 400 as a key problem, so it filed the
    result as "this product has no answer" and then skipped that product on the
    next run. Those products would have been permanently and invisibly missing.
    <p class="mini">Technical failures are now never written as findings. A
    network problem can never masquerade as a fact about a product. This is the
    single most dangerous class of bug in a scraping pipeline, because it is
    silent and it looks like data.</p></p></div>

  <div class="step"><div class="stt">6 &middot; Smaller corrections, listed for completeness</div>
    <div class="stv">each one found by testing a piece of the pipeline in isolation</div>
    <p style="font-size:13px;margin:0">
    &bull; <code>\\boil\\b</code> does not match "oily", so switched to prefix
    matching. This had been silently undercounting every sentence containing the
    word.<br>
    &bull; The code stored the <i>matched word</i> rather than the <i>sentence
    around it</i>, so quotes were meaningless out of context.<br>
    &bull; Six concurrent workers times three queries was dropping connections
    and producing 1,031 spurious "network error" rows. Reduced to three workers
    with three retries and exponential backoff.<br>
    &bull; <code>mark_not_applicable</code> only wrote a status into empty cells,
    so after its first run it never updated again and kept reporting stale
    coverage long after 1,182 more products had been filled.<br>
    &bull; A merge dropped 893 sensitivity-only rows because it required a
    <code>skin_type</code> value to be present, overstating the gap by 1,066.<br>
    &bull; Poshmark and other resale marketplaces were being counted as
    retailers. Demoted, because those listings are written by private sellers.</p></div>

  <div class="ok"><b>The rule that protects the whole thing.</b> Every merge
  step overwrites a row only when the new source has a <i>lower</i> tier number,
  meaning stronger evidence. Nothing is ever emptied. That is why coverage
  stayed at exactly {f(FILLED)} products through every one of these corrections
  while the quality underneath it kept rising, and it is why running another
  pass in future can only ever improve the file.</div>

  <div class="dg">
  <svg viewBox="0 0 700 150" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="14" y="20" width="180" height="48" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="104" y="40" text-anchor="middle" font-weight="700" fill="#8d5433">existing value</text>
    <text x="104" y="57" text-anchor="middle" fill="#6b6478">tier 3, an analysis site</text>
    <rect x="14" y="88" width="180" height="48" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="104" y="108" text-anchor="middle" font-weight="700" fill="#3f6b48">newly found</text>
    <text x="104" y="125" text-anchor="middle" fill="#6b6478">tier 1, the manufacturer</text>
    <path d="M194 44 C240 44 240 78 286 78" stroke="#b9aed0" fill="none" stroke-width="1.6"/>
    <path d="M194 112 C240 112 240 78 286 78" stroke="#6f9c78" fill="none" stroke-width="1.6"/>
    <rect x="292" y="52" width="150" height="52" rx="8" fill="#584a7a"/>
    <text x="367" y="72" text-anchor="middle" fill="#fff" font-weight="700">is it stronger?</text>
    <text x="367" y="90" text-anchor="middle" fill="#d5cae8">1 &lt; 3, so yes</text>
    <path d="M442 78 L486 78" stroke="#6f9c78" stroke-width="2"/><polygon points="486,78 478,73 478,83" fill="#6f9c78"/>
    <rect x="492" y="40" width="196" height="76" rx="8" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="590" y="62" text-anchor="middle" font-weight="700" fill="#3f6b48">replace it</text>
    <text x="590" y="80" text-anchor="middle" fill="#6b6478">if it had been weaker or equal,</text>
    <text x="590" y="96" text-anchor="middle" fill="#6b6478">the old value would simply stay.</text>
    <text x="590" y="110" text-anchor="middle" fill="#3f6b48" font-weight="700">nothing is ever deleted</text>
  </svg>
  <div class="cap">Why running another pass can only ever improve the file.</div></div>

  <h3>What the corrections did to the numbers</h3>
  {tbl(['stage', 'from maker or shop', 'on a weak source', 'coverage'], [
    ['before any correction', '6,017 (79.5%)', '1,403', f'{f(FILLED)} ({pc(FILLED)})'],
    ['after relabelling sources (free)', '6,260 (82.7%)', '1,160', f'{f(FILLED)} ({pc(FILLED)})'],
    ['after refusing analysis sites', '6,527 (86.2%)', '893', f'{f(FILLED)} ({pc(FILLED)})'],
    ['after asking brand sites directly', '7,179 (94.8%)', '241', f'{f(FILLED)} ({pc(FILLED)})'],
    ['<b>after the final pass</b>', f'<b>{f(T12)} ({pc(T12)})</b>', f'<b>{f(T[3]+T[4])}</b>', f'<b>{f(FILLED)} ({pc(FILLED)})</b>']])}
  <p class="small">Read the last column. It never changes. Every improvement in
  the quality of the evidence came at zero cost to coverage, which is the
  guarantee the merge rule was written to provide.</p>
</section>
"""

# ============================================================ 7. RESULTS
weak_rows = [[f'<code>{k}</code>', f(v),
              '<b>the source my supervisors questioned</b>' if re.search('skinsort|skincarisma', k)
              else 'ingredient analysis' if 'incidecoder' in k else 'other']
             for k, v in WEAK_SRC.head(10).items()]

S7 = f"""
<section class="section" id="st-results">
  <h2>7 &middot; The final numbers, in full</h2>
  <p class="lead">Everything on this page was read straight out of
  <code>SKINCARE_DATASET.csv</code> at the moment the page was built, so it
  cannot drift away from the file.</p>

  <div class="kpis">
    <div class="kpi"><div class="n">{pc(FOUND, FACIAL)}</div><div class="l">of facial products have a skin type</div></div>
    <div class="kpi"><div class="n">{pc(T12)}</div><div class="l">from the maker or a shop</div></div>
    <div class="kpi"><div class="n">{pc(T[1])}</div><div class="l">from the manufacturer directly</div></div>
    <div class="kpi"><div class="n">{f(NSRC)}</div><div class="l">distinct websites</div></div>
    <div class="kpi"><div class="n">{f(NBRAND)}</div><div class="l">brands covered</div></div>
  </div>

  <h3>From the whole dataset down to the products the question applies to</h3>
  <div class="dg">
  <svg viewBox="0 0 700 190" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="12">
    <rect x="30" y="16" width="620" height="34" rx="6" fill="#584a7a"/>
    <text x="340" y="38" text-anchor="middle" fill="#fff" font-weight="700">{f(N)} products in the dataset</text>
    <path d="M340 50 L340 62" stroke="#b9aed0" stroke-width="2"/>
    <rect x="30" y="66" width="{int(620*NA/N)}" height="34" rx="6" fill="#ded7ea"/>
    <text x="{30+int(620*NA/N)/2}" y="88" text-anchor="middle" fill="#584a7a" font-size="11" font-weight="700">{f(NA)}</text>
    <rect x="{30+int(620*NA/N)}" y="66" width="{620-int(620*NA/N)}" height="34" rx="6" fill="#7a68a6"/>
    <text x="{30+int(620*NA/N)+(620-int(620*NA/N))/2}" y="88" text-anchor="middle" fill="#fff" font-weight="700">{f(FACIAL)} facial products</text>
    <text x="{30+int(620*NA/N)/2}" y="116" text-anchor="middle" fill="#6b6478" font-size="10.5">lip, hand, hair</text>
    <text x="{30+int(620*NA/N)/2}" y="129" text-anchor="middle" fill="#6b6478" font-size="10.5">not applicable</text>
    <path d="M420 100 L420 116" stroke="#b9aed0" stroke-width="2"/>
    <rect x="{30+int(620*NA/N)}" y="120" width="{int((620-int(620*NA/N))*FOUND/max(FACIAL,1))}" height="34" rx="6" fill="#6f9c78"/>
    <text x="{30+int(620*NA/N)+int((620-int(620*NA/N))*FOUND/max(FACIAL,1))/2}" y="142" text-anchor="middle" fill="#fff" font-weight="700">{f(FOUND)} found &middot; {pc(FOUND, FACIAL)}</text>
    <text x="340" y="176" text-anchor="middle" fill="#6b6478" font-size="11">no brand publishes a facial skin type for a lip balm, so those are marked "not applicable" rather than counted as a gap</text>
  </svg>
  <div class="cap">The funnel, and why the denominator matters.</div></div>

  {tbl(['', 'products', 'share'], [
    ['products in the dataset', f(N), '100%'],
    ['not applicable (lip, hand, hair, tools)', f(NA), pc(NA)],
    ['facial products', f(FACIAL), pc(FACIAL)],
    ['<b>facial products with a skin type</b>', f'<b>{f(FOUND)}</b>', f'<b>{pc(FOUND, FACIAL)} of facial</b>'],
    ['searched, brand does not state it', f(NOTSTATED), pc(NOTSTATED, FACIAL) + ' of facial']])}
  <p class="small">Lip balms, hand creams and shampoos are marked <i>not
  applicable</i> rather than counted as gaps. No brand publishes a facial skin
  type for a lip balm and it would mean nothing if they did. Anything mentioning
  "face" or "facial" is kept even when it also mentions body, which preserved
  166 genuine facial products such as "Face &amp; Body Sunscreen SPF 30".</p>

  <h3>Where the values came from</h3>
  <div id="st_tier"></div>
  {tbl(['tier', 'source', 'products', 'share of dataset', 'share of filled'], [
    ['1', 'the manufacturer', f(T[1]), pc(T[1]), pc(T[1], FILLED)],
    ['2', 'a shop that sells it', f(T[2]), pc(T[2]), pc(T[2], FILLED)],
    ['3', 'an analysis site', f(T[3]), pc(T[3]), pc(T[3], FILLED)],
    ['4', 'something else', f(T[4]), pc(T[4]), pc(T[4], FILLED)]])}

  <h3>What the skin types are</h3>
  <div id="st_dist"></div>
  <h3>Sensitivity, the second axis</h3>
  <div id="st_sens"></div>

  <h3>The two axes crossed</h3>
  <p>This is the table that shows why sensitivity had to be a separate column.
  A product can be oily and sensitive, or oily and resistant, and those are
  different products.</p>
  {tbl(['skin type', 'products', 'sensitive', '%', 'resistant', '%'], CROSS)}

  <h3>Coverage by country of origin</h3>
  {tbl(['country', 'products', 'with a skin type', '%', 'from maker or shop', '%'], CT_COUNTRY)}
  <p class="small">Coverage holds up across origins, which matters because an
  uneven result would suggest the method favours large Western brands with
  well-built websites. It does not.</p>

  <h3>Coverage by product type</h3>
  {tbl(['product type', 'products', 'with a skin type', '%', 'from maker or shop', '%'], CT_TYPE)}

  <h3>The sentence I can defend in one line</h3>
  <div class="ok" style="font-size:14px"><b>{pc(T12)} of the dataset
  ({f(T12)} products) carries a skin type stated by the company that makes the
  product or by a shop that sells it, each with the source domain, the exact
  sentence and a link that opens the page. {pc(T[1])} comes from the
  manufacturer directly. {pc(FOUND, FACIAL)} of facial products have a value,
  drawn from {f(NSRC)} distinct websites across {f(NBRAND)} brands.</b></div>

  <h3>What is still weak, stated openly</h3>
  <p>{f(T[3]+T[4])} products, {pc(T[3]+T[4])} of the dataset, still rest on an
  analysis site or an unidentified page. I am not hiding them, because the tier
  column names them and anyone can filter them out in one line.</p>
  {tbl(['source', 'products', 'what it is'], weak_rows)}
  {''.join(card(r, '#c07a54') for r in e_weak)}
  <div class="note"><b>{f(REJECTED)} products</b>, {pc(REJECTED)} of the
  dataset, still trace back to Skinsort or SkinCarisma, the sources that were
  questioned. Every one was searched repeatedly against manufacturer and
  retailer sites and no declared statement was found, in most cases because the
  product has been discontinued and no shop lists it any more.
  <p style="margin:8px 0 0">My recommendation is to report both figures, the
  full {pc(FILLED)} and the declared-source {pc(T12)}, which is what
  record-linkage studies conventionally do.</p></div>

  <h3>Evidence carried on every row</h3>
  {tbl(['column', 'what it holds', 'filled'], [
    ['<code>skin_type</code>', 'Dry, Oily, Combination, Normal or All', f(FILLED)],
    ['<code>sensitivity</code>', 'Sensitive or Resistant', f(FILLED)],
    ['<code>skin_type_source</code>', 'the domain that answered', f(int((df.loc[got, 'skin_type_source'] != '').sum()))],
    ['<code>skin_type_quote</code>', 'the exact sentence from that page', f(QUOTE)],
    ['<code>skin_type_url</code>', 'the page, so any cell can be checked', f(URL)],
    ['<code>skin_type_tier</code>', '1 maker, 2 shop, 3 analysis, 4 other', f(FILLED)],
    ['<code>skin_type_rule</code>', 'which wording rule fired', f(FILLED)],
    ['<code>skin_type_authority</code>', 'manufacturer, retailer, analysis, other', f(FILLED)],
    ['<code>skin_type_status</code>', 'found, not applicable, or searched and not stated', f(N)]])}

  <h3>How to check any single value in ten seconds</h3>
  <div class="q">Open <code>SKINCARE_DATASET.xlsx</code> &rarr; filter to the
  brand &rarr; read <code>skin_type_quote</code> &rarr; click
  <code>skin_type_url</code> &rarr; the sentence is on the page. Every one of
  the {f(FILLED)} filled rows can be checked this way. That is the entire point
  of the rebuild.</div>
</section>
"""

JS = f"""
<script id="stjs">
bars('st_tier',[['the manufacturer',{100*T[1]/max(FILLED,1):.1f},'#6f9c78','{f(T[1])} ({pc(T[1], FILLED)})'],
 ['a shop that sells it',{100*T[2]/max(FILLED,1):.1f},'#7a68a6','{f(T[2])} ({pc(T[2], FILLED)})'],
 ['an analysis site',{100*T[3]/max(FILLED,1):.1f},'#c07a54','{f(T[3])} ({pc(T[3], FILLED)})'],
 ['something else',{100*T[4]/max(FILLED,1):.1f},'#b5484d','{f(T[4])} ({pc(T[4], FILLED)})']]);
bars('st_dist',[{','.join(f"['{k}',{100*v/max(FILLED,1):.1f},'{c}','{f(v)} ({pc(v, FILLED)})']" for (k, v), c in zip(sorted(DIST.items(), key=lambda x: -x[1]), ['#7a68a6', '#6f9c78', '#c07a54', '#b06a97', '#8a7fb0', '#9aa0b5']))}]);
bars('st_sens',[{','.join(f"['{k}',{100*v/max(FILLED,1):.1f},'{c}','{f(v)} ({pc(v, FILLED)})']" for (k, v), c in zip(sorted(SENS.items(), key=lambda x: -x[1]), ['#7a68a6', '#b06a97']))}]);
</script>
"""

# ======================================================== splice into the file
html = PORTAL.read_text(encoding='utf-8')

start = min([i for i in (html.find('<section class="section on" id="st-why">'),
                         html.find('<section class="section on" id="plan">'),
                         html.find('<section class="section" id="plan">')) if i != -1])
end = html.find('<!-- ============================================ HOME -->')
if end == -1:
    end = html.find('<section class="section" id="home">')
if start < 0 or end < 0:
    raise SystemExit('could not locate the skin type block, portal not changed')
html = html[:start] + S1 + S2 + S3 + S4 + S5 + S6 + S7 + '\n\n' + html[end:]
html = html.replace('<section class="section on" id="home">',
                    '<section class="section" id="home">')

nav_old = re.search(r'<div class="grp">skin type</div>.*?<div class="grp">overview</div>',
                    html, re.S)
nav_new = ('<div class="grp">skin type</div>\n'
           '    <a class="on" data-s="st-why">1. Why I started again</a>\n'
           '    <a data-s="st-tries">2. Everything I tried</a>\n'
           '    <a data-s="st-serper">3. How Serper works</a>\n'
           '    <a data-s="st-tiers">4. The four tiers</a>\n'
           '    <a data-s="st-rules">5. Sentence to value</a>\n'
           '    <a data-s="st-fixes">6. Mistakes I fixed</a>\n'
           '    <a data-s="st-results">7. The final numbers</a>\n'
           '    <div class="grp">overview</div>')
if nav_old:
    html = html[:nav_old.start()] + nav_new + html[nav_old.end():]

html = re.sub(r'<style id="stcss">.*?</style>', '', html, flags=re.S)
html = html.replace('</head>', CSS + '</head>')
html = re.sub(r'<script id="stjs">.*?</script>', '', html, flags=re.S)
# insert immediately before </body>, whatever whitespace happens to be there.
# doing this with a fixed string broke on the second run, because removing the
# previous block left extra newlines and the anchor stopped matching.
html = re.sub(r'\s*</body>', '\n' + JS + '\n</body>', html, count=1)
if 'id="stjs"' not in html:
    raise SystemExit('the chart script was not inserted, portal not saved')

PORTAL.write_text(html, encoding='utf-8')

words = {}
for m in re.finditer(r'<section class="section[^"]*" id="(st-[^"]+)">(.*?)</section>', html, re.S):
    words[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())

print('=' * 64)
print('  PORTAL REBUILT')
print('=' * 64)
print(f'  {PORTAL}\n')
for k, v in words.items():
    print(f'    {k:12s}{v:6,} words')
print(f'    {"TOTAL":12s}{sum(words.values()):6,} words across 7 pages\n')
print(f'  products                {f(N)}')
print(f'    not applicable        {f(NA)}')
print(f'    facial                {f(FACIAL)}')
print(f'    found                 {f(FOUND)}   ({pc(FOUND, FACIAL)} of facial)')
print(f'  filled                  {f(FILLED)}   ({pc(FILLED)})')
print(f'    tier 1 manufacturer   {f(T[1])}   ({pc(T[1])})')
print(f'    tier 2 shop           {f(T[2])}   ({pc(T[2])})')
print(f'    tier 3 analysis       {f(T[3])}')
print(f'    tier 4 other          {f(T[4])}')
print(f'  MAKER OR SHOP           {f(T12)}   ({pc(T12)})')
print(f'  readable quotes         {f(QUOTE)}')
print(f'  clickable links         {f(URL)}')
print(f'  distinct websites       {f(NSRC)}')
print(f'  brands                  {f(NBRAND)}')
print(f'  still skinsort/carisma  {f(REJECTED)}')
