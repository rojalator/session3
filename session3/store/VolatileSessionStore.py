"""
A simple in-memory volatile session store, mimicking the default
Quixote session management.  Here for example's sake only...
"""

from SessionStore import SessionStore


class VolatileSessionStore(SessionStore):
    """
    A simple volatile (non-persistent) session store for session3.
    """
    is_multiprocess_safe = True
    is_thread_safe = True

    def __init__(self):
        """Create the dictionary."""
        self.sessions = {}

    def load_session(self, id, default=None):
        """Return the session if it exists, else return 'default'."""
        return self.sessions.get(id, default)

    def save_session(self, session):
        """Save the session in the dictionary.."""
        self.sessions[session.id] = session

    def delete_session(self, session):
        """Delete the session in the dictionary."""
        if session.id in self.sessions:
            del self.sessions[session.id]

    def has_session(self, id):
        """Return true if the session exists in the dictionary, else false."""
        return id in self.sessions
