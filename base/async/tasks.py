import os
from sqlalchemy import or_
from huey import RedisHuey, crontab
from base.threads.models import Thread
from base.utils.file_utils import (download_pdf,
                                   pdf_to_thumb,
                                   sha1_file)
from base.utils.bioarxiv import fetch_bioarxiv
from base.utils.gs import google_storage
from base import db, app
huey = RedisHuey('upvote',
                 connection_pool=app.config['REDIS_CONNECTION_POOL'])


@huey.task(include_task=True)
def process_pdf_task(pub, task):
    """
        This task processes a PDF and generates a thumbnail preview of it.
    """
    url = pub.get('pub_pdf_url')
    if url:
        fname = download_pdf(url)
        sha1_fname = sha1_file(fname)
        thumbnail_fname = pdf_to_thumb(fname, sha1_fname)

        gs_client = google_storage()
        bucket = gs_client.get_bucket('pdf_thumbnails')
        thumbnail_obj = bucket.blob(thumbnail_fname)
        thumbnail_obj.upload_from_filename(thumbnail_fname)
        # Delete after upload
        os.remove(thumbnail_fname)

        pub_id = pub.get('pub_doi') or \
                 pub.get('pub_pmid') or \
                 pub.get('pub_pmcid') or \
                 pub.get('pub_arxiv')
        # Update database
        thread = Thread.query.filter(or_(Thread.pub_doi == pub_id,
                                         Thread.pub_pmid == pub_id,
                                         Thread.pub_pmcid == pub_id,
                                         Thread.pub_arxiv == pub_id)).first()
        thread.thumbnail = thumbnail_fname
        db.session.commit()


@huey.periodic_task(crontab(minute='*/1'), always_eager=True)
def store_bioarxiv():
    """
        Stores URLS for bioarxiv articles
    """
    r = huey.storage.conn
    for k, v in fetch_bioarxiv().items():
        r.set('biorxiv:' + k, v)

