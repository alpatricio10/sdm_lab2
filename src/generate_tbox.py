from rdflib import Graph, Namespace, URIRef, RDF, RDFS, Literal
from rdflib.namespace import XSD

g = Graph()

# --- NAMESPACE --- #
RES = Namespace("http://research.org/research#")
g.bind("res", RES)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)


# --- CLASSES --- #
# Here for completeness, but commented out since this should be inferred in GraphDB (I think)
classes = [
    "author", "reviewer", "paper", "keyword",
    "volume", "journal", "edition", "proceeding",
    "conference", "city"
]
for c in classes:
    g.add((RES[c], RDF.type, RDFS.Class))


# --- SUBCLASSES --- #
g.add((RES["reviewer"], RDFS.subClassOf, RES["author"]))

# Workshop as subclass of conference?
# g.add((RES["workshop"], RDF.type, RDFS.Class))
# g.add((RES["workshop"], RDFS.subClassOf, RES["conference"]))


# --- PROPERTIES --- #
# Defines the domain and the range
properties = [
    # Author
    ("name", "author", XSD.string),
    ("email", "author", XSD.string),
    ("writes", "author", "paper"),

    # Paper
    ("about", "paper", "keyword"),
    ("title", "paper", XSD.string),
    ("abstract", "paper", XSD.string),
    ("doi", "paper", XSD.string),
    ("url", "paper", XSD.string),
    ("pages", "paper", XSD.int),
    ("citation_count", "paper", XSD.int),
    ("cites", "paper", "paper"),
    ("has_corresponding_author", "paper", "author"),
    ("reviewed_by", "paper", "reviewer"),

    # Keyword
    ("keyword_name", "keyword", XSD.string),

    # Paper / Journal
    ("published_in_volume", "paper", "volume"),
    ("volume_number", "volume", XSD.int),
    ("volume_year", "volume", XSD.int),
    ("has_volume", "journal", "volume"),
    ("journal_name", "journal", XSD.string),

    # Paper / Conference
    ("presented_in_edition", "paper", "edition"),
    ("has_edition", "conference", "edition"),
    ("conference_name", "conference", XSD.string),
    ("has_proceeding", "edition", "proceeding"),
    ("proceeding_name", "proceeding", XSD.string),
    ("heldInCity", "edition", "city"),
    ("cityName", "city", XSD.string),
    ("heldInYear", "edition", XSD.int),
    ("hostedBy", "edition", XSD.string),
]

for prop, domain, range_ in properties:
    g.add((RES[prop], RDF.type, RDF.Property))
    g.add((RES[prop], RDFS.domain, RES[domain] if isinstance(domain, str) and not str(domain).startswith("http://www.w3.org/2001/XMLSchema")  else domain))
    g.add((RES[prop], RDFS.range, RES[range_] if isinstance(range_, str) and not str(range_).startswith("http://www.w3.org/2001/XMLSchema") else range_))

# for prop, domain, range_ in properties:
#     g.add((RES[prop], RDF.type, RDF.Property))
#     g.add((RES[prop], RDFS.domain, RES[domain] if isinstance(domain, str) else domain))
#     g.add((RES[prop], RDFS.range, RES[range_] if isinstance(range_, str) else range_))


# --- GENERATE ONTOLOGY --- #
g.serialize(destination="ontology.ttl", format="turtle")
g.serialize(destination="ontology.rdfs", format="xml")

print("TBox generated and saved as ontology.ttl and ontology.rdfs")