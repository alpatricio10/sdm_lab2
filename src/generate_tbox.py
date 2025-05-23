from rdflib import Graph, Namespace, URIRef, RDF, RDFS, Literal
from rdflib.namespace import XSD

g = Graph()

# --- NAMESPACE --- #
RES = Namespace("http://research.org/research#")
g.bind("res", RES)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)


# --- CLASSES --- #
classes = [
    "person","author", "reviewer", "journal_editor", "conference_chair", "paper", "keyword",
    "volume", "journal", "edition", "proceeding", "event", "workshop", "conference", "city"
]
for c in classes:
    g.add((RES[c], RDF.type, RDFS.Class))


# --- SUBCLASSES --- #
g.add((RES["author"], RDFS.subClassOf, RES["person"]))
g.add((RES["reviewer"], RDFS.subClassOf, RES["person"]))
g.add((RES["journal_editor"], RDFS.subClassOf, RES["person"]))
g.add((RES["conference_chair"], RDFS.subClassOf, RES["person"]))
g.add((RES["workshop"], RDFS.subClassOf, RES["event"]))
g.add((RES["conference"], RDFS.subClassOf, RES["event"]))

# --- PROPERTIES --- #
# Defines the domain and the range
properties = [
    # Person
    ("name", "person", XSD.string),
    ("email", "person", XSD.string),
    # add more attributes

    # Editor
    ("headsJournal", "journal_editor", "journal"),

    # conference_chair
    ("headsEvent", "conference_chair", "event"),

    # Author
    ("writes", "author", "paper"),

    # Paper
    ("hasKeyword", "paper", "keyword"),
    ("title", "paper", XSD.string),
    ("abstract", "paper", XSD.string),
    ("doi", "paper", XSD.string),
    ("url", "paper", XSD.string),
    ("citation_count", "paper", XSD.int),
    ("cites", "paper", "paper"),
    ("has_corresponding_author", "paper", "author"),
    ("reviewed_by", "paper", "reviewer"),

    # Keyword
    # ("keyword_name", "keyword", XSD.string),

    # Paper / Journal
    ("published_in_volume", "paper", "volume"),
    ("volume_number", "volume", XSD.int),
    ("volume_year", "volume", XSD.int),
    ("has_volume", "journal", "volume"),
    ("journal_name", "journal", XSD.string),

    # Paper / Event
    ("presented_in_edition", "paper", "edition"),
    ("has_edition", "event", "edition"),
    ("event_name", "event", XSD.string),
    ("has_proceeding", "edition", "proceeding"),
    ("proceeding_name", "proceeding", XSD.string),
    ("heldInCity", "edition", "city"),
    # ("cityName", "city", XSD.string),
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
g.serialize(destination="tbox.ttl", format="turtle")
g.serialize(destination="tbox.rdfs", format="xml")

print("TBox generated and saved as tbox.ttl and tbox.rdfs")