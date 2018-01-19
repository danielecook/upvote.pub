import markdown2
import bleach
import re
from flask import Markup


def format_comment(text):
    """
        Formats comment
        via ajax or page load
    """
    # DOI
    # PMC
    # Arxiv
    # BioArxiv
    link_patterns=[(re.compile(r'ggg'), r'\1'),
                   (re.compile(r'pmid:([0-9]+)', re.I), r'https://www.ncbi.nlm.nih.gov/pubmed/\1')]
    clean_text = bleach.clean(text)
    markdown_text = markdown2.markdown(clean_text,
                                       extras = ['fenced-code-blocks',
                                                 'nofollow',
                                                 'target-blank-links',
                                                 'tables',
                                                 'footnotes',
                                                 'link-patterns'],
                                       link_patterns=link_patterns)
    return Markup(markdown_text)


def linkify(text):
    """
        Finds links in text and replaces them with URLs
    """
    urlfinder = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    return urlfinder.sub(r'<a href="\1" target="_blank">\1</a>', text)


def find_github_links(text):
    github_finder = re.compile(r'github\.com/([^\/]+)\/([^\/\.\)\( ]+)')
    github_m = github_finder.findall(text)
    if github_m:
        for match in github_m:
            yield match