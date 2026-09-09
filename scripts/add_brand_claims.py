"""
add_brand_claims.py

Adds brand level information to SKINCARE_FINAL.csv.

Two different kinds of thing go in here, and I keep them apart on purpose.

1. WHO OWNS THE BRAND.
   A verifiable corporate fact. Kenvue owns Neutrogena. L'Oreal owns CeraVe.
   Anyone can check this against a company annual report. It is useful for
   many questions, not just this one.

2. WHETHER SOMEBODY HAS LISTED THE BRAND FOR BOYCOTT.
   This is NOT a fact about the product. It is a claim made by a named
   organisation on a named date. So I never write a bare yes or no. Every
   flag carries who said it, on what basis, from what URL, read on what day.
   If the list changes, I swap reference/boycott_claims.csv and rerun. The
   dataset does not hardcode anybody's politics.

The lists come from two published sources, both read on 2026-09-10:
  bdsmovement.net/Guide-to-BDS-Boycott
  ethicalconsumer.org/ethical-campaigns-boycotts/palestine-boycott-list
I did not compile a list myself and I did not add anything the sources
do not say.

Matching is at brand level, then at parent company level. A parent match is
recorded as parent_listed, never as listed, because they are different
claims: "this brand is on the list" and "the company that owns this brand is
on the list" are not the same sentence.

Safety: write to a temp file, assert the row count, then os.replace.
"""
import csv, os, re, collections

csv.field_size_limit(10**9)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "repo")
SRC  = os.path.join(REPO, "SKINCARE_FINAL.csv")
OWN  = os.path.join(REPO, "reference", "brand_ownership.csv")
CLM  = os.path.join(REPO, "reference", "boycott_claims.csv")

NEW = ["brand_parent_company",
       "boycott_listing_status",
       "boycott_listing_authority",
       "boycott_listing_level",
       "boycott_listing_basis",
       "boycott_listing_source",
       "boycott_listing_date_read"]


def norm(s):
    """Fold a brand name so 'L'Oreal Paris' and 'L'Oréal Paris' meet."""
    s = (s or "").lower().strip()
    for a, b in (("é", "e"), ("è", "e"), ("ê", "e"), ("ë", "e"),
                 ("à", "a"), ("â", "a"), ("ô", "o"), ("ö", "o"),
                 ("î", "i"), ("ï", "i"), ("ç", "c"), ("ù", "u"), ("û", "u")):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def main():
    owners = {}
    for r in csv.DictReader(open(OWN, encoding="utf-8")):
        if r["brand"].strip():
            owners[norm(r["brand"])] = r["parent_company"].strip()

    claims = {}
    for r in csv.DictReader(open(CLM, encoding="utf-8")):
        claims[norm(r["entity"])] = r

    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    n_before = len(rows)
    fields = list(rows[0].keys())
    out_fields = fields + [c for c in NEW if c not in fields]

    tally = collections.Counter()
    for row in rows:
        b = norm(row.get("brand"))
        parent = owners.get(b, "")

        hit, how = None, ""
        if b in claims:
            hit, how = claims[b], "listed"
        elif parent and norm(parent) in claims:
            hit, how = claims[norm(parent)], "parent_listed"

        if hit:
            row["boycott_listing_status"]    = how
            row["boycott_listing_authority"] = hit["asserted_by"]
            row["boycott_listing_level"]     = hit["level"]
            row["boycott_listing_basis"]     = hit["basis"]
            row["boycott_listing_source"]    = hit["source_url"]
            row["boycott_listing_date_read"] = hit["date_read"]
        elif parent or b in owners:
            # Ownership is known and neither the brand nor the parent appears
            # on the source list. That is a real negative, so say so.
            row["boycott_listing_status"]    = "not_on_this_list"
            row["boycott_listing_authority"] = "Palestinian BDS National Committee"
            row["boycott_listing_level"]     = ""
            row["boycott_listing_basis"]     = ""
            row["boycott_listing_source"]    = "https://bdsmovement.net/Guide-to-BDS-Boycott"
            row["boycott_listing_date_read"] = "2026-09-10"
        else:
            # Ownership unknown, so absence from the list proves nothing.
            # Never write a negative I cannot stand behind.
            row["boycott_listing_status"]    = "not_checked"
            for c in NEW[2:]:
                row[c] = ""

        row["brand_parent_company"] = parent
        tally[row["boycott_listing_status"]] += 1

    tmp = SRC + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(rows)
    with open(tmp, encoding="utf-8", newline="") as f:
        check = sum(1 for _ in csv.DictReader(f))
    assert check == n_before, f"row count changed: {n_before} -> {check}"
    os.replace(tmp, SRC)

    print(f"rows {n_before}, columns {len(fields)} -> {len(out_fields)}")
    for k, v in tally.most_common():
        print(f"  {k:20s} {v:6d}  ({v/n_before*100:.1f}%)")
    known = sum(1 for r in rows if r["brand_parent_company"])
    print(f"  parent company known {known} ({known/n_before*100:.1f}%)")


if __name__ == "__main__":
    main()
