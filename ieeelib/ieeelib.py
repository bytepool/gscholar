#!/usr/bin/env python3
"""
Library to query IEEE Xplore.

Call the method query with a string which contains the full search
string. Query will return a list of citations.
"""

from urllib.request import Request, urlopen, quote
from html.entities import name2codepoint

import re
import os
import subprocess
import logging

IEEE_API_VERSION = 1
IEEE_URL = "http://ieeexploreapi.ieee.org/api/v%s/search/articles" % IEEE_API_VERSION

SEARCH_FIELD_NONE = 0
SEARCH_FIELD_ABSTRACT = 1
SEARCH_FIELD_DOC_TITLE = 2
SEARCH_FIELD_PUB_TITLE = 4
SEARCH_FIELD_AUTHORS = 8
SEARCH_FIELD_AFFILIATIONS = 16
SEARCH_FIELD_KEYWORDS = 32

SEARCH_FIELDS = {SEARCH_FIELD_ABSTRACT:'"Abstract"', SEARCH_FIELD_DOC_TITLE:'"Document Title"', SEARCH_FIELD_AUTHORS:'"Authors"', SEARCH_FIELD_PUB_TITLE:'"Publication Title"', SEARCH_FIELD_AFFILIATIONS:'"Author Affiliations"', SEARCH_FIELD_KEYWORDS:'"Author Keywords"'}

AND = " AND "
OR = " OR "

HEADERS = {'User-Agent': 'Mozilla/5.0'}

logger = logging.getLogger(__name__)

def determine_query_fields(fields_mask):
    """
    Determine which fields should be used in the query. 
    """
    fields = []

    if fields_mask & SEARCH_FIELD_ABSTRACT:
        fields.append(SEARCH_FIELDS[SEARCH_FIELD_ABSTRACT])
    if fields_mask & SEARCH_FIELD_PUB_TITLE:
        fields.append(SEARCH_FIELDS[SEARCH_FIELD_PUB_TITLE])
    if fields_mask & SEARCH_FIELD_DOC_TITLE:
        fields.append(SEARCH_FIELDS[SEARCH_FIELD_DOC_TITLE])
    if fields_mask & SEARCH_FIELD_AUTHORS:
        fields.append(SEARCH_FIELDS[SEARCH_FIELD_AUTHORS])
    if fields_mask & SEARCH_FIELD_AFFILIATIONS:
        fields.append(SEARCH_FIELDS[SEARCH_FIELD_AFFILIATIONS])
    if fields_mask & SEARCH_FIELD_KEYWORDS:
        fields.append(SEARCH_FIELDS[SEARCH_FIELD_KEYWORDS])

    return fields

def populate_query_fields(fields, search_str, operator):
    """
    Use the given list of fields 
    """
    base_param = "?querytext="
    if not fields:
        query = base_param + quote(search_str)
        return query

    query = base_param
    for field in fields:
        query = query + "(%s:%s)%s" % (quote(field), quote(search_str), quote(operator))

    len_op = len(quote(operator))
    return query[:-len_op]


def query(search_str, api_key="", start_record=1, max_records=200, start_year=None, fields_mask=SEARCH_FIELD_ABSTRACT, operator=AND):
    """Query IEEE Xplore.

    This method queries IEEE Xplore and returns a json string with the result. 

    Parameters
    ----------
    search_str : str
        the query
    api_key : str
        the key to be able to use IEEE's API
    start_record : int, optional
        the index of the first record which should be retrieved (used to "browse" through results)
    max_records : int, optional
        the number of records to return (default is 200, the maximum currently allowed by IEEE).

    Returns
    -------
    result : json string
        the json string with the result of the query
    """
    logger.debug("Query: {sstring}".format(sstring=search_str))

    fields = determine_query_fields(fields_mask)
    # query_str must be first param in URL
    query_str = populate_query_fields(fields, search_str, operator)
    
    #query_str = '?querytext=%s' % quote(search_str)
    #query_str = '?abstract=%s' % quote(search_str)
    #query_str = '?article_title=%s' % quote(search_str)
    #query_str = '?article_title=%s&abstract=%s' % (quote(search_str),quote(search_str))
    #field = '"Abstract"'
    #query_str = '?querytext=("%s":%s)' % (field, quote(search_str))
    
    start_record_str = "&start_record=%d" % start_record
    max_records_str = "&max_records=%d" % max_records
    if start_year:
        start_year_str = "&start_year=%d" % start_year
    else:
        start_year_str = ""

    api_str = "&apikey=%s" % quote(api_key) # last param in URL
    
    params = start_year_str + max_records_str + start_record_str
    url = IEEE_URL + query_str + params  + api_str
    #print("DEBUG: Query URL:", url)
    
    header = HEADERS
    #header['Cookie'] = "GSP=CF=%d" % outformat for google scholar
    request = Request(url, headers=header)
    response = urlopen(request)

    json = response.read()
    return json

