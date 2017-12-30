import os
from sqlalchemy import or_
from huey import RedisHuey, crontab
from base.threads.models import Thread
from base.utils.file_utils import (download_pdf,
                                   pdf_to_thumb,
                                   sha1_file)
from base.utils.bioarxiv import fetch_bioarxiv
from base.utils.gs import google_storage
from base.utils.pub_ids import id_type, get_pub_thread
from base import db, app
from logzero import logger
huey = RedisHuey('upvote',
                 connection_pool=app.config['REDIS_CONNECTION_POOL'])


@huey.task()
def process_pdf_task(pub):
    """
        This task processes a PDF and generates a thumbnail preview of it.
    """
    logger.info(pub)
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

        # Process pub IDs with prefixes
        if pub.get('pub_pmid'):
            pub_id = pub.get('pub_pmid')
        elif pub.get('pub_pmc'):
            pub_id = "PMC" + str(pub.get('pub_pmc'))
        elif pub.get('pub_arxiv'):
            pub_id = "ARXIV:" + pub.get('pub_arxiv')
        elif pub.get('pub_biorxiv'):
            pub_id = "BIORXIV:" + pub.get('pub_biorxiv')
        elif pub.get('pub_doi'):
            pub_id = pub.get('pub_doi')

        # Update database
        thread = get_pub_thread(pub_id)
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

