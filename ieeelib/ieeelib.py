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


GOOGLE_SCHOLAR_URL = "https://scholar.google.com"
ACM_SEARCH_URL = "https://dl.acm.org/results.cfm"
ACM_REFERENCE_URL = "https://dl.acm.org/exportformats.cfm"

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


def convert_pdf_to_txt(pdf, startpage=None):
    """Convert a pdf file to text and return the text.

    This method requires pdftotext to be installed.

    Parameters
    ----------
    pdf : str
        path to pdf file
    startpage : int, optional
        the first page we try to convert

    Returns
    -------
    str
        the converted text

    """
    if startpage is not None:
        startpageargs = ['-f', str(startpage)]
    else:
        startpageargs = []
    stdout = subprocess.Popen(["pdftotext", "-q"] + startpageargs + [pdf, "-"],
                              stdout=subprocess.PIPE).communicate()[0]
    # python2 and 3
    if not isinstance(stdout, str):
        stdout = stdout.decode()
    return stdout


def pdflookup(pdf, allresults, outformat, startpage=None):
    """Look a pdf up on google scholar and return bibtex items.

    Paramters
    ---------
    pdf : str
        path to the pdf file
    allresults : bool
        return all results or only the first (i.e. best one)
    outformat : int
        the output format of the citations
    startpage : int
        first page to start reading from

    Returns
    -------
    List[str]
        the list with citations

    """
    txt = convert_pdf_to_txt(pdf, startpage)
    # remove all non alphanumeric characters
    txt = re.sub("\W", " ", txt)
    words = txt.strip().split()[:20]
    gsquery = " ".join(words)
    bibtexlist = query(gsquery, outformat, allresults)
    return bibtexlist


def _get_bib_element(bibitem, element):
    """Return element from bibitem or None.

    Paramteters
    -----------
    bibitem :
    element :

    Returns
    -------

    """
    lst = [i.strip() for i in bibitem.split("\n")]
    for i in lst:
        if i.startswith(element):
            value = i.split("=", 1)[-1]
            value = value.strip()
            while value.endswith(','):
                value = value[:-1]
            while value.startswith('{') or value.startswith('"'):
                value = value[1:-1]
            return value
    return None


def rename_file(pdf, bibitem):
    """Attempt to rename pdf according to bibitem.

    """
    year = _get_bib_element(bibitem, "year")
    author = _get_bib_element(bibitem, "author")
    if author:
        author = author.split(",")[0]
    title = _get_bib_element(bibitem, "title")
    l = [i for i in (year, author, title) if i]
    filename = "-".join(l) + ".pdf"
    newfile = pdf.replace(os.path.basename(pdf), filename)
    logger.info('Renaming {in_} to {out}'.format(in_=pdf, out=newfile))
    os.rename(pdf, newfile)
