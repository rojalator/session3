"""Store sessions in a PostgreSQL table.

Two extra methods are provided, .create_table and .delete_old_sessions.
These are not called by session3 but may be useful in your programs.
They use a third column of type TIMESTAMP, which is updated every time
the row changes.

This module assumes the connection is in transaction-mode (the default
for psycopg).  Use a separate database connection for sessions, or
else your transactions will become confused.

### NOT YET IMPLEMENTED ###
"""

import pickle
from session3.store.SessionStore import SessionStore

DEFAULT_TABLE = 'sessions'


class PostgresSessionStore(SessionStore):
    """
    Store pickled sessions in an SQL database.

    See the create() function for the table definition.

    This implementation has been tested with psycopg.  It should work
    with any DB-API module that supports *connection.rollback()* and
    "%(var)s" substitution style, e.g. psycopg.

    """

    is_multiprocess_safe = True
    is_thread_safe = False       # Can't share db connection between threads.

    def __init__(self, conn, table=None):
        """
        *__init__* takes a psycopg connection to a PostgreSQL database,
        together with an optional table name, 'table'.
        """
        if table is None:
            table = DEFAULT_TABLE

        # @CTB test for table existence

        self.conn = conn
        self.table = table

    # #### SessionStore methods ####
    def load_session(self, id, default=None):
        """
        Load a pickled session from the database.
        """

        self.conn.rollback()
        c = self.conn.cursor()
        c.execute('SELECT pickle FROM sessions WHERE id=%(id)s', dict(id=id))

        if c.rowcount == 0:
            return default
        assert c.rowcount == 1, "more than one session with id %s" % (id,)

        pck = c.fetchone()[0]
        obj = pickle.loads(pck)

        return obj

    def save_session(self, session):
        """
        Pickle session & save it into the database.
        """

        # build a pickle.
        pck = pickle.dumps(session)

        self.conn.rollback()
        c = self.conn.cursor()

        # decide whether to INSERT or UPDATE:
        if self.has_session(session.id):
            sql = 'UPDATE sessions SET pickle=%(p)s, modify_time=now() WHERE id=%(id)s'
        else:
            sql = 'INSERT INTO sessions (id, pickle, modify_time) VALUES (%(id)s, %(p)s, now())'

        c.execute(sql, dict(id=session.id, p=pck))
        self.conn.commit()

    def delete_session(self, session):
        """
        Delete session from the database.
        """

        self.conn.rollback()
        c = self.conn.cursor()
        c.execute('DELETE FROM sessions WHERE id=%(id)s', dict(id=session.id))
        self.conn.commit()

    def setup(self):
        c = self.conn.cursor()
        try:
            c.execute("DROP TABLE %s" % self.table)
        except:                         # table did not exist...
            self.conn.rollback()

        c.execute("""\
CREATE TABLE %s (
   id TEXT PRIMARY KEY NOT NULL,
   pickle TEXT NOT NULL,
   modify_time TIMESTAMP NOT NULL DEFAULT now()
);
""" % self.table)

        self.conn.commit()
