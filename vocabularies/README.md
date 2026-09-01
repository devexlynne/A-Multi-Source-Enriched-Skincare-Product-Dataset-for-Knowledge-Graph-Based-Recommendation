# Vocabularies I reuse

Four existing vocabularies, plus my own small profile file that ties them to
my data.

I do not keep copies of the full vocabularies in this repository. They are
maintained elsewhere, they change, and an ontology imports them by address
rather than by copying them. `fetch_vocabularies.py` downloads them into this
folder if you want them locally, and `.gitignore` keeps the downloads out of
version control.

## The four

| Prefix | Vocabulary | Official address | Download | Why I use it |
|---|---|---|---|---|
| `schema:` | schema.org | `https://schema.org/` | `https://schema.org/version/latest/schemaorg-current-https.ttl` | separates a `Product` from an `Offer`, which is how one cream can have four prices in four Beirut shops |
| `prov:` | PROV-O, W3C | `http://www.w3.org/ns/prov#` | `https://www.w3.org/ns/prov.ttl` | says where a claim came from, who made it, and when |
| `skos:` | SKOS, W3C | `http://www.w3.org/2004/02/skos/core#` | `https://www.w3.org/2009/08/skos-reference/skos.rdf` | turns my closed lists into concepts, so `Hydrating` and `Hydration` become one thing with two labels |
| `dcterms:` | Dublin Core Terms | `http://purl.org/dc/terms/` | `https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl` | dates and titles, used by PROV-O anyway |

CosIng is the fifth thing I reuse, but it is a register rather than a
vocabulary. It has no OWL file. I link to it by matching INCI names, which is
already done in the dataset.

OntoCosmetic is in `../papers/OntoCosmetic-30-withoutRules.owl`. I borrow its
ingredient type names and do not import it. Reasons in `../ONTOLOGY_REUSE.md`.

## My own file

`skincare-profile.ttl` is the only ontology file I wrote. It declares my
classes and properties, imports the four vocabularies above, and shows the two
ideas the papers gave me:

- a **defined class**, so the reasoner decides which products are safe for
  sensitive skin instead of me tagging them by hand
- **evidence levels** attached to claims, so a manufacturer's statement and my
  own inference are not the same kind of fact

Open it in Protégé. It is small on purpose.

## Licences

| Vocabulary | Licence |
|---|---|
| schema.org | Creative Commons Attribution-ShareAlike 3.0 |
| PROV-O | W3C Software and Document Notice and Licence |
| SKOS | W3C Software and Document Notice and Licence |
| Dublin Core | Creative Commons Attribution 4.0 |
| CosIng | European Commission, reusable with attribution |
