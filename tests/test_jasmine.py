import pytest
import os
import pytest_jasmine
from helpers import (
    fetch_jasmine_standalone, flask_test_app, jasmine_test_html, jasmine_test_js
)


def test_jasmine_suite(testdir):
    to_path = str(testdir.tmpdir)
    fetch_jasmine_standalone(to_path=to_path)
    testdir.makepyfile(flask_test_app)
    with open(os.path.join(to_path, 'spec.html'), 'w') as fp:
        fp.write(jasmine_test_html)
    with open(os.path.join(to_path, 'static/spec.js'), 'w') as fp:
        fp.write(jasmine_test_js)
    # for dirname, dirs, files in os.walk(to_path):
    #     print(dirname, dirs, files)
    result = testdir.runpytest('--with-jasmine')
    result.assert_outcomes(passed=1, failed=1)
