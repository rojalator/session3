"""
Store sessions in a 'shelve' database.
"""

import shelve
from session3.store.SessionStore import SessionStore


class ShelveSessionStore(SessionStore):
    """
    Open a 'shelve' dictionary with the given filename, and store sessions
    in it.

    Shelve is not thread safe or multiprocess safe.  See the "Restrictions"
    section for the shelve module in the Python Library Reference for
    information about file locking.
    """

    is_multiprocess_safe = False  # DBM isn't process safe.
    is_thread_safe = False        # Don't know about this...

    def __init__(self, filename):
        """
        __init__ takes the filename to use as the shelve store.
        """
        self.filename = filename

    def open(self):
        """
        Open the shelve store file.
        """
        return shelve.open(self.filename, 'c')

    def load_session(self, id, default=None):
        """
        Load the session from the shelf.
        """

        db = self.open()
        return db.get(id, default)

    def delete_session(self, session):
        """
        Delete the given session from the shelf.
        """
        db = self.open()
        del db[session.id]

    def save_session(self, session):
        """
        Save the session to the shelf.
        """
        db = self.open()
        db[session.id] = session
