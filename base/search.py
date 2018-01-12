# -*- coding: utf-8 -*-
"""
Simple module for searching the sql-alchemy database based
on user queries.
"""
from base.threads.models import Thread, Publication, Comment
from base import db
from sqlalchemy_fulltext import FullTextSearch
import sqlalchemy_fulltext.modes as FullTextMode


def search(query, orderby='creation', filter_user=None, search_title=True,
            search_text=True, subreddit=None):
    """
    search for threads (and maybe comments in the future)
    """
    if not query:
        return []
    query = query.strip()


    base_qs = Thread.query.join(Publication).filter(FullTextSearch(query, Publication, FullTextMode.NATURAL))


    if orderby == 'creation':
        base_qs = base_qs.order_by(db.desc(Thread.created_on))
    elif orderby == 'title':
        base_qs = base_qs.order_by(Thread.title)
    elif orderby == 'numb_comments':
        pass

    return base_qs
