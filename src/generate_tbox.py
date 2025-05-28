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
    "person", "author", "reviewer", "journalEditor", "conferenceChair", 
    "paper", "keyword", "volume", "journal", "edition", "proceeding", 
    "event", "workshop", "conference", "city"
]
for c in classes:
    g.add((RES[c], RDF.type, RDFS.Class))

# --- SUBCLASSES --- #
g.add((RES["author"], RDFS.subClassOf, RES["person"]))
g.add((RES["reviewer"], RDFS.subClassOf, RES["author"]))  # Reviewers are relevant authors
g.add((RES["journalEditor"], RDFS.subClassOf, RES["person"]))
g.add((RES["conferenceChair"], RDFS.subClassOf, RES["person"]))
g.add((RES["workshop"], RDFS.subClassOf, RES["event"]))
g.add((RES["conference"], RDFS.subClassOf, RES["event"]))

# --- PROPERTIES --- #
properties = [
    # Person properties 
    ("name", "person", XSD.string),
    ("email", "person", XSD.string),
    ("authorId", "author", XSD.integer),
    
    # Editorial roles
    ("headsJournal", "journalEditor", "journal"),
    ("headsEvent", "conferenceChair", "edition"),
    
    # Authorship (matching your exact usage)
    ("writes", "author", "paper"),
    ("isCorrespondingAuthor", "author", "paper"),
    ("reviews", "reviewer", "paper"), 
    
    # Paper properties 
    ("title", "paper", XSD.string),
    ("abstract", "paper", XSD.string),
    ("doi", "paper", XSD.string),
    ("url", "paper", XSD.string),
    ("publicationDate", "paper", XSD.date),
    ("year", "paper", XSD.integer),
    ("citationCount", "paper", XSD.integer),
    ("referenceCount", "paper", XSD.integer),
    ("pages", "paper", XSD.string),
    
    # Paper relationships
    ("hasKeyword", "paper", "keyword"),
    ("cites", "paper", "paper"),
    ("citedBy", "paper", "paper"),  
    
    # Keyword properties 
    ("keywordId", "keyword", XSD.integer),
    
    # Journal publication 
    ("publishedInJournal", "paper", "journal"),
    ("publishedInVolume", "paper", "volume"),
    ("hasVolume", "journal", "volume"),
    ("volumeOf", "volume", "journal"),
    ("journalName", "journal", XSD.string),
    ("issn", "journal", XSD.string),
    ("journalUrl", "journal", XSD.string),
    ("volumeNumber", "volume", XSD.string),
    ("volumeYear", "volume", XSD.integer),
    
    # Conference/Workshop publication 
    ("presentedAt", "paper", "edition"),  # Used in ABox
    ("publishedInProceeding", "paper", "proceeding"),  # Used in ABox
    ("hasEdition", "event", "edition"),
    ("editionOf", "edition", "event"),  # Inverse relationship used in ABox
    ("hasProceeding", "edition", "proceeding"),
    
    # Event properties 
    ("eventName", "event", XSD.string),
    ("eventUrl", "event", XSD.string),
    ("eventId", "event", XSD.string),  # From conferences.csv ID
    
    # Edition properties (conference_editions.csv)
    ("editionId", "edition", XSD.string),
    ("editionName", "edition", XSD.string),
    ("heldInYear", "edition", XSD.integer),
    ("heldInCity", "edition", "city"),
    ("venueId", "edition", XSD.string),  
    
    # Proceeding properties
    ("proceedingName", "proceeding", XSD.string),
]

# --- SUBPROPERTIES --- #
g.add((RES["isCorrespondingAuthor"], RDFS.subPropertyOf, RES["writes"]))

# Add all properties with proper domains and ranges
for prop, domain, range_ in properties:
    g.add((RES[prop], RDF.type, RDF.Property))
    
    # Handle domain
    if isinstance(domain, str) and not str(domain).startswith("http://www.w3.org/2001/XMLSchema"):
        g.add((RES[prop], RDFS.domain, RES[domain]))
    else:
        g.add((RES[prop], RDFS.domain, domain))
    
    # Handle range
    if isinstance(range_, str) and not str(range_).startswith("http://www.w3.org/2001/XMLSchema"):
        g.add((RES[prop], RDFS.range, RES[range_]))
    else:
        g.add((RES[prop], RDFS.range, range_))

# --- GENERATE ONTOLOGY --- #
g.serialize(destination="tbox.ttl", format="turtle")
g.serialize(destination="tbox.rdfs", format="xml")

print("TBox generated and saved as tbox.ttl and tbox.rdfs")
print(f"Total triples in TBox: {len(g)}")

# Verification: Print key relationships
print("\nClass hierarchies:")
for s, p, o in g.triples((None, RDFS.subClassOf, None)):
    print(f"  {s.split('#')[-1]} → {o.split('#')[-1]}")

print("\nSubproperties:")
for s, p, o in g.triples((None, RDFS.subPropertyOf, None)):
    if o != RDF.Property:
        print(f"  {s.split('#')[-1]} → {o.split('#')[-1]}")

print(f"\nDefined {len(properties)} properties")