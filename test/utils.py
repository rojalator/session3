"""
utilities for running twill-based unit tests.
"""
from wsgi_server import QWIP
from twill.wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept
from quixote import publish

def setup_wsgi_intercept(create_publisher_fn, host='localhost', port=8080):
    """
    Create a new function that will return a WSGI handler around the publisher
    created by 'create_publisher_fn', and then installs that as an in-memory
    handler for twill Web calls.

    Optional host and port arguments specify what host/port connection
    should be intercepted.  Defaults to 'localhost', 8080.
    """

    publish._publisher = None
    
    _cached_app = {}                    # for persistence reasons, use object
    def create_app(_cached_app=_cached_app):
        if not _cached_app:
            publisher = create_publisher_fn()
            wsgi_app = QWIP(publisher)
            _cached_app['app'] = wsgi_app

        return _cached_app['app']

    add_wsgi_intercept(host, port, create_app)

def teardown_wsgi_intercept(host='localhost', port=8080):
    """
    Uninstall the WSGI intercept handler.
    """
    remove_wsgi_intercept(host, port)
