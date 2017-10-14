from setuptools import setup

setup(
    name = 'pytest-jasmine',
    py_modules = ['pytest_jasmine'],
    version = '0.0.2',
    description = (
        'Run jasmine tests from your pytest test suite'
    ),
    author = 'Daniel Wozniak',
    description_file = 'README.md',
    author_email = 'dan@woz.io',
    url = 'https://github.com/dwoz/pytest-jasmine',
    download_url = 'https://github.com/dwoz/pytest-jasmine/archive/0.0.2.tar.gz',
    bugtrack_url = 'https://github.com/dwoz/pytest-jasmine/issues',
    keywords = [
        'testing', 'pytest', 'plugin', 'fixture',
    ],
    entry_points = {
        'pytest11': [
            'dataplugin = dataplugin',
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'Framework :: Pytest',
    ],
)
