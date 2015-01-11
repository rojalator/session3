"""
Store sessions in individual files within a directory.
"""

import fcntl, os, os.path
from cPickle import dump, load
from session2.store.SessionStore import SessionStore
import time

class DirectorySessionStore(SessionStore):
    """
    Store sessions in individual files within a directory.
    """

    is_multiprocess_safe = False  # Needs file locking; OS-specific.
    is_thread_safe = False        # Needs file locking or synchronization.
    pickle_protocol = 2
    
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
        """
        Build the filename from the session ID.
        """
        return os.path.join(self.directory, id)
        
    def load_session(self, id, default=None):
        """
        Load the pickled session from a file.
        """
        
        filename = self._make_filename(id)
        try:
            f = open(filename)
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                obj = load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                f.close()
        except IOError:
            obj = default

        return obj

    def save_session(self, session):
        """
        Pickle the session and save it into a file.
        """
        filename = self._make_filename(session.id)
        f = open(filename, 'w')
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            dump(session, f, self.pickle_protocol)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            f.close()

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
