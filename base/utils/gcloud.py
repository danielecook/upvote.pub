from gcloud import datastore, storage
from logzero import logger


def google_datastore():
    """
        Fetch google storage credentials
    """
    return datastore.Client(project='upvote-189514')


def store_item(kind, name, **kwargs):
    ds = google_datastore()
    m = datastore.Entity(key=ds.key(kind, name))
    for key, value in kwargs.items():
        if type(value) == str:
            m[key] = unicode(value)
        else:
            m[key] = value
    ds.put(m)


def query_item(kind, filters=None, projection=()):
    # filters:
    # [("var_name", "=", 1)]
    ds = google_datastore()
    query = ds.query(kind=kind, projection=projection)
    if filters:
        for var, op, val in filters:
            query.add_filter(var, op, val)
    return query.fetch()


def get_item(kind, name):
    """
        returns item by kind and name
    """
    logger.info("Retrieving {} {}".format(kind, name))
    ds = google_datastore()
    result = ds.get(ds.key(kind, name))
    return {k:v for k,v in result.items() if v}



def google_storage():
    """
        Fetch google storage credentials
    """
    return storage.Client(project='upvote-189514')