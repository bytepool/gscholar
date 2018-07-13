#!/usr/bin/env python3
"""
Simple library to create all possible search queries of a given list of combinable terms. 
"""

import data

DBLP = "DBLP"
IEEE = "IEEE Xplore"
SCHOLAR = "Google Scholar"
ACM = "ACM Digital Library"

db = IEEE

AND = " AND "
OR = " OR "
        

def construct_queries(terms, operator):
    """
    Combines terms in a given list of lists. You could also think of it as set multiplication. 

    terms
        A list of lists. Each of the inner lists is a bag of terms that should be combined with the other bags.

    operator
        The operator with which the terms should be linked. E.g., " " or " AND ". 

    Example
        >>> construct_queries([['A', 'B'],['C','D'],['E','F']], " ")
        ['A C E', 'A C F', 'A D E', 'A D F', 'B C E', 'B C F', 'B D E', 'B D F']

    Returns a list of queries.
    """
    queries = []

    nr_of_bags = len(terms)
    if nr_of_bags < 1:
        raise RuntimeError("Too few terms given!")
    elif nr_of_bags == 1:
        return terms[0]

    start = terms[0]
    second_index = 1
    
    while second_index < nr_of_bags:
        result = []
        add = terms[second_index]
    
        for start_term in start:
            for add_term in add:
                result.append(start_term + operator + add_term)
    
        start = result
        second_index = second_index + 1
    
    return result


def __main__():
    """Constructs all possible queries given the input terms."""

    queries = construct_queries(data.search_terms, " AND ")

    for query in queries:
        print(query)
    

if __name__== "__main__":
    __main__()
