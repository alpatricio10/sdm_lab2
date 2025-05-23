from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import random
from datetime import datetime
import pandas as pd
import string

g = Graph()

# The TBOX can be loaded if we want to generate a combined ABOX/TBOX file.
# Otherwise, we can upload the TBOX and ABOX files to the graph separately.
# This will generate the same outcome.
# g.parse("ontology.rdfs", format="xml")

# Types are not defined for each created class, because it is already inferred from the properties.

# Define namespaces
RES = Namespace("http://research.org/research#")
g.bind("res", RES)

# --- HELPER FUNCTIONS --- #
def generate_email(name):
    """Generate a random email from a name"""
    email_name = name.lower().split()[0]
    random_num = random.randint(100, 999)
    
    # List of common email domains
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    
    return f"{email_name}{random_num}@{random.choice(domains)}"

# --- NODE CREATION FUNCTIONS --- #
# If we have time, we can separate functions for clarity, since the code below is a bit messy


# --- GENERATING ABOX--- #
# Read data from CSV files
author_paper_df = pd.read_csv('../data/author_paper_relationship_concat.csv')
authors_df = pd.read_csv('../data/Author_nodes.csv')
papers_df = pd.read_csv('../data/Paper_nodes.csv')

author_instances = set()

# Create author, paper and author-paper relationships
for _, row in author_paper_df.iterrows():
    paper_id = f"paper_{row['DOI']}"  
    author_id = f"author_{row['Author_ID']}"  

    paper = RES[paper_id]
    author = RES[author_id]

    # Add Author Info
    author_info = authors_df[authors_df['Author_ID'] == row['Author_ID']]
    if not author_info.empty:
        author_row = author_info.iloc[0]

        name = author_row['Author_Name']
        email = generate_email(name)
        g.add((author, RES.name, Literal(name)))
        g.add((author, RES.email, Literal(email)))

        # Add author to set
        author_instances.add(author_id)

    # Add Paper Info
    paper_info = papers_df[papers_df['DOI'] == row['DOI']]
    if not paper_info.empty:
        paper_row = paper_info.iloc[0]

        g.add((paper, RES.title, Literal(paper_row['Title'])))
        g.add((paper, RES.doi, Literal(paper_row['DOI'])))
        if pd.notna(paper_row.get('Abstract')):
            g.add((paper, RES.abstract, Literal(paper_row['Abstract'])))
        if pd.notna(paper_row.get('Citations')):
            g.add((paper, RES.citationCount, Literal(paper_row['Citations'], datatype=XSD.integer)))
        if pd.notna(paper_row.get('URL')):
            g.add((paper, RES.url, Literal(paper_row['URL'])))

    # Create corresponding author or writes relationship
    corresponding = row['Corresponding']
    if corresponding == True:
        g.add((author, RES.isCorrespondingAuthor, paper))
    else:
        g.add((author, RES.writes, paper))

# Create review decisions and relationships
reviews_df = pd.read_csv('../data/reviews_decisions.csv')
for _, row in reviews_df.iterrows():
    # Get reviewer
    # This assumes that the reviewer has already been created as an author
    reviewer_id = f"author_{row['Reviewer_ID']}"
    reviewer = RES[reviewer_id]

    # Get paper
    paper_id = f"paper_{row['Paper_DOI']}"
    paper = RES[paper_id]

    # Add review relationship
    g.add((paper, RES.reviewedBy, reviewer))

# Create cites relationship
references_df = pd.read_csv('../data/references.csv')
for _, row in references_df.iterrows():
    # Get citing paper
    citing_paper_id = f"paper_{row['Paper_DOI']}"
    citing_paper = RES[citing_paper_id]

    # Get referenced paper
    referenced_paper_id = f"paper_{row['Reference_DOI']}"
    referenced_paper = RES[referenced_paper_id]

    # Add review relationship
    g.add((citing_paper, RES.cites, referenced_paper))

# Create keywords
keywords_df = pd.read_csv('../data/fields_of_study.csv')
keyword_instances = {}
for _, row in keywords_df.iterrows():
    # Clean the keyword name by removing extra spaces and special characters
    keyword = row['Field_Name'].strip().replace(" ", "_").replace("-", "_")
    keyword_node = RES[keyword]
    keyword_instances[row['Field_ID']] = keyword_node

paper_keywords_df = pd.read_csv('../data/paper_field_relationship_concat.csv')
for _, row in paper_keywords_df.iterrows():
    # get keyword
    keyword = keyword_instances[row['Field_ID']]
    
    # Get paper
    paper_id = f"paper_{row['DOI']}"
    paper = RES[paper_id]

    # Add keyword to paper
    g.add((paper, RES.hasKeyword, keyword))

# Create journals
journals_df = pd.read_csv('../data/Journal_papers.csv')
volume_instances = set()
journal_instances = set()
for _, row in journals_df.iterrows():
    # Get volume
    # If the volume is not available, we cannot add it to the graph
    if pd.notna(row.get('volume')):
        # Get journal
        # If the journal has already been added, we don't need to add it again
        journal_id = f"journal{row['venue_id']}"
        journal = RES[journal_id]
        if journal_id not in journal_instances:
            journal_name = row['Venue']
            g.add((journal, RES.journalName, Literal(journal_name)))
            journal_instances.add(journal_id)

        # Get volume
        # If the volume has already been added, we don't need to add it again
        volume_id = f"volume_{row['volume'].strip().replace(" ", "_").replace("-", "_")}_{row['venue_id']}"
        volume = RES[volume_id]
        if volume_id not in volume_instances:
            g.add((journal, RES.hasVolume, volume))
            g.add((volume, RES.volumeNumber, Literal(row['volume'])))
            g.add((volume, RES.volumeYear, Literal(row['Year'], datatype=XSD.integer)))
            volume_instances.add(volume_id)

            # Assign Random Journal Editor
            journal_editor_id = random.choice(list(author_instances))
            journal_editor = RES[journal_editor_id]
            g.add((journal_editor, RES.headsJournal, volume))

        # Get paper
        paper_id = f"paper_{row['DOI']}"
        paper = RES[paper_id]

        g.add((paper, RES.publishedInVolume, volume))
            

# --- GENERATE ONTOLOGY --- #
g.serialize(destination="abox.ttl", format="turtle")
g.serialize(destination="abox.rdfs", format="xml")

print("ABox generated and saved as abox.ttl and abox.rdfs")