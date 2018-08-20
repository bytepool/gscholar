#!/usr/bin/env python3
"""
Scientific Bibliography Querying Tool

A simple tool to query various scientific citation databases, returning bibtex information.
It is being developed to be used in a systematic mapping study / systematic literature review.
"""

import os
import json
import bibtexparser
from urllib.request import quote

import ieeelib
import ieeelib.ieeeresultparser as ieeeparser
import querylib

from utils import dotdict
from sbqt_errors import *

results_dir = "query_results"
api_dir = "api-keys"
max_records = 25



def construct_queries():
    """
    """
    queries = []
    queries.append(quote("My Test Query"))
    return queries

def save_json(query_results, mask):
    """
    """
    query_res_filename = "%s-mask=%d.json" % (query, mask)
    query_res_full_path = os.path.join(results_dir, query_res_filename)
    
    with open(query_res_full_path, "wb") as res_file:
        res_file.write(query_result)
        print("Query results written to json file %s." % query_res_full_path)

def load_api_key(filename):
    """
    Read an api key (used by e.g., IEEE Xplore) from disk and return it as a string. 
    """
    api_full_path = os.path.join(api_dir, filename)
    
    with open(api_full_path, "r") as apifile:
        api_key = apifile.read().strip()

    return api_key


def ieee_query():
    """
    Run queries on the IEEE Xplore DB using their REST API. Requires a valid API key. 
    """
    api_key = load_api_key("ieee.key")

    queries = construct_queries()

    fields_mask = ieeelib.SEARCH_FIELD_ABSTRACT | ieeelib.SEARCH_FIELD_DOC_TITLE

    for query in queries:
        query_result = ieeelib.query(query, api_key, max_records=max_records, fields_mask=fields_mask)
        #save_json(query_result, fields_mask)
        ieee_data = json.loads(query_result)

        if not ieee_data:
            print("No data returned for query %s. Aborting." % query, file=sys.stderr)
            exit(NO_DATA_ERROR)
            
        ieee_data = dotdict(ieee_data)
        bibtex_str = bibtexparser.dumps(ieeeparser.bibtexize(ieee_data))
        #write_bibtex(ieee_data, query, fields_mask)
            
        total_records = ieee_data.total_records
        next_start_record = 1 + max_records
        
        while next_start_record < total_records:
            #print("DEBUG: Retrieving records starting at %s..." % next_start_record)
            next_start_record = next_start_record + max_records
            query_result = ieeelib.query(query, api_key, max_records=max_records, fields_mask=fields_mask)
            ieee_data = json.loads(query_result)
            if not ieee_data:
                print("Something went wrong while retrieving records starting at %s for query. Aborting." % (next_start_record, query), file=sys.stderr)
                exit(NO_DATA_ERROR)
            
            ieee_data = dotdict(ieee_data)
            bibtex_str = bibtex_str + bibtexparser.dumps(ieeeparser.bibtexize(ieee_data))
            #write_bibtex(ieee_data, query, fields_mask)

        write_bibtex_str(bibtex_str, query, fields_mask)
    print ('ieee_query() for query "%s" finished.' % query)

            
def write_bibtex(data, query, mask):
    """
    """
    bibtex_db = ieeeparser.bibtexize(data)
            
    bibtex_filename =  "%s-mask=%d.bib" % (query, mask)
    bibtex_full_path = os.path.join(results_dir, bibtex_filename)
            
    ieeeparser.append_to_bibfile(bibtex_db, bibtex_full_path)
    
def write_bibtex_str(bibtex_str, query, mask):
    """
    """
    bibtex_filename =  "%s-mask=%d.bib" % (query, mask)
    bibtex_full_path = os.path.join(results_dir, bibtex_filename)

    with open(bibtex_full_path, "a") as f:
        f.write(bibtex_str)
    

def __main__():
    ieee_query()
    
if __name__ == "__main__":
    __main__()
    
