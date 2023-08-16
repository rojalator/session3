"""Store sessions in a MySQL table.

Two extra methods are provided, .create_table and .delete_old_sessions.
These are not called by session3 but may be useful in your programs.
They use a third column of type TIMESTAMP, which MySQL automatically updates
whenever the row changes.

This module assumes the table is non-transactional (no commit or rollback).
That's the most popular type of MySQL table, and you can't rollback a
non-transactional table or you'll sometimes get an "incomplete rollback error".

Use a separate database connection for sessions than for your other SQL code,
to avoid incompatible code stomping on each other's transactions.

### NOT YET IMPLEMENTED ###
"""

from array import array
import pickle
from session3.store.SessionStore import SessionStore

DEFAULT_TABLE = "sessions"


class MySQLSessionStore(SessionStore):
    is_multiprocess_safe = True
    is_thread_safe = False  # Can't share db connection between threads.
    pickle_protocol = 2

    def __init__(self, conn, table=None):
        """
        `__init__` takes a MySQLdb connection object, together with an
        optional 'table' argument containing the name of the table to use.
        """
        if table is None:
            table = DEFAULT_TABLE
        self.conn = conn
        self.table = table
        c = conn.cursor()
        c.execute("SHOW TABLES")
        tables = [x[0] for x in c.fetchall()]
        if table not in tables:
            self.setup()

    # #### SessionStore methods ###
    def load_session(self, id, default=None):
        c = self.conn.cursor()
        sql = "SELECT pickle FROM %s WHERE id=%%(id)s" % self.table
        dic = {'id': id}
        c.execute(sql, dic)
        if c.rowcount == 0:
            return default
        assert c.rowcount == 1, "more than one session with id %s" % (id,)
        pck = c.fetchone()[0]
        if isinstance(pck, array):  # Object may be array.array('c') type.
            pck = pck.tostring()
        obj = pickle.loads(pck)
        return obj

    def save_session(self, session):
        pck = pickle.dumps(session, self.pickle_protocol)
        c = self.conn.cursor()
        sql = "REPLACE INTO %s (id, pickle) VALUES (%%(id)s, %%(p)s)"
        sql %= self.table
        dic = {'id': session.id, 'p': pck}
        c.execute(sql, dic)

    def delete_session(self, session):
        c = self.conn.cursor()
        sql = "DELETE FROM %s WHERE id=%%(id)s" % self.table
        dic = {'id': session.id}
        c.execute(sql, dic)

    # ### Other methods ###
    def iter_sessions(self):
        c = self.conn.cursor()
        sql = "SELECT id, pickle FROM %s" % self.table
        c.execute(sql)
        return c.fetchall()

    def setup(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS %s" % self.table)
        c.execute("""\
CREATE TABLE %s (
id VARCHAR(255) NOT NULL PRIMARY KEY,
pickle BLOB NOT NULL,
modify_time TIMESTAMP)""" % self.table)

    def delete_old_sessions(self, minutes):
        c = self.conn.cursor()
        sql = """\
DELETE FROM %s WHERE 
modify_time < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL %%(minutes)s MINUTE)"""
        sql %= self.table
        dic = {'minutes': minutes}
        c.execute(sql, dic)
