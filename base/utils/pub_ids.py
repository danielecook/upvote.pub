# -*- coding: utf-8 -*-

# Parse Pubs
import re
from logzero import logger
from base.threads.models import Thread


def id_type(pub_id):
    pub_id = pub_id.strip().upper()
    if re.match("(arXiv)?[: ]?([0-9]{4}\.[0-9]{4,5}(v[0-9]+)?)", pub_id, re.IGNORECASE):
        m = re.match("(arXiv)?[: ]?([0-9]{4}\.[0-9]{4,5}(v[0-9]+)?)", pub_id, re.IGNORECASE)
        return 'arxiv', m.group(2)
    elif re.match("[a-z]+(\.[a-z]+)/[0-9]+", pub_id, re.IGNORECASE):
        m = re.match("[a-z]+(\.[a-z]+)/[0-9]+", pub_id, re.IGNORECASE)
        return 'arxiv', m.group(0)
    elif re.match("PMC[0-9]+", pub_id.upper()):
        return 'pmc', int(pub_id.upper().replace("PMC", ""))
    elif re.match('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)', pub_id):
        m = re.match('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)', pub_id)
        return 'doi', m.group(1)
    elif re.match('[0-9]+', pub_id):
        return 'pmid', int(pub_id)
    elif re.match("bio[a]?rxiv[: ]?([0-9\.]{6,9})", pub_id, re.IGNORECASE):
        m = re.match("bio[a]?rxiv[: ]?([0-9\.]{6,9})", pub_id, re.IGNORECASE)
        return 'biorxiv', m.group(1)


def get_pub_thread(pub_id):
    """
    Get pub thread from the database
    """
    logger.debug('Fetching ' + pub_id)
    pub_id = pub_id.strip().upper()
    pub_type, pub_id = id_type(pub_id)
    thread = Thread.query.filter(getattr(Thread, 'pub_' + pub_type) == pub_id).first()
    return thread


