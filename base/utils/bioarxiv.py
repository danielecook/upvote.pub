#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Because bioRxiv offers no API and has a stupid URL scheme, we have to 
    periodically parse the site map and make it available (within redis) for fetching bioarxiv articles.
"""

from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


def get_sitemap(url):
    get_url = requests.get(url)

    if get_url.status_code == 200:
        return get_url.text
    else:
        print('Unable to fetch sitemap: %s.' % url)


def process_sitemap(s):
    soup = BeautifulSoup(s, 'lxml')
    result = []

    for loc in soup.findAll('loc'):
        result.append(loc.text)

    return result


def is_sub_sitemap(s):
    s = urlparse(s)
    if s.path.endswith('.xml') and 'sitemap' in s.path:
        return True
    else:
        return False


def parse_sitemap(s):
    sitemap = process_sitemap(s)
    result = []

    while sitemap:
        candidate = sitemap.pop()
        if is_sub_sitemap(candidate):
            sub_sitemap = get_sitemap(candidate)
            for i in process_sitemap(sub_sitemap):
                sitemap.append(i)
        else:
            result.append(candidate)

    return result


def fetch_bioarxiv():
    bioarxiv_out = {}
    sitemap = get_sitemap('https://www.biorxiv.org/sitemap.xml')
    sitemap = parse_sitemap(sitemap)
    for url in sitemap:
        url_split = url.split("/")
        if len(url_split) == 9:
            bioarxiv_id = url_split[8]
            bioarxiv_out[bioarxiv_id] = url
    return bioarxiv_out
