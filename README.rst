=======================================================
Session3: Persistent Session Management for Quixote 3.0
=======================================================

:Authors: R J Ladyman, (based upon session2 by C Titus Brown and Mike Orr)
:Email: it@file-away.co.uk
:License: MIT  (http://www.opensource.org/licenses/mit-license.php)
:Version: 3-3.0.post0 released 2019-01-14
:Status: Only the file-storage mechanism (DirectorySessionStore) is working with Quixote 3.0+

.. contents::

Introduction
============

Quixote_ is a Python Web application framework.  It comes with an
in-memory session manager, which works but is incompatible with
multi-process servers (SCGI, CGI, etc) ---  it also forgets the sessions
when the Publisher quits.  Session3_ solves these problems by
providing a new session manager class and a simple back-end storage
API. [#previousversion]_

Session3 version 3.0.0 provides a fully functional [#limited]_ persistent storage
 back-end for use with Quixote 3.0.0 and above (also see Road-map_ below, for later version notes):-

DirectorySessionStore_ (DirectorySessionStoreAPI_)
  Store each pickled session in a file in the designated directory.  The
  filename is the session ID.  Uses ``fcntl`` file locking.  ::

      DirectorySessionStore(directory)


This package includes a refactored SessionManager_ (SessionManagerAPI_) that makes it easy to develop
additional back ends along with a simplified Session class (no ``.is_dirty`` method).
It supports the usual ``.user``, ``.set_user()`` and ``.has_info()``
attributes and you can also set your own attributes which will be saved.

It's quite likely that the session stores can be adapted for use with other
Web frameworks; let us know if you do this so we can link to you and / or
include helpful code in the package.

Road-map
--------
Quixote (at time of writing - January 2019) is at version 3.0.0 and Session3 works with that
(stable) version.

Quixote 3.1.x has added BaseSessionManager and SessionStore classes requiring Session3
to be updated (the new
Session3 version-number will reflect the Quixote version it works with).

Getting Session3
================

Installation
------------
Session3 can be installed via pip (``pip3 install session3``).
Alternatively (or if you also want the documentation) download and unpack
the tar.gz file and install the normal Python way (``python3
setup.py install``). Note that Session3 requires Quixote 3.0.0 --- this
is also available via pip or from Quixote_.

Documentation
-------------
`API documentation`_ is available as is `Literate Programming documentation`_ ---
either read it on-line or extract it from the tar.gz file.


Using session3
==============

You need a *store*, a *manager* and then you need to tell Quixote's
publisher to use them both: in your `create_publisher` function, place the following code::

    # create the session store.
    from session3.store.DirectorySessionStore import DirectorySessionStore
    from session3.SessionManager import SessionManager

    # create the session manager.
    store = DirectorySessionStore(path.expanduser(some_location), create=True)
    session_manager = SessionManager(store)

    # create the publisher.
    from quixote.publish import Publisher
    publisher = Publisher(..., session_manager.session_manager)

Each session store has different initialization requirements:[#limited]_ see
the `API documentation`_ or the `literate programming documentation`_ for more information.


Features
========

All session stores have the following methods, which are called by the session
manager:-

``.load_session``, ``.save_session``, ``.delete_session``,
``.has_session``.

They also have these convenience methods:-

``.setup()``:
	initializes the store.

``.delete_old_sessions(minutes)``:
	deletes sessions that haven't been modified for N minutes.
	This is meant for your application maintenance program; e.g.,
	a daily cron job.

``.iter_sessions()``:
	Return an iterable of (id, session) for all sessions
	in the store.  This is for admin applications that want to browse the sessions.
	The DirectorySession will raise a *NotImplementedError* [#wasinsession2]_.

All stores have ``.is_multiprocess_safe`` and ``.is_thread_safe`` attributes.
An application can check these flags and abort if configured inappropriately.
The flags are defined as follows:-

- DirectorySessionStore is multiprocess safe because it uses ``fcntl`` file
  locking.  This limits its use to POSIX.  See the fcntl caution below.  It may
  be thread safe because it always locks-unlocks within the same method, but we
  don't know for sure so the attribute is false. [#limited]_

Interactive Testing
-------------------

Session3 comes with an interactive web test application. To run the web demo,
cd to the **test/** directory in the application source and run::

    $ test_session2.py directory

Point your web browser to http://localhost:8080/  and play around.
You can use ``--host=hostname`` and ``--port=N`` to bind to a different hostname
or port.

Press ctrl-C to quit the demo (or command-C on the Mac, or ctrl-Break on
Windows).

``fcntl`` Caution
-----------------

On Mac OS X when using PTL, import ``fcntl`` *before* enabling PTL.
Otherwise the import hook may load the deprecated FCNTL.py instead due to
the Mac's case-insensitive filesystem, which will cause errors down the road.
This was supposedly fixed in Python 2.4, which doesn't have FCNTL.py.

Changes from Session2
---------------------
Since Session2 was released a number of packages that were referred to in the documentation (and the source)
have either ceased to exist or moved into maintenance mode and Session3 itself is solely for Python 3.

 * Nose_ is in maintenance mode
 * The original web-site for Twill_ has disappeared. Existing Twill code appears to be Python 2 only. There
   is a new version at TwillTools_

.. _xxQuixote: http://www.mems-exchange.org/software/quixote/
.. _Quixote: https://github.com/nascheme/quixote
.. _MySQL: http://mysql.org/
.. _PostgreSQL: http://postgresql.org/
.. _Paste: https://github.com/cdent/paste/
.. _Durus: http://www.mems-exchange.org/software/durus/
.. _Twill: https://pypi.org/project/twill/
.. _TwillTools: https://github.com/twill-tools/twill
.. _api documentation: https://rojalator.github.io/session3/moduleIndex.html
.. _literate programming documentation: https://rojalator.github.io/session3/literate/
.. _nose: https://nose.readthedocs.io/en/latest/
.. _session3: https://github.com/rojalator/session3


.. _DirectorySessionStore: https://rojalator.github.io/session3/literate/session3/store/DirectorySessionStore.html
.. _DirectorySessionStoreAPI: https://rojalator.github.io/session3/session3.store.DirectorySessionStore.html
.. _SessionManager: https://rojalator.github.io/session3/literate/session3/SessionManager.html
.. _SessionManagerAPI: https://rojalator.github.io/session3/session3.SessionManager.SessionManager.html

.. _DurusSessionStore: https://rojalator.github.io/session3/literate/session3/store/DurusSessionStore.html
.. _MySQLSessionStore: https://rojalator.github.io/session3/literate/session3/store/MySQLSessionStore.html
.. _PostgresSessionStore: https://rojalator.github.io/session3/literate/session3/store/PostgresSessionStore.html
.. _ShelveSessionStore:https://rojalator.github.io/session3/literate/session3/store/ShelveSessionStore.html



--------------

.. [#limited] Note that only DirectorySessionStore_ is working for version 3.0
.. [#dict_note] DictSession is especially useful for applications that may want
   to use `Paste`_'s session middleware in the future, because it is dict-based.
   However, the migration for ``.user`` and ``.set_user()`` is not yet clear.
.. [#wasinsession2] For the Session2 code, this *was* implemented but *only* for MySQL
.. [#previousversion] Session3 is based upon the previous Session2 code (designed for, unsurprisingly, Quixote 2).
