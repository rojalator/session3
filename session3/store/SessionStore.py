"""
Base class for persistent session stores.
"""


class SessionStore:
    """
    Persistent `Session` storage API for session3's `SessionManager`.

    Subclass this class & provide implementations of `load_session`,
    `save_session`, and `delete_session`, and voila, persistent sessions!
    """

    is_multiprocess_safe = False
    is_thread_safe = False

    # ### Methods called by the SessionManager ###
    def load_session(self, id, default=None):
        """Return the session if it exists, else return 'default'."""
        raise NotImplementedError()

    def save_session(self, session):
        """Save the session in the store."""
        raise NotImplementedError()

    def delete_session(self, session):
        """Delete the session in the store."""
        raise NotImplementedError()

    def has_session(self, id):
        """Return true if the session exists in the store, else false."""
        return self.load_session(id, None)

    # ### Other methods ###
    def iter_sessions(self):
        """
        Return an iterable of (id, session) for all sessions in the store.

        This method is never called by the session manager; it's for admin
        applications that want to browse the sessions.
        """
        raise NotImplementedError()

    def setup(self):
        """
        Initialize the session store; e.g., create required database tables.
        If a previous store exists, overwrite it or raise an error.  The
        default implmenetation does nothing, meaning no setup is necessary.

        This method is never called by the session manager; it's for your
        application setup program.
        """
        pass

    def delete_old_sessions(self, minutes):
        """
        Delete all sessions that have not been modified for N minutes.  The
        default implementation does nothing, meaning the store cannot delete
        old sessions.

        This method is never called by the session manager.  It's for your
        application maintenance program; e.g., a daily cron job.
        """
        pass
