from gcloud import storage

def google_storage():
    """
        Fetch google storage credentials
    """
    return storage.Client.from_service_account_json("pdf_thumbnail_creator_credentials.json", project='upvote')

