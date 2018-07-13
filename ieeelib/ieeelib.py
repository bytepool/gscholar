#!/usr/bin/env python3

"""
Library to query IEEE Xplore.

Call the method query with a string which contains the full search
string. Query will return a list of citations.
"""

try:
    # python 2
    from urllib2 import Request, urlopen, quote
except ImportError:
    # python 3
    from urllib.request import Request, urlopen, quote

try:
    # python 2
    from htmlentitydefs import name2codepoint
except ImportError:
    # python 3
    from html.entities import name2codepoint

import re
import os
import subprocess
import logging

IEEE_API_VERSION = 1
IEEE_URL = "http://ieeexploreapi.ieee.org/api/v%s/search/articles" % IEEE_API_VERSION

HEADERS = {'User-Agent': 'Mozilla/5.0'}

FORMAT_BIBTEX = 4
FORMAT_ENDNOTE = 3
FORMAT_REFMAN = 2
FORMAT_WENXIANWANG = 5

logger = logging.getLogger(__name__)

def query(searchstr, apikey="", outformat=FORMAT_BIBTEX, allresults=False):
    """Query IEEE Xplore.

    This method queries IEEE Xplore and returns a list of citations.

    Parameters
    ----------
    searchstr : str
        the query
    apikey : str
        the key to be able to use IEEE's API
    outformat : int, optional
        the output format of the citations. Default is bibtex.
    allresults : bool, optional
        return all results or only the first (i.e. best one)

    Returns
    -------
    result : list of strings
        the list with citations

    """
    logger.debug("Query: {sstring}".format(sstring=searchstr))
    searchstr = '?querytext=' + quote(searchstr)
    apistr = "&apikey=" + apikey
    url = IEEE_URL + searchstr + apistr
    
    header = HEADERS
    #header['Cookie'] = "GSP=CF=%d" % outformat
    request = Request(url, headers=header)
    response = urlopen(request)

    json = response.read()
    return json

