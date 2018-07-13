"""
A library to parse the json results returned from the IEEE Xplore API.
"""

import re
import json
import bibtexparser

from utils import dotdict
from sbqt_errors import *


def __main__():
    testfile = "5G_sec.json"

    with open(testfile, "rt") as f:
        # parse json into python objects
        data = json.load(f)

    bibtex_db = bibtexize(data)
    
    with open("foo.bib", "w") as bf:
        bibtexparser.dump(bibtex_db, bf)

def append_to_bibfile(bibtex_db, filepath):
    """
    Append the entries in the given bibtex_db to the given file. 
    """
    with open(filepath, "a") as bf:
        bibtexparser.dump(bibtex_db, bf)

        
def bibtexize(data):
    """
    Takes the given json data (from IEEE Xplore's API), and returns a corresponding bibtex string.
    """
    ieee_data = dotdict(data)
    # ieee_data has 3 entries: total_records, total_searched and articles

    articles = ieee_data.articles
    entries = []
    
    for a in articles:
        a = dotdict(a)

        if a.content_type == "Journals" or a.content_type == "Early Access":
            bibtex = load_journal(a)
            entries.append(bibtex)
        elif a.content_type == "Books":
            bibtex = load_book(a)
            entries.append(bibtex)
        elif a.content_type == "Conferences":
            bibtex = load_inproceeding(a)
            entries.append(bibtex)
        else:
            print("Unknown content type while parsing IEEE data (json). Aborting.", file=sys.stderr)
            exit(UNKNOWN_ARTICLE_TYPE_ERROR)

    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    #print(db.entries)
    
    #writer = bibtexparser.bwriter.BibTexWriter()
    #with open('foo.bib', 'w') as bibfile:
    #    bibfile.write(writer.write(db))

    return db
    
def extract_year(date_string):
    """
    Extract a year from the given date string (assuming the year is always 4 digits long).
    """
    year_pattern = re.compile(r'\d{4}')
    year_match = year_pattern.search(date_string)
    if year_match:
        return year_match.group()
    else:
        return ""


def load_journal(entry):
    """
    """
    bibdict = {}
    
    bibdict["ENTRYTYPE"] = "article"
    bibdict["ID"] = "ieee" + str(entry.article_number)
    bibdict["title"] = str(entry.title)
    bibdict["abstract"] = str(entry.abstract)
    
    authors = [ a["full_name"] for a in entry.authors["authors"] ]
    bibdict["authors"] = (''.join('%s, ' % a for a in authors))[:-2]

    affiliations = [ a["affiliation"] if "affiliation" in a.keys() else None for a in entry.authors["authors"]]
    bibdict["affiliations"] = (''.join('%s, ' % a for a in affiliations))[:-2]
    
    bibdict["doi"] = str(entry.doi)
    bibdict["booktitle"] = str(entry.publication_title)
    
    bibdict["issn"] = str(entry.issn)
    bibdict["issue"] = str(entry.issue)
    bibdict["number"] = str(entry.publication_number)
    bibdict["volume"] = str(entry.volume)
    bibdict["publisher"] = str(entry.publisher)
    bibdict["pages"] = "%s -- %s" % (entry.start_page, entry.end_page)
    
    if "author_terms" in entry.index_terms.keys():
        keywords = entry.index_terms["author_terms"]["terms"] # list of author-provided keywords
        bibdict["keywords"] = (''.join('%s, ' % a for a in keywords))[:-2]

    bibdict["pdfurl"] = str(entry.pdf_url)

    year = entry.publication_date
    if year:
        bibdict["year"] = extract_year(year)
        
    return bibdict


def load_inproceeding(entry):
    """
    """
    bibdict = {}
    
    bibdict["ENTRYTYPE"] = "inproceeding"
    bibdict["ID"] = "ieee" + str(entry.article_number)

    bibdict["title"] = str(entry.title)
    bibdict["abstract"] = str(entry.abstract)

    authors = [ a["full_name"] for a in entry.authors["authors"] ]
    bibdict["authors"] = (''.join('%s, ' % a for a in authors))[:-2]

    affiliations = [ a["affiliation"] if "affiliation" in a.keys() else None for a in entry.authors["authors"]]
    bibdict["affiliations"] = (''.join('%s, ' % a for a in affiliations))[:-2]
    
    bibdict["doi"] = str(entry.doi)
    bibdict["booktitle"] = str(entry.publication_title)

    bibdict["conference_location"] = str(entry.conference_location)
    bibdict["conference_dates"] = str(entry.conference_dates)
    
    bibdict["isbn"] = str(entry.isbn)

    bibdict["publisher"] = str(entry.publisher)
    bibdict["pages"] = "%s -- %s" % (entry.start_page, entry.end_page)
    
    if "author_terms" in entry.index_terms.keys():
        keywords = entry.index_terms["author_terms"]["terms"] # list of author-provided keywords
        bibdict["keywords"] = (''.join('%s, ' % a for a in keywords))[:-2]

    bibdict["pdfurl"] = str(entry.pdf_url)

    year = entry.conference_dates
    if year:
        bibdict["year"] = extract_year(year)

    return bibdict


def load_book(entry):
    """
    """
    bibdict = {}
    
    bibdict["ENTRYTYPE"] = "book"
    bibdict["ID"] = "ieee" + str(entry.article_number)

    bibdict["title"] = str(entry.publication_title)

    authors = [ a["full_name"] for a in entry.authors["authors"] ]
    bibdict["authors"] = (''.join('%s, ' % a for a in authors))[:-2]

    bibdict["doi"] = str(entry.doi)
    bibdict["chapter"] = str(entry.title)
    
    bibdict["isbn"] = str(entry.isbn)
    bibdict["publisher"] = str(entry.publisher)
    
    bibdict["pdfurl"] = str(entry.pdf_url)
    return bibdict
        
    
if __name__ == "__main__":
    __main__()
    
