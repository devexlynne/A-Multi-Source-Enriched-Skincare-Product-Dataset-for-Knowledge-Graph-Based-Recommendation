# Brand level claims: ownership and boycott listings

What I added, why it is built the way it is, and what it cannot do.

---

## 1. The problem this had to solve

Everything else in the dataset is derived from the ingredient list. An INCI
string tells you whether a product contains retinol. It tells you nothing
about the company that made it.

So "is this brand boycotted" is a different kind of question from every other
column. It is not a fact about the formula. It is not even a fact about the
product. It is **something a named organisation published on a named day**.

If I write a column that says `boycotted: yes`, the system is making a
political assertion in its own voice, and a user has no way to see where it
came from or when it was last true. That is not acceptable in a thesis and it
is not acceptable in a recommender.

So I split it in two.

---

## 2. Two files, two different kinds of thing

### `reference/brand_ownership.csv` — facts

Corporate ownership. Kenvue owns Neutrogena. L'Oréal owns CeraVe. Unilever
owns Paula's Choice. Anyone can check these against an annual report, so they
are asserted directly.

This column is useful far beyond this one question. It answers "how
concentrated is my catalogue really", it lets me group products by
manufacturer, and it is the thing that lets **any** brand level list be
applied later without touching the dataset again.

**118 brands mapped, covering 3,109 of 12,629 products (24.6%).**

### `reference/boycott_claims.csv` — claims

Every row carries: the entity, the list name, the tier the source itself
assigns, who asserted it, the basis in the source's own words, the URL, and
the date I read it.

I did not compile this list. I copied it from two published sources, both read
on **10 September 2026**:

| Source | What it is |
|---|---|
| [bdsmovement.net Guide to BDS Boycott](https://bdsmovement.net/Guide-to-BDS-Boycott) | The BDS National Committee's own published guide. The primary source |
| [Ethical Consumer, Palestine boycott list](https://www.ethicalconsumer.org/ethical-campaigns-boycotts/palestine-boycott-list) | A UK research organisation reproducing the same Level 1 list with per company reasons |

I added nothing the sources do not say.

---

## 3. The columns

Seven new columns, 110 → **117**. Row count unchanged at 12,629. **0 original
cells altered.**

| Column | What it holds |
|---|---|
| `brand_parent_company` | Who owns the brand. Blank if I could not establish it |
| `boycott_listing_status` | `listed`, `parent_listed`, `not_on_this_list`, `not_checked` |
| `boycott_listing_authority` | Who said it |
| `boycott_listing_level` | The tier the source assigns, 1, 2 or 3 |
| `boycott_listing_basis` | The reason, in the source's words |
| `boycott_listing_source` | The URL |
| `boycott_listing_date_read` | When I read it |

**There is no boolean.** On purpose. The status is never separable from who
said it.

### The four statuses, and why there are four

| Status | Count | Meaning |
|---|---|---|
| `listed` | **2** | The brand itself is named on the source list |
| `parent_listed` | 0 | The company that owns the brand is named, but not the brand |
| `not_on_this_list` | 3,109 | I know the owner, and neither brand nor owner appears |
| `not_checked` | 9,518 | I could not establish the owner, so absence proves nothing |

That last row matters. A negative I cannot stand behind is worse than a blank,
so 75.4% of the catalogue says `not_checked` rather than pretending to be
clean.

---

## 4. The result, and it is not what most people expect

**Two products.** AHAVA Purifying Mud Mask and AHAVA Mineral Hand Cream.

The BDS movement uses **targeted** boycotts on purpose. Its own guide explains
why: a short, carefully chosen list of companies with proven, documented
involvement has more effect than a long list. The Level 1 list is mostly tech,
finance, energy and fast food. **The only cosmetics company on it is Ahava.**

The very long cosmetics lists that circulate on social media and in consumer
apps are Level 2 and Level 3, which the source itself describes as "connected
companies" and "broad connections". Those are weaker claims, they are not
published in a machine readable form, and reproducing them from memory or from
screenshots would be exactly the kind of unsourced assertion this whole design
exists to avoid.

So I implemented Level 1 completely and honestly, and I left Levels 2 and 3
out with a stated reason rather than filling them with guesses.

**Say this to your supervisor:** the finding is not "only two products are
affected". The finding is **"the authoritative list and the popular list are
not the same list, and a system that does not record which one it used is
not reporting, it is asserting."** That is a methodological result, and it is
worth more than a big number would have been.

---

## 5. Why a parent match is not the same as a brand match

`parent_listed` exists as a separate value because these are two different
sentences:

- "This brand is on the list."
- "The company that owns this brand is on the list."

Collapsing them would be sloppy, and it would also be unstable, because
ownership changes. Aesop moved from Natura to L'Oréal in 2023. The Ordinary
sits under Estée Lauder through DECIEM. If the two sentences were merged, a
corporate sale would silently change a product's political label with no
record of why.

---

## 6. The ontology pattern

In `vocabularies/brand-claims-pattern.ttl`. It reuses the **exact shape
already adopted from the halal flavouring ontology** and used for CosIng annex
restrictions:

```
thing  ->  listing  ->  authority
```

The listing is a first class individual, not an attribute. It carries
`prov:wasAttributedTo`, `dct:source`, `prov:generatedAtTime`, the tier and the
basis. The authority is its own entity, so two lists can be compared, dated,
or swapped.

This is the single strongest justification for the provenance model in the
whole thesis. Every other column is a fact somebody could verify. **This one is
a contested claim where the source *is* the information.** A system that
outputs `boycotted: yes` is taking a position. A system that outputs "listed
by this organisation, at this tier, for this stated reason, read on this date,
here is the link" is reporting, and lets the user decide.

The same pattern covers **cruelty free** and **organic**, which are also
claims by certifiers rather than properties of a formula. One design, three
problems solved.

---

## 7. Swapping the list

The dataset does not hardcode anybody's politics. To use a different source:

1. Replace `reference/boycott_claims.csv`
2. Run `py FINAL_PIPELINE/add_brand_claims.py`

New authority, new date, new basis, same seven columns. If you wanted to run
two lists side by side, the reified pattern in the TTL already allows a brand
to carry more than one listing.

---

## 8. Limits, stated plainly

**Ownership coverage is 24.6%.** This is the binding constraint, not the list.
Sprint 2 already had "check Wikidata brand coverage" on it, and Wikidata's
`parent organization` property would raise this substantially in one pass.
Until then, three quarters of the catalogue honestly reads `not_checked`.

**Lists disagree.** The BDS priority list and the crowd sourced app lists give
very different answers. Recording which one was used is the whole point.

**Positions change.** A listing is true as at a date, which is why every row
carries one.

**"Supports X" and "is listed as a target" are different questions.** I only
implemented the second, because it is the one with a published source. There
is no column anywhere in this dataset asserting what a company believes.

---

## Files

| File | What |
|---|---|
| `FINAL_PIPELINE/add_brand_claims.py` | The script |
| `repo/reference/brand_ownership.csv` | 118 brands to parents |
| `repo/reference/boycott_claims.csv` | 49 sourced claim rows |
| `repo/vocabularies/brand-claims-pattern.ttl` | The OWL pattern, parses clean, 49 triples |

Sources: [BDS Guide to Boycott](https://bdsmovement.net/Guide-to-BDS-Boycott), [Ethical Consumer Palestine boycott list](https://www.ethicalconsumer.org/ethical-campaigns-boycotts/palestine-boycott-list). Both read 10 September 2026.
