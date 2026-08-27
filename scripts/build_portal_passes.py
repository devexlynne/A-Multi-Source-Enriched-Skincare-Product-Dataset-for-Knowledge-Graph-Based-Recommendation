"""
The "seven passes" portal page

What each search pass asked, how many pages it opened, which websites it would
accept, what it cost, and how many products it left behind for the next one.

Answers, in diagram form, the questions that come up when someone follows the
method closely:

    what happens when a pass finds nothing
    what actually changes between one pass and the next
    what a "snippet" is and why it matters
    how many web pages are opened per product
    how sites are rejected, and at what point
    whether the whole page is read or only part of it

Usage:
    py build_portal_passes.py
"""
import re
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
d = pd.read_csv('SKINCARE_DATASET.csv', dtype=str, low_memory=False).fillna('')
N = len(d)
tier = pd.to_numeric(d['skin_type_tier'], errors='coerce')
got = d['skin_type'] != ''
FILLED = int(got.sum())
T12 = int((tier[got] <= 2).sum())


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


# products still without a skin type after each pass, from the run logs
JOURNEY = [
    ('start', 7569, 'the column was emptied and rebuilt from nothing'),
    ('after pass 1', 1881, 'one question, 3 pages each'),
    ('after pass 2', 1186, 'a different question, 6 pages'),
    ('after pass 3', 149, 'three questions, 10 pages, the loose rule'),
]
WEAK = [
    ('after pass 3', 1403, 'on an analysis site or an unknown site'),
    ('after retier', 1160, 'free, only the labels were corrected'),
    ('after rescue', 893, 'analysis sites refused outright'),
    ('after direct', 241, 'asked each brand its own site'),
    ('after last241', 178, 'three more angles on the stubborn ones'),
]

W = 660
bars = []
y = 8
for lab, v, note in JOURNEY:
    wpx = int(560 * v / 7569)
    bars.append(f'<text x="8" y="{y+15}" font-size="11.5" fill="#6b6478">{lab}</text>')
    bars.append(f'<rect x="96" y="{y+2}" width="{max(wpx,3)}" height="18" rx="4" '
                f'fill="{"#b5484d" if v > 3000 else "#c07a54" if v > 500 else "#6f9c78"}"/>')
    bars.append(f'<text x="{96+max(wpx,3)+7}" y="{y+16}" font-size="11.5" '
                f'font-weight="bold" fill="#584a7a">{f(v)}</text>')
    bars.append(f'<text x="188" y="{y+16}" font-size="10.5" fill="#9990a8">{note}</text>')
    y += 26
FUNNEL = (f'<div class="dg"><svg viewBox="0 0 {W} {y+22}" '
          f'xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial">'
          f'<text x="8" y="{y+16}" font-size="11" fill="#6b6478" font-style="italic">'
          f'products still WITHOUT a skin type after each pass</text>'
          + ''.join(bars) + '</svg></div>')

bars2 = []
y = 8
for lab, v, note in WEAK:
    wpx = int(560 * v / 1500)
    bars2.append(f'<text x="8" y="{y+15}" font-size="11.5" fill="#6b6478">{lab}</text>')
    bars2.append(f'<rect x="104" y="{y+2}" width="{max(wpx,3)}" height="18" rx="4" '
                 f'fill="{"#c07a54" if v > 500 else "#6f9c78"}"/>')
    bars2.append(f'<text x="{104+max(wpx,3)+7}" y="{y+16}" font-size="11.5" '
                 f'font-weight="bold" fill="#584a7a">{f(v)}</text>')
    bars2.append(f'<text x="196" y="{y+16}" font-size="10.5" fill="#9990a8">{note}</text>')
    y += 26
FUNNEL2 = (f'<div class="dg"><svg viewBox="0 0 {W} {y+22}" '
           f'xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial">'
           f'<text x="8" y="{y+16}" font-size="11" fill="#6b6478" font-style="italic">'
           f'products still on a WEAK source after each pass</text>'
           + ''.join(bars2) + '</svg></div>')

