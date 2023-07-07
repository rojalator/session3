#!/usr/bin/env python
"""
Test the session3 package with a variety of session stores.
Run with (for use_directory) in the "test" folder:

    python3 -bb test_session3.py directory

and then visit:

    http://localhost:8080

Publisher factory functions:

   * use_shelve() -- use a 'shelve' database to store sessions.

   * use_directory() -- store sessions in files under a directory.

   * use_psycopg() -- use 'psycopg' to connect to a database called 'sql_store'
                      and store pickled sessions in that database.  Assumes a
                      table 'sessions' exists with the correct structure.

   * use_postgres() -- same as 'psycopg'                      

   * use_mysql()   -- use 'MySQLdb' to connect to a database called 'test'
                      and store pickled sessions in that database.  Assumes a
                      table 'sessions' exists with the correct structure.

   * use_durus() -- use the Durus object database to store sessions.
"""

import sys
from optparse import OptionParser
from quixote.publish import Publisher
from quixote.directory import Directory
from quixote import get_session, get_session_manager, get_path, redirect
from quixote.server import simple_server
from quixote.server.util import get_server_parser
from quixote.logger import DefaultLogger
from io import StringIO

sys.path.insert(0, '..')
from session3.Session import Session
from session3.SessionManager import SessionManager

##########################################

def use_volatile():
    from session3.store.VolatileSessionStore import VolatileSessionStore
    store = VolatileSessionStore()
    return create_publisher(store)

def use_shelve():
    from session3.store.ShelveSessionStore import ShelveSessionStore
    shelve_store = ShelveSessionStore('sessions.shelf')
    return create_publisher(shelve_store)

def use_directory():
    from session3.store.DirectorySessionStore import DirectorySessionStore
    dir_store = DirectorySessionStore('./sessiondir/', create=True)
    return create_publisher(dir_store)

def use_psycopg():
    from session3.store.PostgresSessionStore import PostgresSessionStore
    import psycopg
    conn = psycopg.connect('dbname=sql_store')
    sql_store = PostgresSessionStore(conn)
    return create_publisher(sql_store)

use_postgres = use_psycopg

def use_mysql():
    from session3.store.MySQLSessionStore import MySQLSessionStore
    import MySQLdb
    conn = MySQLdb.connect(db='test')
    sql_store = MySQLSessionStore(conn)
    return create_publisher(sql_store)

def use_durus():
    from session3.store.DurusSessionStore import DurusSessionStore
    from durus.file_storage import FileStorage
    from durus.connection import Connection
    durus_conn = Connection(FileStorage('sessions.durus'))
    durus_store = DurusSessionStore(durus_conn)

    return create_publisher(durus_store)

logger = None
def create_publisher(session_store):
    global logger
    logger = DefaultLogger()
    logger.access_log = StringIO()
    logger.error_log = StringIO()
    
    session_manager = SessionManager(session_store, session_class=TestSession)
    
    return Publisher(LoginSession(),
                     session_manager=session_manager,
#                     logger=logger,
                     display_exceptions='html')

##################################################

class TestSession(Session):
    def __init__(self, id):
        Session.__init__(self, id)
        self.counter = 0
        self.keep = False

    def increment(self):
        self.counter += 1

    def has_info(self):
        return self.keep

class LoginSession(Directory):
    """
    Do some simple session manipulations.
    """
    _q_exports = ['', 'logout', 'logoutfail', 'increment', 'incrementfail',
                  'keep']

    def _q_index(self):
        # a session object exists for each connection: get it.
        session = get_session()

        # return page.
        return """\
Hello, world!
<p>
Your session ID is %s.
<p>
Counter is at %d.
<p>
<a href="./">revisit page</a>
<p>
<a href="keep">assign session</a>
<p>
<a href="increment">increment</a> | <a href="incrementfail">increment+error</a>
<p>
<a href="logout">log out</a> | <a href="logoutfail">logout+error</a>
""" % (session.id, session.counter)

    def keep(self):
        """
        Set the session to persist.
        """
        session = get_session()
        session.keep = True

        # redirect to index page.
        return redirect(get_path(1) + '/')

    def logout(self):
        """
        Expire the session, redirect back to index page.
        """
        # expire session
        session_manager = get_session_manager()
        session_manager.expire_session()

        # redirect to index page.
        return redirect(get_path(1) + '/')

    def logoutfail(self):
        """
        Expire the session, raise PublishException.

        Effect: no log out.
        """
        session_manager = get_session_manager()
        session_manager.expire_session()
        raise Exception("oops.")

    def increment(self):
        session = get_session()
        session.increment()
        return redirect(get_path(1) + '/')

    def incrementfail(self):
        session = get_session()
        session.increment()
        raise Exception("oops!")

##################################################
USAGE = """\
%prog STORAGE_TYPE
    STORAGE_TYPE must be one of: directory durus mysql postgres psycopg shelve
    See the module docstring for additional help."""

# @@MO: --dict flag or second arg could select a TestDictStorage.
# Use --help for additional help, and see the module docstring.

DESCRIPTION = """\
Runs a session testing application with Quixote's simple server."""

def main():
    parser = get_server_parser(DESCRIPTION)
    parser.set_usage(USAGE)
    parser.remove_option('--factory')
    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error("wrong number of command-line args")
    factory_name = "use_" + args[0]
    try:
        factory = globals()[factory_name]
    except KeyError:
        parser.error("unknown storage type")
    simple_server.run(factory, opts.host, opts.port)

if __name__ == "__main__":  main()
