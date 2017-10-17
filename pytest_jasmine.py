'''
Collect Jasmine tests from a url using selenium webdriver and display the
results durring a pytest run.
'''
import contextlib
import time
import signal

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from py._path.local import FSBase
import multiprocessing

import pytest


NOOP = '__pytest_jasmine_NOOP'


def driver_class(name="chrome"):
    '''
    Lookup a WebDriver class from the given driver name
    '''
    mod = getattr(webdriver, name, None)
    if not mod:
        raise Exception
    return mod.webdriver.WebDriver


def server_target(app, address, port):
    app.configure({})
    app.run(address, port, use_reloader=False, threaded=True)


@contextlib.contextmanager
def server_ctxt(app):
    address = '127.0.0.1'
    port = 9280
    proc = multiprocessing.Process(target=server_target, args=(app, address, port))
    try:
        proc.start()
        yield
    finally:
        proc.terminate()


@contextlib.contextmanager
def driver_ctx(name="chrome", **kwargs):
    '''
    Selenium WebDriver context manager.
    '''
    cls = driver_class(name)
    driver = cls(**kwargs)
    driver.set_window_size(1400, 1000)
    yield driver
    driver.close()
    # TODO: Really seems like this shouldn't bee needed. At the very leasg
    # SIGEXIT seems more appropriate but that doesnt' seem to work for some
    # versions of phantomjs
    driver.service.process.send_signal(signal.SIGKILL)
    driver.quit()


def wait_for_results(driver, ready_wait=False):
    '''
    Wait for the Jasmine test suite to finish
    '''
    if ready_wait:
        WebDriverWait(driver, 100).until(
            lambda driver:
            driver.execute_script("return document.readyState === 'complete';")
        )
    WebDriverWait(driver, 100).until(
        lambda driver:
        driver.execute_script("return jsApiReporter.finished;")
    )


def results(driver):
    '''
    Collect Jasmine test results from the webdriver instance.
    '''
    batch_size = 10
    spec_results = []
    index = 0
    while True:
        results = driver.execute_script(
            "return jsApiReporter.specResults({0}, {1})".format(
                index,
                batch_size
            )
        )
        spec_results.extend(results)
        index += len(results)

        if not len(results) == batch_size:
            break
    return spec_results


class JasmineException(Exception):
    '''
    Exception class to be raised if the Jasmine plugin experiences an error
    '''


class Jasmine(object):
    '''
    Configure Jasmine test suite url
    '''

    def __init__(self, app=None, url=None, driver_name='phantomjs'):
        self.app = app
        self.url = url
        self.driver_name = driver_name


class JasmineItem(pytest.Item):
    '''
    Represents a single Jasmine test
    '''

    def __init__(self, name, parent, spec):
        super(JasmineItem, self).__init__(name, parent)
        self.spec = spec
        #self._location = (parent.url, None, name)

    def runtest(self):
        assert self.spec['status'] == 'passed'

    def repr_failure(self, excinfo):
        lines = []
        for exp in self.spec['failedExpectations']:
            lines.append(exp['message'])
            #lines.append(exp['stack'])
        return '\n'.join(lines)

    @property
    def originalname(self):
        return ''

    def _getfailureheadline(self, rep):
        if hasattr(rep, 'location'):
            fspath, lineno, domain = rep.location
            return domain
        else:
            return "test session"  # XXX?

    @property
    def location(self):
        #print("LOCTION CALL")
        return self._location


class JasmineCollector(pytest.Collector):
    '''
    Collect the jasmine tests.
    '''

    def __init__(self, app, url, driver_name, *args, **kwargs):
        self.app = app
        self.url = url
        self.driver_name = driver_name
        self._nodeid = url
        super(JasmineCollector, self).__init__(url, *args, **kwargs)

    def collect(self):
        items = []
        # print("Begin Jasmine collection: {}".format(self.url))
        # with driver_ctx('phantomjs', service_args=["--debug=yes","--remote-debugger-port=9000"]) as driver:
        #with driver_ctx('phantomjs', service_args=['--debug=yes']) as driver:
        with server_ctxt(self.app):
            with driver_ctx(self.driver_name, service_args=['--debug=yes']) as driver:
                url = 'http://127.0.0.1:9280/' + self.url
                print(url)
                driver.get(url)
                wait_for_results(driver)
                for i in results(driver):
                    items.append(JasmineItem(i['description'], self, i))
        return items

    def reportinfo(self):
        return ('.', False, "")


class JasminePath(FSBase):
    '''
    Path helper to oeverride the pytest path setting since the Jasmine tests
    are not located at a filesystem path.
    '''

    def __init__(self, path, expanduser=False):
        self.strpath = path

    def replace(self, *args):
        return self.strpath

    def __repr__(self):
        return self.strpath

    def alt_join(self, *args):
        path = self.strpath
        for i in args:
            path = "{}/{}".format(path.rstrip('/'), i.lstrip('/'))
        o = object.__new__(self.__class__)
        o.strpath = path
        return o


def pytest_addoption(parser):
    '''
    Add pytest commandline options for the jasmine plugin
    '''
    parser.addoption(
        "--with-jasmine",
        #action='store_true',
        default=NOOP,
        nargs='?',
        help='Run cassandra tests',
    )


def pytest_pycollect_makeitem(collector, name, obj):
    '''
    When the jasmine plugin in enabled add the Jasmine items to the Pytest
    collector.
    '''
    url = pytest.config.option.with_jasmine
    if url != NOOP and isinstance(obj, Jasmine):
        if url is None:
            url = obj.url
        return JasmineCollector(obj.app, url, obj.driver_name, parent=collector.parent)


def pytest_collection_modifyitems(session, config, items):
    '''
    Provide sane output for the path portion of the test results.
    '''
    for item in items:
        if isinstance(item, JasmineItem):
            if config.option.verbose == 1:
                name = JasminePath(item.parent.url)
            else:
                config.rootdir.join = JasminePath.alt_join.__get__(
                    config.rootdir, config.rootdir.__class__
                )
                name = JasminePath(item.name)
            item._location = (name, None, item.name)
