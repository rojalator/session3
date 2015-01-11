=======================================================
session2: Persistent Session Management for Quixote 2.x
=======================================================

:Authors: C Titus Brown, Mike Orr
:Email: titus@caltech.edu, mso@oz.net
:License: MIT  (http://www.opensource.org/licenses/mit-license.php)
:Version: 0.6.1  released on 2006-2-05
:Status: beta.  All stores pass basic tests and several are used in production code.

.. contents::

Introduction
============

Quixote_ is a Python Web application framework.  It comes with an
in-memory session manager, which works but is incompatible with
multi-process servers (SCGI, CGI, etc).  It also forgets the sessions
when the Publisher quits.  `session2` solves these problems by
providing a new session manager class and a simple back end storage
API.

`session2` also provides several (fully functional) persistent storage back
ends:

DirectorySessionStore_
  Store each pickled session in a file in the designated directory.  The
  filename is the session ID.  Uses ``fcntl`` file locking.  ::

      DirectorySessionStore(directory)
  
DurusSessionStore_
  Store sessions in a Durus_ database.  ::

      DurusSessionStore(durus_connection)

MySQLSessionStore_
  Store sessions in a MySQL_ database.  ::
      
      MySQLSessionStore(mysql_connection, table='sessions')

PostgresSessionStore_
  Store sessions in a PostgreSQL_ database.  ::

      PostgresSessionStore(psycopg_connection)
  
ShelveSessionStore_
  Store sessions in a DBM database using ``shelve``.  ::

      ShelveSessionStore(filename)
  
This package includes a refactored SessionManager that makes it easy to develop
additional back ends, and a simplified Session class (no .is_dirty method).
It supports the usual ``.user``, ``.set_user()`` and ``.has_info()``
attributes, and you can also set your own attributes which will be saved.
There's also a DictSession subclass for those who prefer setting keys rather
than attributes [1]_.

It's quite likely that the session stores can be adapted for use with other
Web frameworks; let us know if you do this so we can link to you and/or
include helpful code in our package.

.. _DirectorySessionStore: epydoc-html/session2.store.DirectorySessionStore.DirectorySessionStore-class.html
.. _DurusSessionStore: epydoc-html/session2.store.DurusSessionStore.DurusSessionStore-class.html
.. _MySQLSessionStore: epydoc-html/session2.store.MySQLSessionStore.MySQLSessionStore-class.html
.. _PostgresSessionStore: epydoc-html/session2.store.PostgresSessionStore.PostgresSessionStore-class.html
.. _ShelveSessionStore: epydoc-html/session2.store.ShelveSessionStore.ShelveSessionStore-class.html

.. [1] DictSession is especially useful for applications that may want
   to use `Paste`_'s session middleware in the future, because it is dict-based.
   However, the migration for ``.user`` and ``.set_user()`` is not yet clear.

Getting session2
================

Download the latest version here:
http://quixote.idyll.org/session2/session2-0.6.tar.gz

Source code browser: http://cafepy.com/quixote_extras/titus/session2/

You can also `grab it directly via subversion`_.

.. _grab it directly via subversion: http://cafepy.com/quixote_extras/README

Installation
------------

Unpack the tar.gz file, and install the normal Python way ("python
setup.py install").  You can also just put the 'session2' subdirectory
in your Python path.

Upgrading
---------

The MySQL database format changed in 0.4.  Users should convert the 'pickle'
column to type BLOB, or delete the table and recreate it.

Using session2
==============

In your `create_publisher` function, place the following code::

    # create the session store.
    from session2.store.VolatileSessionStore import VolatileSessionStore
    store = VolatileSessionStore()

    # create the session manager.
    from session2.SessionManager import SessionManager
    session_manager = SessionManager(store)

    # create the publisher.
    from quixote.publish import Publisher
    publisher = Publisher(..., session_manager.session_manager)

Each session store has different initialization requirements; see
the `source documentation`_ for more information.    

To use an alternate session class::

    from session2.DictSession import DictSession
    session_manager = SessionManager(store, DictSession)

Using MySQL
-----------
::

    import MySQLdb
    from session2.store.MySQLSessionStore import MySQLSessionStore
    from session2.SessionManager import SessionManager
    from quixote.publish import Publisher
    conn = MySQLdb.connect(user='USER', passwd='PASSWORD', db='DB')
    store = MySQLSessionStore(conn, table='sessions')
    session_manager = SessionManager(store)
    publisher = Publisher(MyDirectory(), session_manager=session_manager)

Customizing the 'user' member
-----------------------------

The session2 code is fairly flexible.  You can assign anything pickle-able
to the 'Session.user' variable, and it will work with any of the session
stores.  This lets you use almost any Python class for user information.

However, you might want your session store to be independent from your
primary database.  If your user information is stored in this
database, but your session information is not, then you probably don't
want to store pickled user objects in your session store.

All of this is the long way to say that there's no reason for you to
store your entire user object within the session store.  You can easily
write an application-specific wrapper around the 'user' member of Session::

   class MySessionWrapper(Session):
      """Store only your user's database ID in the user variable."""
      def set_user(self, user):
         self.user = user.db_id

      def get_user(self):
         if self.user is None:   # user not set
            return None

         return database.load_user(self.user)

(Remember to pass the new session class in as the second argument to your
SessionManager_ instance!)

.. _SessionManager: epydoc-html/session2.SessionManager.SessionManager-class.html#__init__

Features
========

All session stores have the following methods, which are called by the session
manager: ``.load_session``, ``.save_session``, ``.delete_session``,
``.has_session``.

They also have these convenience methods:

``.setup()``: initializes the store.  For MySQL and PostgreSQL, this
creates the table.  This is meant to be called in your application
setup code when you deploy it on a new server.

``.delete_old_sessions(minutes)``: deletes sessions that haven't been modified
for N minutes.  This is meant for your application maintenance program; e.g.,
a daily cron job.  Only MySQLSessionStore actually deletes the sessions at
this point; it's a no-op for the others.

``.iter_sessions()``: Return an iterable of (id, session) for all sessions
in the store.  This is for admin applications that want to browse the sessions.
Only MySQLSessionStore currently implements this; the others raise
NotImplementedError.

All stores have ``.is_multiprocess_safe`` and ``.is_thread_safe`` attributes.
An application can check these flags and abort if configured inappropriately.
The flags are defined as follows:

- DirectorySessionStore is multiprocess safe because it uses ``fcntl`` file
  locking.  This limits its use to POSIX.  See the fcntl caution below.  It may
  be thread safe because it always locks-unlocks within the same method, but we
  don't know for sure so the attribute is false.

- DurusSessionStore is multiprocess safe.  It's not thread safe because Durus
  isn't.  With synchronization (see ``thread.allocate_lock``) a subclass could
  be made safe, maybe.

- The two SQL session stores (MySQLSessionStore and
  PostgresSessionStore) are multiprocess safe.  They are not thread
  safe because each connection is per-process.  A subclass could use
  thread-specific connections or a connection pool.

- ShelveSessionStore is *not* multiprocess safe because it doesn't do file
  locking.  See the "Restrictions" section for the ``shelve`` module in the
  Python Library Reference.  It's not thread safe for the same reason.  If you
  think about using ``fcntl`` in a subclass, see the fcntl caution below.

setup-store.py
--------------

This is a command-line interface to the ``.setup()`` method.  It currently
supports MySQL and PostgreSQL/psycopg with the following syntax::

    $ setup-store.py mysql HOST USER PASSWORD DATABASE [TABLE]
    $ setup-store.py mysql '' joe sEcReT test
    $ setup-store.py mysql '' joe sEcReT test Session

The table name defaults to 'sessions'.  All stores except PostgreSQL
automatically create themselves when instantiated, but this command is
useful if the application won't have permission to create the store.

This command is not installed by ``setup.py``; it's available only in the
application source.  It's not used frequently enough to warrant installation.

Interactive Testing
-------------------

session2 comes with two ways to test it: an interactive web application, and
nose_-based unit tests that require twill_.

To run the unit tests, run ``nosetests``.

To run the web demo, cd to the **test/** directory in the application
source and run one of::

    $ test_session2.py directory
    $ test_session2.py durus
    $ test_session2.py mysql
    $ test_session2.py psycopg
    $ test_session2.py shelve

Point your web browser to **http://localhost:8080/** and play around.
You can use '--host=hostname' and ``--port=N`` to bind to a different hostname
or port.

Press ctrl-C to quit the demo (or command-C on the Mac, or ctrl-Break on
Windows).

See the module source for the filenames, databases, and tables it
uses.  Note that you'll have to create the PostgreSQL table yourself
using 'setup-store.py'.

``fcntl`` Caution
-----------------

On Mac OS X when using PTL, import ``fcntl`` *before* enabling PTL.
Otherwise the import hook may load the deprecated FCNTL.py instead due to
the Mac's case-insensitive filesystem, which will cause errors down the road.
This is supposedly fixed in Python 2.4, which doesn't have FCNTL.py.

.. _Quixote: http://www.mems-exchange.org/software/quixote/
.. _MySQL: http://mysql.org/
.. _PostgreSQL: http://postgresql.org/
.. _Paste: http://pythonpaste.org/
.. _Durus: http://www.mems-exchange.org/software/durus/
.. _twill: http://www.idyll.org/~t/www-tools/twill.html
.. _source documentation: ./epydoc-html/session2-module.html
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
