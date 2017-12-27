import requests
import hashlib
from tempfile import NamedTemporaryFile
from subprocess import Popen


BUFFER_SIZE = 65336

def sha1_file(input):
    sha1 = hashlib.sha1()
    with open(input, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def download_pdf(url):
    """
        Downloads a pdf to a temporary location
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        download_url = requests.head(url,
                                     allow_redirects=True,
                                     headers=headers)
        response = requests.get(download_url.url, stream=True, headers=headers)
    except:
        return None
    out = NamedTemporaryFile(suffix=".pdf", delete=False)
    with open(out.name, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)
    return out.name


def pdf_to_thumb(fname, sha1_fname):
    """
        Generates a thumbnail
        for the URL provided for a PDF
    """
    thumbnail_fname = sha1_fname + ".thumb.png"
    comm = ['convert', '-strip', '-quality',
            '90', '-thumbnail', '200',
            fname + "[0]", thumbnail_fname]
    out, err = Popen(comm).communicate()
    return thumbnail_fname
