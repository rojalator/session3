"""
nose-based unit tests.

CTB: where is stdout getting captured in here!?

CTB TODO:
 * cleanup files after running tests
"""

from pkg_resources import require
#require('quixote >= 2.3')
require('twill >= 0.8.2a3')

import sys
import utils, test_session2
import twill
from cStringIO import StringIO

def test_basic():
    """
    Test basic session handling with the volatile session handler.
    """
    utils.setup_wsgi_intercept(test_session2.use_volatile)

    try:
        old_err, sys.stderr = sys.stderr, StringIO()

        twill.execute_file('test/twill-tests/increment')
        twill.execute_file('test/twill-tests/increment+fail')
        twill.execute_file('test/twill-tests/logout')
        twill.execute_file('test/twill-tests/logout+fail')
        twill.execute_file('test/twill-tests/logout+nokeep')
        twill.execute_file('test/twill-tests/session_id')
    finally:
        sys.stderr = old_err
    
    utils.teardown_wsgi_intercept()

def test_directory():
    """
    Test basic session handling with the directory session handler.
    """
    utils.setup_wsgi_intercept(test_session2.use_directory)

    try:
        old_err, sys.stderr = sys.stderr, StringIO()
        
        twill.execute_file('test/twill-tests/increment')
        twill.execute_file('test/twill-tests/increment+fail')
        twill.execute_file('test/twill-tests/logout')
        twill.execute_file('test/twill-tests/logout+fail')
        twill.execute_file('test/twill-tests/logout+nokeep')
        twill.execute_file('test/twill-tests/session_id')
    finally:
        sys.stderr = old_err
    
    utils.teardown_wsgi_intercept()

def test_shelve():
    """
    Test basic session handling with the shelve session handler.
    """
    utils.setup_wsgi_intercept(test_session2.use_shelve)
    
    try:
        old_err, sys.stderr = sys.stderr, StringIO()

        twill.execute_file('test/twill-tests/increment')
        twill.execute_file('test/twill-tests/increment+fail')
        twill.execute_file('test/twill-tests/logout')
        twill.execute_file('test/twill-tests/logout+fail')
        twill.execute_file('test/twill-tests/logout+nokeep')
        twill.execute_file('test/twill-tests/session_id')
    finally:
        sys.stderr = old_err
    
    utils.teardown_wsgi_intercept()

def test_durus():
    """
    Test basic session handling with the durus session handler.
    """
    try:
        import durus
    except ImportError:
        pass
    else:
        utils.setup_wsgi_intercept(test_session2.use_durus)

        try:
            old_err, sys.stderr = sys.stderr, StringIO()

            twill.execute_file('test/twill-tests/increment')
            twill.execute_file('test/twill-tests/increment+fail')
            twill.execute_file('test/twill-tests/logout')
            twill.execute_file('test/twill-tests/logout+fail')
            twill.execute_file('test/twill-tests/logout+nokeep')
            twill.execute_file('test/twill-tests/session_id')
        finally:
            sys.stderr = old_err

        utils.teardown_wsgi_intercept()
        
