"""Store sessions in individual files within a directory.
RJLRJL: Note that python 3.3. change fcntl to return
OSError instead of IOError

RJLRJL: 19th August 2018
There is a problem with the existing code (adopted from
the python 2 version), which leads to an EOFError: Ran out of input

The code in ::save_session() does::

    f = open(filename, 'wb')

which immediately makes the file zero bytes long. You can try this out in 2
terminals with one doing (where s is some dummy class with s.id as the file-name):-

    >>> import pickle
    >>> pickle.dump(s, f, 4)
    >>> f.close()
    >>> f = open(s.id, 'wb')

If in the other terminal you do::

    >>> f = open(s.id, 'rb')
    >>> o = pickle.load(f)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    EOFError: Ran out of input
    >>>

This is not entirely unexpected BUT the code in load_session()...::

    f = open(filename, 'rb')
    fcntl.flock(f.fileno(), fcntl.LOCK_SH)

...can get the shared lock (LOCK_SH) after save_session() performs
the open() but BEFORE save_session() gets a chance to get the exclusive lock::

    f = open(filename, 'wb')
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)

(You can try it by quickly refreshing a browser calling a Quixote server.)

What happens appears to be::

    save_session() opens the file to write  f = open(filename, 'wb')
    load_session() opens the file to read   f = open(filename, 'rb')
    load_session() asks for and GETS a shared lock [fcntl.LOCK_SH]
    save_session() asks for an exclusive lock BUT gets blocked by the shared lock
    load_session() tries to load the object and gets zero bytes. It then closes the
        file, allowing save_session() to proceed.

All that we need to do, now that we know that save_session() truncates the file
and then waits for an exclusive lock, is have load_session() check for a zero-sized file.
If it has one, then save_session() has just created (or re-created) it and we should let
go and try again.

Addendum:
It turns out that, during testing, one can get at EOFError from pickle anyway, so testing for that
was added too.
"""


import sys

if sys.version_info < (3,4,0):
    sys.stderr.write("You need python 3.4.0 or later to run this script\n")
    exit(1)


import fcntl
import os
import os.path
from pickle import dump, load
from session3.store.SessionStore import SessionStore
import time

SLEEPY_TIME = 0.1


class DirectorySessionStore(SessionStore):
    """
    Store sessions in individual files within a directory.
    """

    is_multiprocess_safe = False  # Needs file locking; OS-specific.
    is_thread_safe = False        # Needs file locking or synchronization.
    # RJLRJL for Python3 we now use the highest protocol at time of writing,
    # being protocol 4 (it was 2)
    pickle_protocol = 4

    def __init__(self, directory, create=False):
        """
        __init__ takes a directory name, with an option to create it if
        it's not already there.
        """
        directory = os.path.abspath(directory)

        # make sure the directory exists:
        if not os.path.exists(directory):
            if create:
                os.mkdir(directory)
            else:
                raise OSError("error, '%s' does not exist." % (directory,))

        # is it actually a directory?
        if not os.path.isdir(directory):
            raise OSError("error, '%s' is not a directory." % (directory,))

        self.directory = directory

    def _make_filename(self, id):
        """Build the filename from the session ID."""
        return os.path.join(self.directory, id)

    def save_session(self, session):
        """Pickle the session and save it into a file."""
        filename = self._make_filename(session.id)
        f = open(filename, 'wb')
        # We wait at the following statement until we get an exclusive lock
        # Note that load_session() can sometimes jump in here before we get the lock
        # (the naughty thing) but it will get a zero-sized file (wb mode truncates the file)
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            dump(session, f, self.pickle_protocol)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            f.close()

    def load_session(self, id, default=None):
        """Load the pickled session from a file."""
        filename = self._make_filename(id)
        finished = False
        while not finished:
            try:
                f = open(filename, 'rb')
                # Sometimes we get the following lock AFTER save_session() has created
                # the file but BEFORE it has locked it. If so, we'll have a zero-sized file
                # (hence the loop, BTW).
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                if os.stat(f.fileno()).st_size == 0:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    f.close()
                    # wait around for a bit...
                    time.sleep(SLEEPY_TIME)
                else:
                    try:
                        obj = load(f)
                        # Don't be tempted to move this into a finally
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        f.close()
                        finished = True
                    except EOFError:
                        # Sometimes we'll also get EOFError from pickle anyway, so we might
                        # as well trap for that too...
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        f.close()
                        time.sleep(SLEEPY_TIME)

            except OSError:
                obj = default
                finished = True

        return obj

    def delete_session(self, session):
        """
        Delete the session file.
        """

        filename = self._make_filename(session.id)
        os.unlink(filename)

    def delete_old_sessions(self, minutes):
        """
        Delete all sessions that have not been modified for N minutes.

        This method is never called by the session manager.  It's for
        your application maintenance program; e.g., a daily cron job.

        DirectorySessionStore.delete_old_sessions returns a tuple:

            (n_deleted, n_remaining)
        """

        deleted = 0
        remaining = 0
        for sess_id in os.listdir(self.directory):
            pth = self._make_filename(sess_id)
            mtime = os.stat(pth).st_mtime
            inactive_for = (time.time() - mtime) / 60.0

            if inactive_for > minutes:
                os.unlink(pth)
                deleted += 1
            else:
                remaining += 1

        return (deleted, remaining)
