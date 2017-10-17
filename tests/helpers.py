try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen
from zipfile import ZipFile

URL = 'https://github.com/jasmine/jasmine/releases/download/v2.8.0/jasmine-standalone-2.8.0.zip'
SHA1 = '6a6cddd66330a550a82119e55585d37965b14a4c'

def fetch_jasmine_standalone(url=URL, sha1=SHA1):
    filename = url.rsplit('/', 1)[-1]
    with urlopen(url) as url_fp:
        with open(filename, 'wb') as fp:
            while True:
                chunk = url_fp.read(1024 * 1024)
                if not chunk:
                    break
                fp.write(chunk)
    zip = ZipFile(filename)
    zip.extractall(path='jasmine')
