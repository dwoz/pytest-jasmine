import os
from zipfile import ZipFile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


URL = 'https://github.com/jasmine/jasmine/releases/download/v2.8.0/jasmine-standalone-2.8.0.zip'
SHA1 = '6a6cddd66330a550a82119e55585d37965b14a4c'


def fetch_jasmine_standalone(url=URL, sha1=SHA1, to_path=None, folder='jasmine'):
    filename = url.rsplit('/', 1)[-1]
    if to_path:
        filename = os.path.join(to_path, filename)
        folder = os.path.join(to_path, folder)
    with urlopen(url) as url_fp:
        with open(filename, 'wb') as fp:
            while True:
                chunk = url_fp.read(1024 * 1024)
                if not chunk:
                    break
                fp.write(chunk)
    zip = ZipFile(filename)
    zip.extractall(path=folder)


jasmine_test_js = '''
describe("Jasmine Test Suite", function() {

    it("Passing test", function() {
        expect(true).toEqual(true)
    });

    it("Failing test", function() {
        expect(true).toEqual(false)
    });

});
'''


jasmine_test_html = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Jasmine Spec Runner v2.8.0</title>
    <link rel="shortcut icon"
      type="image/png"
      href="jasmine/lib/jasmine-2.8.0/jasmine_favicon.png">
    <link rel="stylesheet" href="jasmine/lib/jasmine-2.8.0/jasmine.css">
    <script type="text/javascript"
      src="https://code.jquery.com/jquery-3.2.1.min.js"
      integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
      crossorigin="anonymous"></script>
    <script type="text/javascript"
      src="jasmine/lib/jasmine-2.8.0/jasmine.js"></script>
    <script type="text/javascript"
      src="jasmine/lib/jasmine-2.8.0/jasmine-html.js"></script>
    <script type="text/javascript"
      src="jasmine/lib/jasmine-2.8.0/boot.js"></script>
    <script type="text/javascript"
      src="jasmine/mock-ajax.js"></script>
    <!-- jasmine spec files -->
    <script src="spec.js"></script>
  </head>
  <body>
  </body>
</html>
'''


flask_test_app = '''
import Flask, abort, send_file
app = Flask(__name__)
@app.route('/', methods=['GET'])
def index(self):
    try:
        return send_file('spec.html')
    except FileNotFoundError:
        return abort(404)
'''
