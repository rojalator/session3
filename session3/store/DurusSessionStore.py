"""
Store sessions in a Durus database.

### NOT YET IMPLEMENTED ###
"""

import os, os.path
from session3.store.SessionStore import SessionStore
from durus.persistent_dict import PersistentDict


class DurusSessionStore(SessionStore):
    """
    A session store for Durus, a simple object database.

    Unlike the dulcinea Durus session store, session objects
    themselves are *not* subclasses of Persistent; here they
    are managed by `DurusSessionStore` directly.
    """

    is_multiprocess_safe = True
    is_thread_safe = False       # Durus is not thread safe.

    def __init__(self, connection):
        """
        __init__ takes a Durus `connection` object.
        """

        self.connection = connection
        root = connection.get_root()
        sessions_dict = root.get('sessions')

        if sessions_dict is None:
            sessions_dict = PersistentDict()
            root['sessions'] = sessions_dict
            connection.commit()

        self.sessions_dict = sessions_dict

    def load_session(self, id, default=None):
        """
        Load the session from the shelf.
        """
        self.connection.abort()
        return self.sessions_dict.get(id, default)

    def delete_session(self, session):
        """
        Delete the given session from the shelf.
        """
        del self.sessions_dict[session.id]
        self.connection.commit()

    def save_session(self, session):
        """
        Save the session to the shelf.
        """
        self.sessions_dict[session.id] = session
        self.connection.commit()
