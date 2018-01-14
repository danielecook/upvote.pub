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
    print(clean_text)
    markdown_text = markdown2.markdown(clean_text,
                                       extras = ['fenced-code-blocks',
                                                 'nofollow',
                                                 'target-blank-links',
                                                 'tables',
                                                 'footnotes',
                                                 'link-patterns'],
                                       link_patterns=link_patterns)
    return Markup(markdown_text)