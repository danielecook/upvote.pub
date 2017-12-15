# -*- coding: utf-8 -*-

# Parse Pubs
import re
import glob
import eutils
from pdfx import PDFx
from metapub import PubMedFetcher
from metapub.crossref import CrossRef
from metapub.text_mining import findall_dois_in_text
from metapub.utils import asciify

import hashlib
import requests
import http.client, urllib.request, urllib.parse, urllib.error, base64


BUFFER_SIZE = 65336

def sha1_file(input):
    sha1 = hashlib.sha1()
    with open(input, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()





def pubmed_lone_result(words):
    """
        Attempts to identify PMID from 
        input terms. Can be a DOI or
        a bunch of words. Only returns
        true when there is one result.
    """
    ec = eutils.client.Client()
    # Get rid of the f'ing unicode
    words = asciify(words)
    result = ec.esearch(db='pubmed', term=words.decode('UTF-8'))
    if result.count == 1:
        return result.ids[0]
    else:
        return None


def filter_two(x):
    if len(x) < 3:
        return False
    else:
        return True


"""
def parse_pub(pdf_file):
    pub = None
    pubmed_fetcher = PubMedFetcher()
    pdf = PDFx(pdf_file)
    pdf_meta = pdf.get_metadata()
    if pdf_meta.get('crossmark') and pdf_meta['crossmark'].get('DOI'):
        doi = pdf_meta['crossmark']['DOI']
        pub = pubmed_fetcher.article_by_doi(doi).to_dict()
    else:
        # Identify DOIs from text
        doi_found = findall_dois_in_text(pdf.get_text())
        if len(doi_found) == 1:
            search_term = doi_found[0]
        else:
            search_term = ' '.join(list(filter(filter_two, [x.strip() for x in re.split("\W", pdf.get_text())]))[0:50])
        # If the pub cannot be identified then extract first 30 words and search on Microsoft Academic
        pmid = pubmed_lone_result(search_term)
        if pmid:
            pub = pubmed_fetcher.article_by_pmid(pmid)
    return pub
"""
