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
    "person","author", "reviewer", "journalEditor", "conferenceChair", "paper", "keyword",
    "volume", "journal", "edition", "proceeding", "event", "workshop", "conference", "city"
]
for c in classes:
    g.add((RES[c], RDF.type, RDFS.Class))


# --- SUBCLASSES --- #
g.add((RES["author"], RDFS.subClassOf, RES["person"]))
# g.add((RES["reviewer"], RDFS.subClassOf, RES["person"]))
g.add((RES["reviewer"], RDFS.subClassOf, RES["author"]))
g.add((RES["journalEditor"], RDFS.subClassOf, RES["person"]))
g.add((RES["conferenceChair"], RDFS.subClassOf, RES["person"]))
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
    ("headsJournal", "journalEditor", "volume"),

    # conferenceChair
    ("headsEvent", "conferenceChair", "edition"),

    # Author
    ("writes", "author", "paper"),

    # Paper
    ("hasKeyword", "paper", "keyword"),
    ("title", "paper", XSD.string),
    ("abstract", "paper", XSD.string),
    ("doi", "paper", XSD.string),
    ("url", "paper", XSD.string),
    ("citationCount", "paper", XSD.int),
    ("cites", "paper", "paper"),
    ("isCorrespondingAuthor", "author", "paper"),
    ("reviewedBy", "paper", "reviewer"),

    # Keyword
    # ("keyword_name", "keyword", XSD.string),

    # Paper / Journal
    ("publishedInVolume", "paper", "volume"),
    ("volumeNumber", "volume", XSD.string),
    ("volumeYear", "volume", XSD.int),
    ("hasVolume", "journal", "volume"),
    ("journalName", "journal", XSD.string),

    # Paper / Event
    ("presentedInEdition", "paper", "edition"),
    ("hasEdition", "event", "edition"),
    ("eventName", "event", XSD.string),
    ("hasProceeding", "edition", "proceeding"),
    ("proceedingName", "proceeding", XSD.string),
    ("heldInCity", "edition", "city"),
    # ("cityName", "city", XSD.string),
    ("heldInYear", "edition", XSD.int),
    ("hostedBy", "edition", XSD.string),
]

# --- SUBPROPERTIES --- #
g.add((RES["isCorrespondingAuthor"], RDFS.subPropertyOf, RES["writes"]))

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