PAGE = f"""
<section class="section" id="st-passes">
  <h2>3c &middot; The seven passes, and what changed each time</h2>
  <p class="lead">No single search filled the column. Seven passes did, and each
  one asked a different question of the products the previous pass could not
  answer. This page is what changed, why, and what it cost.</p>

  <h3>What happens when a pass finds nothing</h3>
  <div class="q">Nothing is written. The product keeps an empty cell and is
  picked up by the next pass. Each pass only ever looks at products that are
  still empty, so no product is ever paid for twice.</div>
  {FUNNEL}
  <p class="small">Read it as a queue getting shorter. Pass 1 attempted all
  {f(N)} products and left 1,881 unanswered. Pass 2 attempted only those 1,881.
  Pass 3 attempted only the 1,186 that were still empty after that.</p>

  <h3>The three things that change between passes</h3>
  {tbl(['what changes', 'why it helps'], [
    ['<b>the wording of the question</b>',
     'a brand that never writes "skin type" may still write "suitable for dry skin". asking differently finds different pages.'],
    ['<b>how many pages get opened</b>',
     'from 3 in pass 1 up to 10 in pass 3. more pages costs more time, so it is only spent on the products that resisted everything else.'],
    ['<b>which websites are acceptable</b>',
     'this is the one that reverses direction halfway through, and it is the most important row in the table below.']])}

  <h3>All seven passes</h3>
  {tbl(['#', 'pass', 'the question it asked', 'pages', 'sites accepted', 'cost'], [
    ['1', '<code>serper_skintype</code>', '<code>&lt;brand&gt; &lt;name&gt; skin type</code>', '3',
     'maker, shop, analysis', '~7,500'],
    ['2', '<code>serper_pass2</code>',
     '<code>&lt;brand&gt; &lt;name&gt; suitable for dry oily sensitive skin</code>', '6',
     '+ unknown sites', '~1,900'],
    ['3', '<code>serper_pass3</code>',
     'three: the plain name, "for dry oily sensitive skin", "review skin type"', '10',
     'everything but social and marketplaces', '~3,500'],
    ['4', '<code>retier</code>', '<i>no search at all</i>', '&mdash;',
     '&mdash;', '<b>free</b>'],
    ['5', '<code>serper_rescue</code>',
     '<code>&lt;brand&gt; &lt;name&gt; skin type</code> + <code>official site</code>', '8',
     '<b>maker and shop only</b>', '~1,700'],
    ['6', '<code>serper_direct</code>',
     '<b><code>site:&lt;brand domain&gt; &lt;name&gt;</code></b> + <code>&lt;name&gt; buy</code>', '6',
     '<b>maker and shop only</b>', '~1,700'],
    ['7', '<code>serper_last241</code>',
     '<code>"&lt;brand&gt; &lt;name&gt;" ingredients</code> + <code>for which skin type</code>', '6',
     '<b>maker and shop only</b>', '~600']])}

  <div class="note"><b>The turn in the middle.</b> Passes 1 to 3 got steadily
  <i>more permissive</i>, because the goal was coverage and each one was
  scraping the bottom of the barrel. Passes 5 to 7 went the other way and got
  <i>stricter</i>, because by then the goal had changed to quality. That turn
  is where my supervisors' objection enters the method: analysis sites went
  from accepted, to tolerated, to banned outright.</div>
  {FUNNEL2}
  <p class="small">The second chart is the quality story rather than the
  coverage one. Coverage never moved after pass 3; what kept improving was
  where the answers came from. Today {f(T12)} of {f(FILLED)} filled values,
  {pc(T12, FILLED)}, come from a manufacturer or a shop.</p>

  <h3>What a "snippet" is, and why it saves work</h3>
  <p>When you search on Google, each result has a title, a link, and two lines
  of grey text underneath. That grey text is the <b>snippet</b>: a fragment
  Google pulls out of the page, usually the part containing your search words.
  Serper hands it over as data.</p>
  <div class="dg">
  <svg viewBox="0 0 700 190" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="14" y="12" width="330" height="86" rx="8" fill="#fff" stroke="#b9aed0"/>
    <text x="26" y="32" fill="#7a68a6" font-size="12" font-weight="700">Moisturising Cream | CeraVe</text>
    <text x="26" y="48" fill="#3f6b48" font-size="10.5">https://www.cerave.com/moisturising-cream</text>
    <text x="26" y="68" fill="#6b6478" font-size="10.5">Developed with dermatologists, this rich cream</text>
    <text x="26" y="82" fill="#6b6478" font-size="10.5">is suitable for normal to dry skin ...</text>
    <text x="26" y="112" fill="#8d5433" font-size="10.5" font-style="italic">the grey text is the snippet</text>
    <path d="M344 55 L392 55" stroke="#6f9c78" stroke-width="2"/>
    <polygon points="392,55 384,50 384,60" fill="#6f9c78"/>
    <rect x="398" y="12" width="288" height="86" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="542" y="36" text-anchor="middle" font-weight="700" fill="#3f6b48">read the snippet FIRST</text>
    <text x="542" y="56" text-anchor="middle" fill="#6b6478">if the answer is already in it,</text>
    <text x="542" y="72" text-anchor="middle" fill="#6b6478">the page is never downloaded</text>
    <text x="542" y="90" text-anchor="middle" fill="#8d5433" font-style="italic">faster, and gentler on the site</text>
    <rect x="14" y="126" width="672" height="52" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="350" y="148" text-anchor="middle" fill="#8d5433" font-weight="700">Google often picks exactly the sentence that answers the question, because that is what it was asked about.</text>
    <text x="350" y="166" text-anchor="middle" fill="#6b6478">when it does not, the page is downloaded and read in full.</text>
  </svg>
  <div class="cap">The snippet is a free first look at the page.</div></div>

  <h3>How many pages are actually opened per product</h3>
  <p>Serper returns <b>10 results</b> per query. What happens to those ten:</p>
  <div class="dg">
  <svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="14" y="12" width="150" height="40" rx="7" fill="#584a7a"/>
    <text x="89" y="30" text-anchor="middle" fill="#fff" font-weight="700">10 results</text>
    <text x="89" y="45" text-anchor="middle" fill="#d5cae8">back from Serper</text>
    <path d="M164 32 L206 32" stroke="#b9aed0" stroke-width="2"/><polygon points="206,32 198,27 198,37" fill="#b9aed0"/>
    <rect x="212" y="12" width="200" height="40" rx="7" fill="#fdeeee" stroke="#b5484d"/>
    <text x="312" y="30" text-anchor="middle" fill="#8d3a3e" font-weight="700">1. grade every domain</text>
    <text x="312" y="45" text-anchor="middle" fill="#6b6478">rejected ones are never opened</text>
    <path d="M412 32 L454 32" stroke="#b9aed0" stroke-width="2"/><polygon points="454,32 446,27 446,37" fill="#b9aed0"/>
    <rect x="460" y="12" width="226" height="40" rx="7" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="573" y="30" text-anchor="middle" fill="#584a7a" font-weight="700">2. sort strongest first</text>
    <text x="573" y="45" text-anchor="middle" fill="#6b6478">brand site before shop</text>
    <path d="M573 52 L573 70" stroke="#b9aed0" stroke-width="2"/><polygon points="573,70 568,62 578,62" fill="#b9aed0"/>
    <rect x="400" y="74" width="286" height="40" rx="7" fill="#fff" stroke="#b9aed0"/>
    <text x="543" y="92" text-anchor="middle" fill="#584a7a" font-weight="700">3. read the snippet</text>
    <text x="543" y="107" text-anchor="middle" fill="#6b6478">free, no download</text>
    <path d="M400 94 L358 94" stroke="#b9aed0" stroke-width="2"/><polygon points="358,94 366,89 366,99" fill="#b9aed0"/>
    <rect x="120" y="74" width="230" height="40" rx="7" fill="#fff" stroke="#b9aed0"/>
    <text x="235" y="92" text-anchor="middle" fill="#584a7a" font-weight="700">4. if not enough, download it</text>
    <text x="235" y="107" text-anchor="middle" fill="#6b6478">up to 200,000 characters</text>
    <path d="M235 114 L235 132" stroke="#b9aed0" stroke-width="2"/><polygon points="235,132 230,124 240,124" fill="#b9aed0"/>
    <rect x="60" y="136" width="350" height="40" rx="7" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="235" y="154" text-anchor="middle" fill="#8d5433" font-weight="700">5. is this really the brand? really a shop?</text>
    <text x="235" y="169" text-anchor="middle" fill="#6b6478">two checks after downloading</text>
    <path d="M410 156 L452 156" stroke="#6f9c78" stroke-width="2"/><polygon points="452,156 444,151 444,161" fill="#6f9c78"/>
    <rect x="458" y="136" width="228" height="40" rx="7" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="572" y="154" text-anchor="middle" fill="#3f6b48" font-weight="700">6. run the wording rules</text>
    <text x="572" y="169" text-anchor="middle" fill="#6b6478">on the whole page</text>
    <rect x="14" y="196" width="672" height="44" rx="8" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="350" y="216" text-anchor="middle" fill="#3f6b48" font-weight="700">IT STOPS AT THE FIRST PAGE THAT ANSWERS.</text>
    <text x="350" y="233" text-anchor="middle" fill="#6b6478">so most products cost one or two downloads, not ten, even when the limit allows ten.</text>
  </svg>
  <div class="cap">Ten results in, usually one or two pages actually opened.</div></div>

  <h3>How sites are ignored, and at what point</h3>
  <p>Two filters, one before downloading and one after.</p>
  <div class="two">
  <div><h4>Before &middot; the domain is checked</h4>
  {tbl(['refused', 'why'], [
    ['incidecoder, skinsort, skincarisma, cosdna', 'analysis sites, they infer rather than state'],
    ['allure, byrdie, vogue, nypost, buzzfeed', 'magazines, editorial opinion'],
    ['instagram, tiktok, reddit, youtube', 'social, nobody is accountable'],
    ['ebay, aliexpress, etsy, dhgate', 'marketplaces, user-written listings'],
    ['poshmark, mercari, depop, vinted', 'resale, a private seller wrote it']])}
  <p class="small">Rejected domains are never downloaded at all, so they cost
  nothing and can never contribute a value.</p></div>
  <div><h4>After &middot; the page itself is checked</h4>
  {tbl(['check', 'what it stops'], [
    ['a distinctive word of the brand must appear in the page',
     'the search drifting onto a different product'],
    ['for non-brand sites, the page must have an add-to-cart, a price, or product markup',
     'a blog that merely mentions the product being treated as a shop']])}
  <p class="small">This second check is why a shop is recognised by what the
  page <i>does</i> rather than by whether I had heard of it, which matters for
  the small Lebanese retailers.</p></div>
  </div>

  <h3>Does it read the whole page?</h3>
  <div class="ok"><b>Yes.</b> The first 200,000 characters of HTML are
  downloaded, <code>&lt;script&gt;</code> and <code>&lt;style&gt;</code> blocks
  are stripped out, and all nine wording rules run over everything that is left.
  It is not restricted to a description field, so a sentence in a spec table or
  a bullet at the very bottom of the page is still found.</div>
  <div class="note"><b>And that is exactly why the negation problem mattered.</b>
  Reading the whole page means picking up sentences from anywhere on it,
  including an FAQ that says "this is <b>not</b> suitable for sensitive skin".
  Until that was checked, the rules matched the positive phrase inside the
  negative sentence. 13 products were affected, 0.17%, and all are corrected.</div>

  <h3>What it all cost</h3>
  {tbl(['', 'credits'], [
    ['the seven passes together', '~16,900'],
    ['of which spent by the two free passes', '<b>0</b>'],
    ['bought', '50,000 for $50'],
    ['<b>per product, averaged over the whole dataset</b>', f'<b>about {16900/N:.1f} credits</b>']])}
</section>
"""

html = PORTAL.read_text(encoding='utf-8')
html = re.sub(r'<section class="section" id="st-passes">.*?</section>', '', html, flags=re.S)
anchor = html.find('<section class="section" id="st-tiers">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + PAGE + '\n' + html[anchor:]

m = re.search(r'(<a data-s="st-tiers">)', html)
if m and 'st-passes' not in html[:m.start()]:
    html = html[:m.start()] + '<a data-s="st-passes">3c. The seven passes</a>\n    ' + html[m.start():]

PORTAL.write_text(html, encoding='utf-8')

sec = re.search(r'<section class="section" id="st-passes">(.*?)</section>', html, re.S).group(1)
print('=' * 56)
print('  SEVEN PASSES PAGE ADDED')
print('=' * 56)
print(f'  {len(re.sub(r"<[^>]+>", " ", sec).split()):,} words, '
      f'{sec.count("<table>")} tables, {sec.count("<svg")} diagrams')
print(f'  coverage journey: 7,569 empty -> 149 empty')
print(f'  quality journey : 1,403 weak -> 178 weak')
print(f'  declared today  : {f(T12)} of {f(FILLED)} ({pc(T12, FILLED)})')
