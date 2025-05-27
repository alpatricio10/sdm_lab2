from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import random
from datetime import datetime, date
import pandas as pd
import string

g = Graph()

# Define namespaces
RES = Namespace("http://research.org/research#")
g.bind("res", RES)

# --- HELPER FUNCTIONS --- #
def generate_email(name):
    """Generate a random email from a name"""
    email_name = name.lower().split()[0]
    random_num = random.randint(100, 999)
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "university.edu"]
    return f"{email_name}{random_num}@{random.choice(domains)}"

def clean_string_for_uri(s):
    """Clean a string to be URI-safe"""
    return str(s).strip().replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_").replace(":", "_")

def generate_city_name():
    """Generate a random city name"""
    cities = ["New York", "London", "Paris", "Tokyo", "Berlin", "Sydney", "Toronto", 
              "Barcelona", "Amsterdam", "Vienna", "Singapore", "Seoul", "Boston", 
              "San Francisco", "Munich", "Stockholm", "Copenhagen", "Zurich"]
    return random.choice(cities)

# --- DATA LOADING --- #
print("Loading data...")
try:
    author_paper_df = pd.read_csv('../data/author_paper_relationship_concat.csv')
    authors_df = pd.read_csv('../data/Author_nodes.csv')
    papers_df = pd.read_csv('../data/Paper_nodes.csv')
    reviews_df = pd.read_csv('../data/reviews.csv')
    references_df = pd.read_csv('../data/references.csv')
    keywords_df = pd.read_csv('../data/fields_of_study.csv')
    paper_keywords_df = pd.read_csv('../data/paper_field_relationship_concat.csv')
    journal_papers_df = pd.read_csv('../data/Journal_papers.csv')
    conference_papers_df = pd.read_csv('../data/Conference_papers.csv')
    conferences_df = pd.read_csv('../data/conferences.csv')
    conference_editions_df = pd.read_csv('../data/conference_editions.csv')
    journals_df = pd.read_csv('../data/journals.csv')
    print("All data files loaded successfully!")
except FileNotFoundError as e:
    print(f"Error loading data: {e}")
    print("Please ensure all data files are in the '../data/' directory")
    exit(1)

# Global sets to track instances (prevent duplicates)
author_instances = set()
paper_instances = set()
reviewer_instances = set()
journal_instances = set()
volume_instances = set()
conference_instances = set()
workshop_instances = set()
edition_instances = set()
city_instances = set()
proceeding_instances = set()

print("Creating authors and papers...")

# --- CREATE AUTHORS AND PAPERS WITH RELATIONSHIPS --- #
# author_paper_relationship_concat.csv
for _, row in author_paper_df.iterrows():
    paper_doi = str(row['DOI']).strip()
    # author_id_num = int(row['Author_ID'])
    if pd.notna(row['Author_ID']):
        author_id_num = int(row['Author_ID'])
        # continue with processing...
    else:
        continue  # skip this row

    
    paper_id = f"paper_{clean_string_for_uri(paper_doi)}"
    author_id = f"author_{author_id_num}"
    
    paper = RES[paper_id]
    author = RES[author_id]
    
    # Add Author Info (only once per author)
    if author_id not in author_instances:
        author_info = authors_df[authors_df['Author_ID'] == author_id_num]
        if not author_info.empty:
            author_row = author_info.iloc[0]
            name = str(author_row['Author_Name']).strip()
            email = generate_email(name)
            
            g.add((author, RES.name, Literal(name)))
            g.add((author, RES.email, Literal(email)))
            g.add((author, RES.authorId, Literal(author_id_num, datatype=XSD.integer)))
            
            author_instances.add(author_id)
    
    # Add Paper Info (only once per paper)
    if paper_id not in paper_instances:
        paper_info = papers_df[papers_df['DOI'] == paper_doi]
        if not paper_info.empty:
            paper_row = paper_info.iloc[0]
            
            g.add((paper, RES.title, Literal(str(paper_row['Title']).strip())))
            g.add((paper, RES.doi, Literal(paper_doi)))
            
            if pd.notna(paper_row.get('Abstract')):
                g.add((paper, RES.abstract, Literal(str(paper_row['Abstract']).strip())))
            if pd.notna(paper_row.get('Citations')):
                g.add((paper, RES.citationCount, Literal(int(paper_row['Citations']), datatype=XSD.integer)))
            if pd.notna(paper_row.get('References')):
                g.add((paper, RES.referenceCount, Literal(int(paper_row['References']), datatype=XSD.integer)))
            if pd.notna(paper_row.get('URL')):
                g.add((paper, RES.url, Literal(str(paper_row['URL']).strip())))
            if pd.notna(paper_row.get('Year')):
                g.add((paper, RES.year, Literal(int(paper_row['Year']), datatype=XSD.integer)))
            if pd.notna(paper_row.get('publicationDate')):
                pub_date_str = str(paper_row['publicationDate'])[:10]  # YYYY-MM-DD
                g.add((paper, RES.publicationDate, Literal(pub_date_str, datatype=XSD.date)))
            
            paper_instances.add(paper_id)
    
    # Create authorship relationships 
    corresponding = row.get('Corresponding', False)
    if pd.notna(corresponding) and corresponding == True:
        g.add((author, RES.isCorrespondingAuthor, paper))
    else:
        g.add((author, RES.writes, paper))

