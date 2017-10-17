from helpers import fetch_jasmine_standalone
import os


def test_jasmine_suite(testdir):
    print(dir(testdir))
    to_path = str(testdir.tmpdir)
    fetch_jasmine_standalone(to_path=to_path)
    for dirname, dirs, files in os.walk(to_path):
        print(dirname, dirs, files)
    assert False
