# SDM Lab 2
This is the codebase for Semantic Data Management Lab Assignment21 at UPC. It was developed by Adrian Patricio and Hadiqa Alamdar Bukhari.

## Important Files
- generate_tbox.py: This script creates all the class and property definitions required for the TBOX.
- generate_abox.py: This script extracts data from Semantic Scholar and processes them into triples for ingestion into the ABOX. 

## How to Run
- Run generate_tbox.py and generate_abox.py separately. This will produce the rdfs files needed for importing into GraphDB.

## Notes
- The /data folder contains the raw csv files before processing into graph triples.
- The results will be generated in the same directory as the Python scripts.