print(f"Created {len(author_instances)} authors and {len(paper_instances)} papers")

# --- CREATE REVIEW RELATIONSHIPS --- #
print("Creating review relationships...")
for _, row in reviews_df.iterrows():
    # reviewer_id_num = int(row['Reviewer_ID'])
    if pd.notna(row['Reviewer_ID']):
        reviewer_id_num = int(row['Reviewer_ID'])
        # continue with processing...
    else:
        continue  # skip this row
    
    paper_doi = str(row['Paper_DOI']).strip()
    
    reviewer_id = f"author_{reviewer_id_num}"
    paper_id = f"paper_{clean_string_for_uri(paper_doi)}"
    
    # Only create review if both reviewer and paper exist in our data
    if reviewer_id in author_instances and paper_id in paper_instances:
        reviewer = RES[reviewer_id]
        paper = RES[paper_id]
        
        g.add((reviewer, RES.reviews, paper))
        reviewer_instances.add(reviewer_id)

print(f"Created review relationships for {len(reviewer_instances)} reviewers")

# --- CREATE CITATION RELATIONSHIPS --- #
print("Creating citation relationships...")
citation_count = 0
for _, row in references_df.iterrows():
    citing_doi = str(row['Paper_DOI']).strip()
    cited_doi = str(row['Reference_DOI']).strip()
    
    citing_paper_id = f"paper_{clean_string_for_uri(citing_doi)}"
    cited_paper_id = f"paper_{clean_string_for_uri(cited_doi)}"
    
    citing_paper = RES[citing_paper_id]
    cited_paper = RES[cited_paper_id]
    
    # Add citation relationships (both directions for better querying)
    g.add((citing_paper, RES.cites, cited_paper))
    g.add((cited_paper, RES.citedBy, citing_paper))
    citation_count += 1

print(f"Created {citation_count} citation relationships")

# --- CREATE KEYWORDS --- #
print("Creating keywords...")
keyword_instances = {}
for _, row in keywords_df.iterrows():
    field_id = int(row['Field_ID'])
    field_name = str(row['Field_Name']).strip().replace(" ", "_")
    keyword = RES[field_name]
    
    g.add((keyword, RES.keywordId, Literal(field_id, datatype=XSD.integer)))
    
    keyword_instances[field_id] = keyword

# Link papers to keywords
keyword_links = 0
for _, row in paper_keywords_df.iterrows():
    field_id = int(row['Field_ID'])
    paper_doi = str(row['DOI']).strip()
    
    if field_id in keyword_instances:
        keyword = keyword_instances[field_id]
        paper_id = f"paper_{clean_string_for_uri(paper_doi)}"
        paper = RES[paper_id]
        
        g.add((paper, RES.hasKeyword, keyword))
        keyword_links += 1

print(f"Created {len(keyword_instances)} keywords with {keyword_links} paper-keyword links")

# --- CREATE JOURNALS FROM journals.csv --- #
print("Creating journals...")
for _, row in journals_df.iterrows():
    journal_id_num = str(row['ID'])
    journal_id = f"journal_{journal_id_num}"
    journal = RES[journal_id]
    
    g.add((journal, RES.journalName, Literal(str(row['Name']).strip())))
    g.add((journal, RES.eventId, Literal(journal_id_num)))
    
    if pd.notna(row.get('issn')):
        g.add((journal, RES.issn, Literal(str(row['issn']).strip())))
    if pd.notna(row.get('url')):
        g.add((journal, RES.journalUrl, Literal(str(row['url']).strip())))
    
    journal_instances.add(journal_id)

