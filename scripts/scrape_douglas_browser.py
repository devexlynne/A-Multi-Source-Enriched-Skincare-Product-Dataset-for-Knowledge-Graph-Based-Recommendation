"""
DOUGLAS SCRAPER - REAL BROWSER VERSION (Playwright)

Why this version exists
  Plain `requests` gets HTTP 403 from Douglas. Their bot protection does not
  just read the User-Agent, it fingerprints the TLS handshake itself, which no
  header trick can fake. The only reliable answer is to drive a real browser.

  This opens Chromium, loads each skin-type category page exactly as a person
  would, scrolls to trigger lazy loading, and reads the products off the page.

SETUP (one time, ~2 minutes)
  py -m pip install playwright pandas
  py -m playwright install chromium

RUN
  py scrape_douglas_browser.py
  A browser window opens and drives itself. Leave it alone until it finishes.
  Roughly 5-10 minutes for all five categories.

The idea is still the same
  Douglas has one category page PER SKIN TYPE, so the page IS the label. I am
  not interpreting any text: every product on "fuer-trockene-haut" is a dry
  skin product because Douglas categorised it that way. That makes this
  retailer-DECLARED evidence, the same class as Sephora or Mazen.
"""
import re, time
import pandas as pd
from playwright.sync_api import sync_playwright

BASE = 'https://www.douglas.de'
CATEGORIES = [
    ('dry',         '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-trockene-haut/120601'),
    ('oily',        '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-fettige-haut/120602'),
    ('sensitive',   '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-sensible-haut/120603'),
    ('acne',        '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-unreine-haut/120604'),
    ('combination', '/de/c/hautpflege/hautzustaende-routinen/mischhaut/99190205'),
]
MAX_PAGES = 12          # Douglas shows ~10 pages per category


def read_products(page):
    """Read (brand, name) off the rendered page.
    Douglas renders each tile as a link to /p/<id>; the brand sits in its own
    element inside the tile, so I take them together where possible."""
    return page.evaluate("""() => {
        const out = [];
        document.querySelectorAll('a[href*="/p/"]').forEach(a => {
            const tile = a.closest('div,article,li') || a;
            const txt  = (tile.innerText || '').split('\\n')
                          .map(s => s.trim()).filter(Boolean);
            if (txt.length < 2) return;
            // the first line is usually the product-type phrase, then brand,
            // then the product name
            let brand = '', name = '';
            for (let i = 0; i < txt.length && i < 6; i++) {
                const line = txt[i];
                if (/^\\d/.test(line) || /€/.test(line)) break;
                if (!brand && !/ für /i.test(line)) { brand = line; continue; }
                if (brand && !name && line !== brand) { name = line; break; }
            }
            if (brand && name) out.push([brand, name]);
        });
        return out;
    }""")


def main():
    rows = []
    with sync_playwright() as pw:
        # headless=False looks like a normal browser and is far less likely to
        # be blocked. You will see the window working - that is expected.
        browser = pw.chromium.launch(headless=False)
        ctx = browser.new_context(
            locale='de-DE',
            viewport={'width': 1440, 'height': 900},
            user_agent=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/126.0.0.0 Safari/537.36'))
        page = ctx.new_page()

        print('opening Douglas homepage to pick up cookies...')
        page.goto(BASE + '/de', wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        # accept the cookie banner if it appears, otherwise it blocks the page
        for sel in ('button:has-text("Akzeptieren")', 'button:has-text("Alle akzeptieren")',
                    '#onetrust-accept-btn-handler'):
            try:
                page.click(sel, timeout=2500); print('  cookie banner accepted'); break
            except Exception:
                pass
        time.sleep(2)

        for label, path in CATEGORIES:
            print(f'\n=== {label.upper()}')
            seen = set()
            for pno in range(MAX_PAGES):
                url = f'{BASE}{path}' + (f'?page={pno}' if pno else '')
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                except Exception as e:
                    print('   load failed:', str(e)[:60]); break
                # scroll so lazy-loaded tiles actually render
                for _ in range(6):
                    page.mouse.wheel(0, 2200); time.sleep(0.7)
                time.sleep(1.5)

                got = read_products(page)
                new = [(b, n) for b, n in got if (b, n) not in seen]
                if not new:
                    print(f'   page {pno}: nothing new, done'); break
                for b, n in new:
                    seen.add((b, n))
                    rows.append({'douglas_skin_type': label, 'brand': b, 'name': n})
                print(f'   page {pno}: +{len(new)} (total {len(seen)})')
                pd.DataFrame(rows).to_csv('douglas_skintype.csv', index=False)
        browser.close()

    out = pd.DataFrame(rows).drop_duplicates()
    out.to_csv('douglas_skintype.csv', index=False)
    print(f'\nDONE. {len(out):,} product-labels -> douglas_skintype.csv')
    if not out.empty:
        print(out['douglas_skin_type'].value_counts().to_string())
        print(f"distinct brands captured: {out['brand'].nunique()}")
        print('\nnext: py merge_douglas.py')


if __name__ == '__main__':
    main()
