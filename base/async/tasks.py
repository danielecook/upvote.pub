import os
from sqlalchemy import or_
from huey import RedisHuey, crontab
from base.threads.models import Thread
from base.utils.file_utils import (download_pdf,
                                   pdf_to_thumb,
                                   sha1_file)
from base.utils.bioarxiv import fetch_bioarxiv
from base.utils.gcloud import google_storage
from base.utils.pub_ids import id_type, get_pub_thread
from base import db, app
from logzero import logger
from metapub import FindIt
from metapub.base import MetaPubError

huey = RedisHuey('upvote',
                 connection_pool=app.config['REDIS_CONNECTION_POOL'])


@huey.task(retries = 3, retry_delay =20)
def process_pdf_task(pub):
    """
        This task processes a PDF and generates a thumbnail preview of it.
    """
    logger.info("STARTING TASK {}".format(pub))

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

    thread = get_pub_thread(pub_id)

    pub_type, pub_id = id_type(pub_id)

    url = pub.get('pub_pdf_url')

    # Attempt to find the publication
    if url == 'searching':
        try:
            if pub_type == 'pmid':
                found_pdf = FindIt(pmid=pub['pub_pmid'])
            elif pub_type == 'doi':
                found_pdf = FindIt(doi=pub['pub_doi'])
            url = found_pdf.url
            thread.pub_pdf_url = url
            # Update status to indicate PDF found!
            db.session.commit()
        except MetaPubError:
            url = None

    if url:
        fname = download_pdf(url)
        sha1_fname = sha1_file(fname)
        logger.info(sha1_fname)
        thumbnail_fname = pdf_to_thumb(fname, sha1_fname)

        gs_client = google_storage()
        bucket = gs_client.get_bucket('pdf_thumbnails')
        thumbnail_obj = bucket.blob(thumbnail_fname)
        thumbnail_obj.upload_from_filename(thumbnail_fname)
        # Delete after upload
        os.remove(thumbnail_fname)

        # Update database
        thread.thumbnail = thumbnail_fname
    else:
        thread.pub_pdf_url = None
    db.session.commit()



@huey.periodic_task(crontab(hour='*/10'), always_eager=True)
def store_bioarxiv():
    """
        Stores URLS for bioarxiv articles
    """
    r = huey.storage.conn
    for k, v in fetch_bioarxiv().items():
        r.set('biorxiv:' + k, v)