print(f"Created {len(journal_instances)} journals")

# --- CREATE VOLUMES AND LINK JOURNAL PAPERS --- #
print("Creating volumes and linking journal papers...")
journal_paper_count = 0
for _, row in journal_papers_df.iterrows():
    paper_doi = str(row['DOI']).strip()
    venue_id = str(row['venue_id']).strip()
    
    # Skip papers with unknown venues
    if venue_id == 'Unknown' or pd.isna(row.get('venue_id')):
        continue
    
    journal_id = f"journal_{venue_id}"
    
    # Only process if journal exists
    if journal_id in journal_instances and pd.notna(row.get('volume')):
        journal = RES[journal_id]
        volume_str = str(row['volume']).strip()
        
        # Create unique volume ID
        volume_id = f"volume_{clean_string_for_uri(volume_str)}_{venue_id}"
        volume = RES[volume_id]
        
        # Create volume only once
        if volume_id not in volume_instances:
            g.add((journal, RES.hasVolume, volume))
            g.add((volume, RES.volumeOf, journal))
            g.add((volume, RES.volumeNumber, Literal(volume_str)))
            
            if pd.notna(row.get('Year')):
                g.add((volume, RES.volumeYear, Literal(int(row['Year']), datatype=XSD.integer)))
            
            # Assign random journal editor from existing authors
            if author_instances:
                editor_id = random.choice(list(author_instances))
                editor = RES[editor_id]
                g.add((editor, RES.headsJournal, journal))
            
            volume_instances.add(volume_id)
        
        # Link paper to volume and journal
        paper_id = f"paper_{clean_string_for_uri(paper_doi)}"
        paper = RES[paper_id]
        
        g.add((paper, RES.publishedInVolume, volume))
        g.add((paper, RES.publishedInJournal, journal))
        
        # Add pages if available
        if pd.notna(row.get('pages')):
            g.add((paper, RES.pages, Literal(str(row['pages']).strip())))
        
        journal_paper_count += 1

print(f"Created {len(volume_instances)} volumes and linked {journal_paper_count} journal papers")

# --- CREATE CONFERENCES FROM conferences.csv --- #
print("Creating conferences...")
for _, row in conferences_df.iterrows():
    conf_id_num = str(row['ID'])
    conference_id = f"conference_{conf_id_num}"
    conference = RES[conference_id]
    
    # Use exact property names from TBox
    g.add((conference, RES.eventName, Literal(str(row['Name']).strip())))
    g.add((conference, RES.eventId, Literal(conf_id_num)))
    
    if pd.notna(row.get('url')):
        g.add((conference, RES.eventUrl, Literal(str(row['url']).strip())))
    
    g.add((conference, RDF.type, RES["conference"]))
    conference_instances.add(conference_id)

print(f"Created {len(conference_instances)} conferences")

# --- CREATE WORKSHOPS (synthetic data) --- #
print("Creating workshops (synthetic data)...")
# Create workshops by duplicating some conferences
conference_list = list(conference_instances)
workshop_count = len(conference_list) // 3  # Create workshops for 1/3 of conferences

for i in range(workshop_count):
    original_conf_id = conference_list[i]
    conf_id_num = original_conf_id.split('_')[1]
    
    workshop_id = f"workshop_{conf_id_num}"
    workshop = RES[workshop_id]
    
    # Get original conference name and modify for workshop
    original_conf = RES[original_conf_id]
    for s, p, o in g.triples((original_conf, RES.eventName, None)):
        workshop_name = f"{str(o)} Workshop"
        g.add((workshop, RES.eventName, Literal(workshop_name)))
        break
    
    g.add((workshop, RES.eventId, Literal(str(conf_id_num))))
    g.add((workshop, RDF.type, RES["workshop"]))
    workshop_instances.add(workshop_id)

print(f"Created {len(workshop_instances)} workshops")

