# -*- coding: utf-8 -*-

# Parse Pubs
import re
import requests
import arxiv
from bs4 import BeautifulSoup
from base import app
from logzero import logger
from base.threads.models import Thread
from bs4 import BeautifulSoup
from metapub import PubMedFetcher
from metapub.base import MetaPubError
from dateutil.parser import parse
from base.async.tasks import process_pdf_task
from sqlalchemy import or_


def clean_pub_id(pub_id):
    if pub_id:
        return pub_id.strip().upper().replace("ARXIV", "").replace("BIORXIV", "").replace(":", "")


def get_pub_thread(pub_id):
    """
    Get pub thread from the database
    """
    pub_id = pub_id.strip()
    pub_id_type = id_type(pub_id)

    thread = Thread.query.filter(getattr(Thread, 'pub_' + pub_id_type) == pub_id).first()
    return thread


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
        result['pdf_url'] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{result['pmc']}/pdf"
        result['pmc'] = "PMC" + result['pmc']

    out = {"pub_title": result.get('title'),
           "pub_authors": result.get('authors'),
           "pub_abstract": result.get('abstract'),
           "pub_doi": result.get('doi'),
           "pub_pmid": result.get('pmid'),
           "pub_pmc": result.get('pmc'),
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
           "pub_arxiv": arxiv_id,
           "pub_url": result.get('arxiv_url'),
           "pub_pdf_url": result.get('pdf_url'),
           "pub_journal": result.get('journal_reference') or "arXiv",
           "pub_date": parse(result.get('published'))}
    return out


def fetch_biorxiv(biorxiv_id):
    r = app.config.get('REDIS_DB')
    biorxiv_id = re.split("[: ]{1}", biorxiv_id.lower())[1]
    biorxiv_url = str(r.get('biorxiv:' + biorxiv_id), encoding='utf-8')
    biorxiv_resp = requests.get(biorxiv_url)
    b = BeautifulSoup(biorxiv_resp.content, 'lxml')
    doi_span = b.findAll('span', {'class': 'highwire-cite-metadata-doi'})
    if len(doi_span) > 0:
        doi = doi_span[0].text.replace('doi: https://doi.org/', '')
    pub = fetch_doi(doi)
    pub['pub_journal'] = 'bioRxiv'
    pub['pub_pdf_url'] = biorxiv_url + ".full.pdf"
    pub['pub_biorxiv'] = biorxiv_id
    pub['pub_biorxiv_url'] = biorxiv_url
    return pub


def id_type(pub_id):
    pub_id = pub_id.strip().upper()
    logger.info(re.match("bio[a]?rxiv[: ]?[0-9\.]{6,9}", pub_id, re.IGNORECASE))
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
    elif re.match("bio[a]?rxiv[: ]?[0-9\.]{6,9}", pub_id, re.IGNORECASE):
        return 'biorxiv'


def fetch_pub(pub_id):
    """
        Fetch pub and process accordingly
    """
    pub_id = clean_pub_id(pub_id)
    pub_type = id_type(pub_id)

    if pub_type == 'arxiv':
        pub = fetch_arxiv(pub_id)
    elif pub_type in ['pmc', 'pmid']:
        pub = fetch_pubmed(pub_id, pub_type)
    elif pub_type == 'doi':
        pub = fetch_doi(pub_id)
    elif pub_type == 'biorxiv':
        pub = fetch_biorxiv(pub_id)
    else:
        return None


    if pub.get('pub_pdf_url'):
        thumbnail = process_pdf_task(pub)
        #if thumbnail:
        #    pub['thumbnail'] = thumbnail

    # Strip periods
    pub['pub_title'] = pub['pub_title'].strip(".")

    # Format authors
    logger.info(pub['pub_authors'])
    logger.info(len(pub['pub_authors']))
    if len(pub['pub_authors']) > 10:
        pub['pub_authors'] = pub['pub_authors'][0] + " <em>et al.</em>"
    else:
        pub['pub_authors'] = ', '.join(pub['pub_authors'])

    return pub


"""
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
"""

def parse_pub(pub_id):
    pass




