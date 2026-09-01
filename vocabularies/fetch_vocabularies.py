"""
Download the four vocabularies I reuse into this folder.

They are not committed to the repository. An ontology imports a vocabulary by
its address, and keeping a frozen copy of somebody else's maintained file in
my repository would go stale without me noticing.

Run this if you want them locally, for example to open one in Protege and read
the class definitions.

    py fetch_vocabularies.py
"""
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HEADERS = {'User-Agent': 'Mozilla/5.0',
           'Accept': 'text/turtle, application/rdf+xml;q=0.9, */*;q=0.8'}

SOURCES = [
    ('schemaorg.ttl',
     'https://schema.org/version/latest/schemaorg-current-https.ttl',
     'schema.org, the Product and Offer split'),
    ('prov.ttl', 'https://www.w3.org/ns/prov.ttl',
     'PROV-O, where a claim came from'),
    ('skos.rdf', 'https://www.w3.org/2009/08/skos-reference/skos.rdf',
     'SKOS, controlled lists'),
    ('dcterms.ttl',
     'https://www.dublincore.org/specifications/dublin-core/dcmi-terms/'
     'dublin_core_terms.ttl',
     'Dublin Core Terms, dates and titles'),
]


def main():
    for name, url, why in SOURCES:
        path = os.path.join(HERE, name)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            data = urllib.request.urlopen(req, timeout=60).read()
            open(path, 'wb').write(data)
            print(f'  saved {name:16s} {len(data):>9,} bytes   {why}')
        except Exception as e:
            print(f'  could not fetch {name}: {type(e).__name__}')
            print(f'    open {url} in a browser and save it here instead')


if __name__ == '__main__':
    main()