# --- CREATE EDITIONS FROM conference_editions.csv --- #
print("Creating editions...")
conference_papers_list = conference_papers_df['DOI'].tolist()
random.shuffle(conference_papers_list)
workshop_paper_dois = set(conference_papers_list[:len(conference_papers_list)//3])  # 1/3 for workshops

for _, row in conference_editions_df.iterrows():
    venue_id = str(row['Venue_ID']).strip()
    edition_id_num = str(row['Edition_ID'])
    
    # Skip unknown venues
    if venue_id == 'Unknown':
        continue
    
    edition_id = f"edition_{edition_id_num}"
    edition = RES[edition_id]
    
    # Use exact property names from TBox
    g.add((edition, RES.editionId, Literal(edition_id_num)))
    g.add((edition, RES.editionName, Literal(str(row['Conference_Edition_Name']).strip())))
    
    if pd.notna(row.get('Year')):
        g.add((edition, RES.heldInYear, Literal(int(row['Year']), datatype=XSD.integer)))
    
    # Create city
    city_name = generate_city_name()
    city_id = f"city_{clean_string_for_uri(city_name)}"
    city = RES[city_id]
    
    if city_id not in city_instances:
        city_instances.add(city_id)
    
    g.add((edition, RES.heldInCity, city))
    
    # Determine if this edition belongs to conference or workshop
    edition_papers = conference_papers_df[conference_papers_df['Edition_id'] == str(edition_id_num)]
    has_workshop_papers = any(doi in workshop_paper_dois for doi in edition_papers['DOI'])
    
    if has_workshop_papers and f"workshop_{venue_id}" in workshop_instances:
        # Link to workshop
        workshop = RES[f"workshop_{venue_id}"]
        g.add((workshop, RES.hasEdition, edition))
        g.add((edition, RES.editionOf, workshop))
    else:
        # Link to conference
        conference_id = f"conference_{venue_id}"
        if conference_id in conference_instances:
            conference = RES[conference_id]
            g.add((conference, RES.hasEdition, edition))
            g.add((edition, RES.editionOf, conference))
    
    # Assign conference chair
    if author_instances:
        chair_id = random.choice(list(author_instances))
        chair = RES[chair_id]
        g.add((chair, RES.headsEvent, edition))
    
    # Create proceeding
    proceeding_id = f"proceeding_{edition_id_num}"
    proceeding = RES[proceeding_id]
    
    g.add((edition, RES.hasProceeding, proceeding))
    g.add((proceeding, RES.proceedingName, Literal(f"Proceedings of {str(row['Conference_Edition_Name']).strip()}")))
    
    edition_instances.add(edition_id)
    proceeding_instances.add(proceeding_id)

print(f"Created {len(edition_instances)} editions and {len(proceeding_instances)} proceedings")

# --- LINK CONFERENCE PAPERS TO EDITIONS --- #
print("Linking conference papers to editions...")
conference_paper_count = 0
for _, row in conference_papers_df.iterrows():
    paper_doi = str(row['DOI']).strip()
    edition_id_str = str(row['Edition_id']).strip()
    
    if edition_id_str != 'nan' and pd.notna(row.get('Edition_id')):
        paper_id = f"paper_{clean_string_for_uri(paper_doi)}"
        edition_id = f"edition_{edition_id_str}"
        proceeding_id = f"proceeding_{edition_id_str}"
        
        if edition_id in edition_instances:
            paper = RES[paper_id]
            edition = RES[edition_id]
            proceeding = RES[proceeding_id]
            
            g.add((paper, RES.presentedAt, edition))
            g.add((paper, RES.publishedInProceeding, proceeding))
            
            # Add pages if available
            if pd.notna(row.get('pages')):
                g.add((paper, RES.pages, Literal(str(row['pages']).strip())))
            
            conference_paper_count += 1

print(f"Linked {conference_paper_count} conference papers to editions")

# --- GENERATE ONTOLOGY --- #
print("Serializing graph...")
g.serialize(destination="abox.ttl", format="turtle")
g.serialize(destination="abox.rdfs", format="xml")

print(f"\nABox generation complete!")
print(f"STATISTICS:")
print(f"   Total triples: {len(g)}")
print(f"   Authors: {len(author_instances)}")
print(f"   Papers: {len(paper_instances)}")
print(f"   Reviewers: {len(reviewer_instances)}")
print(f"   Keywords: {len(keyword_instances)}")
print(f"   Journals: {len(journal_instances)}")
print(f"   Volumes: {len(volume_instances)}")
print(f"   Conferences: {len(conference_instances)}")
print(f"   Workshops: {len(workshop_instances)}")
print(f"   Editions: {len(edition_instances)}")
print(f"   Cities: {len(city_instances)}")
print(f"   Proceedings: {len(proceeding_instances)}")
print(f"   Citations: {citation_count}")
print(f"   Journal papers: {journal_paper_count}")
print(f"   Conference papers: {conference_paper_count}")

print(f"\n FILES GENERATED:")
print(f"   - abox.ttl")
print(f"   - abox.rdfs")
