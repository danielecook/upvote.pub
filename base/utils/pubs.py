# -*- coding: utf-8 -*-

# Parse Pubs
import hashlib
import requests
import arxiv
from bs4 import BeautifulSoup
from metapub import CrossRef, PubMedFetcher
from metapub.base import MetaPubError
from dateutil.parser import parse
from subprocess import Popen
from tempfile import NamedTemporaryFile

THUMBNAIL_SIZE = 
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



def pdf_url_to_thumb(url, fname):
    """
        Generates a thumbnail
        for the URL provided for a PDF
    """
    response = requests.get(url, stream = True)
    out = NamedTemporaryFile(suffix=".pdf")
    with open(out.name, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)
    comm = ['convert', '-thumbnail', '200', out.name + "[0]", fname]
    out, err = Popen(comm).communicate()
    return fname


def fetch_pubmed(pub_id, id_type = "pmid"):
    """
        Fetches and formats pub data from
        pubmed
    """
    pm = PubMedFetcher()
    if id_type == 'doi':
        try:
            result = pm.article_by_doi(pub_id)
        except (AttributeError, MetaPubError):
            return None
    elif id_type == "pmid":
        try:
            result = pm.article_by_pmid(pub_id)
        except AttributeError:
            return None
    elif id_type == "pmc":
        try:
            result = pm.article_by_pmcid(pub_id)
        except AttributeError:
            return None
    result = result.to_dict()

    # Set link using DOI
    if result.get('doi'):
        result['url'] = "http://dx.doi.org/" + result.get('doi')
    else:
        result['url'] = result.get('url')

    # Provide PDF if possible
    if result.get('pmc'):
        result['pdf_url'] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{result['pmc']}/pdf/{result['pii']}.pdf"

    out = {"pub_title": result.get('title'),
           "pub_authors": result.get('authors'),
           "pub_abstract": result.get('abstract'),
           "pub_doi": result.get('doi'),
           "pub_pmid": result.get('pmid'),
           "pub_pmcid": result.get('pmc'),
           "pub_url": result.get('url'),
           "pub_pdf_url": result.get('pdf_url'),
           "pub_journal": result.get('journal'),
           "pub_date": result['history'].get('pubmed')}
    return out


def fetch_doi(doi):
    """
        Fetches and parses information
        from a DOI.

        First tries pubmed.
    """

    pm_result = fetch_pubmed(doi, id_type = 'doi')
    if pm_result:
        return pm_result

    url = "http://dx.doi.org/" + doi
    headers = {"accept": "application/json"}
    r = requests.get(url, headers = headers)
    if r.status_code == 200:
        result = r.json()

        if result.get('author'):
            authors = [x['given'] + " " + x['family'] for x in result['author']]

        if result.get('published'):
            published = parse(result.get('published'))
        else:
            published = parse(result['indexed']['date-time'])
        
        # Abstracts can have tags. Remove them
        if result.get('abstract'):
            abstract = BeautifulSoup(result['abstract'], "lxml")
            result['abstract'] = abstract.get_text(strip=True)

        out = {"pub_title": result.get('title').strip(),
               "pub_authors": authors,
               "pub_abstract": result.get('abstract').strip(),
               "pub_doi": result.get('DOI'),
               "pub_url": result.get('URL'),
               "pub_pdf_url": result.get('pdf_url'),
               "pub_journal": result.get('journal_reference') or "arXiv",
               "pub_date": published}
        return out
    return None


def fetch_arxiv(arxiv_id):
    try:
        result = arxiv.query(id_list=[arxiv_id])[0]
    except Exception:
        return None

    out = {"pub_title": result.get('title'),
           "pub_authors": result.get('authors'),
           "pub_abstract": result.get('summary'),
           "pub_doi": result.get('doi'),
           "pub_url": result.get('arxiv_url'),
           "pub_pdf_url": result.get('pdf_url'),
           "pub_journal": result.get('journal_reference') or "arXiv",
           "pub_date": parse(result.get('published'))}
    return out


def id_type(pub_id):
    if re.match("(arXiv:)?[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?", pub_id, re.IGNORECASE):
        return 'arxiv'
    elif re.match("[a-z]+(\.[a-z]+)/[0-9]+", pub_id, re.IGNORECASE):
        return 'arxiv'
    elif re.match("PMC[0-9]+", pub_id):
        return 'pmc'
    elif re.match('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)', pub_id):
        return 'doi'
    elif re.match('[0-9]+', pub_id):
        return 'pmid'


id_type("28892780") # pubmed
id_type("PMC5012401") # pmc
id_type('10.1093/nar/gkw893') # doi
id_type("10.1016.12.31/nature.S0735-1097(98)2000/12/31/34:7-7") # complex doi

# Andersen
fetch_doi('10.1093/nar/gkw893')
fetch_doi('10.1101/125567')

# Bio arxiv
fetch_doi('10.1101/233270')

fetch_arxiv("1510.08002")

def parse_pub(pub_id):
    pass

