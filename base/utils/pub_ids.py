# -*- coding: utf-8 -*-

# Parse Pubs
import re
from logzero import logger
from base.threads.models import Publication


def id_type(pub_id):
    logger.info(pub_id)
    pub_id = re.sub("http[s]?://doi.org/", "", pub_id, re.IGNORECASE)
    # arXiv
    if re.match("(arXiv)?[: \-]?([0-9]{4}\.[0-9]{4,5}(v[0-9]+)?)", pub_id, re.IGNORECASE):
        m = re.match("(arXiv)?[: \-]?([0-9]{4}\.[0-9]{4,5}(v[0-9]+)?)", pub_id, re.IGNORECASE)
        return 'arxiv', m.group(2)
    elif re.match("[a-z]+(\.[a-z]+)/[0-9]+", pub_id, re.IGNORECASE):
        m = re.match("[a-z]+(\.[a-z]+)/[0-9]+", pub_id, re.IGNORECASE)
        return 'arxiv', m.group(0)
    elif re.match(".*arxiv.org/abs/([0-9]{4}\.[0-9]{4,5}(v[0-9]+)?).*", pub_id, re.IGNORECASE):
        m = re.match(".*arxiv.org/abs/([0-9]{4}\.[0-9]{4,5}(v[0-9]+)?).*", pub_id, re.IGNORECASE)
        return 'arxiv', m.group(1)
    elif re.match(".*arxiv.org/abs/([^\/]+/[0-9]+).*", pub_id, re.IGNORECASE):
        # Arxiv - old ids
        m = re.match(".*arxiv.org/abs/([^\/]+/[0-9]+).*", pub_id, re.IGNORECASE)
        return 'arxiv', m.group(1).lower()


    # PMC
    elif re.match("PMC[0-9]+", pub_id.upper()):
        return 'pmc', int(pub_id.upper().replace("PMC", ""))
    elif re.match(".*ncbi.nlm.nih.gov/pmc/articles/(PMC[0-9]+)/", pub_id, re.IGNORECASE):
        m = re.match(".*ncbi.nlm.nih.gov/pmc/articles/PMC([0-9]+)/", pub_id, re.IGNORECASE)
        return 'pmc', int(m.group(1))

    # DOI
    elif re.match('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)', pub_id):
        m = re.match('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)', pub_id)
        return 'doi', m.group(1)
    
    # Pubmed
    elif re.match('[0-9]+', pub_id):
        return 'pmid', int(pub_id)
    elif re.match('.*ncbi.nlm.nih.gov/pubmed/([0-9^\/]+).*', pub_id, re.IGNORECASE):
        m = re.match('.*ncbi.nlm.nih.gov/pubmed/([0-9^\/]+).*', pub_id, re.IGNORECASE)
        return 'pmid', m.group(1)
    
    # BiorXiv
    elif re.match("bio[a]?rxiv[: \-]?([0-9\.]{6,9})", pub_id, re.IGNORECASE):
        m = re.match("bio[a]?rxiv[: \-]?([0-9\.]{6,9})", pub_id, re.IGNORECASE)
        return 'biorxiv', m.group(1)
    elif re.match(".*biorxiv.org/content/early/[0-9]{4}/[0-9]{2}/[0-9]{2}/([0-9\.]{6,9})", pub_id, re.IGNORECASE):
        m = re.match(".*biorxiv.org/content/early/[0-9]{4}/[0-9]{2}/[0-9]{2}/([0-9\.]{6,9})", pub_id, re.IGNORECASE)
        return 'biorxiv', m.group(1)
    else:
        return None, None


def get_publication(pub_id):
    """Fetch publication from the database

    Args:
        pub_id - Any publication ID

    """
    pub_id = pub_id.strip()
    pub_type, pub_id = id_type(pub_id)
    if pub_type:
        return Publication.query.filter(getattr(Publication, 'pub_' + pub_type) == pub_id).first()


