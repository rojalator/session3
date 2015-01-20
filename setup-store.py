#!/usr/bin/env python3
"""Initialize a session store.
"""
import os, sys
#import pickle as pickle

# RJLRJL Converted to Python3

if sys.version_info < (3,4,0):
    sys.stderr.write("You need python 3.4.0 or later to run this script\n")
    exit(1)

##########
def usage():
    dic = {'prog': os.path.basename(sys.argv[0])}
    print("""\
Usage:
    %(prog)s mysql     HOST USER PASSWORD DATABASE [TABLE]
    %(prog)s psycopg   HOST USER PASSWORD DATABASE [TABLE]
Hints:
    Use HOST='' or 'localhost' for localhost;
    for psycopg/PostgreSQL, USER='' and PASSWORD='' will use default user/pass.
""" % dic, end=' ')

##########
def error(store_type, message, print_usage=True):
    if store_type:
        prefix = store_type.upper() + ' '
    else:
        prefix = ''
    print("%sERROR: %s" % (prefix, message))
    if print_usage:
        usage()
    sys.exit(1)

def mysql(args):
    import MySQLdb
    from .session3.store.MySQLSessionStore import MySQLSessionStore
    from .session3.store.MySQLSessionStore import DEFAULT_TABLE as table
    if   len(args) == 5:
        table = args[4]
    elif len(args) == 4:
        pass
    else:
        error("mysql", "incorrect number of command-line arguments")
    host, user, passwd, db = args[:4]
    print("Creating MySQL table %r in database %r" % (table, db))
    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    store = MySQLSessionStore(conn, table)
    store.setup()

def psycopg(args):
    import psycopg
    from .session3.store.PostgresSessionStore import PostgresSessionStore
    from .session3.store.PostgresSessionStore import DEFAULT_TABLE as table
    if   len(args) == 5:
        table = args[4]
    elif len(args) == 4:
        pass
    else:
        error("psycopg", "incorrect number of command-line arguments")
    host, user, passwd, db = args[:4]
    print("Creating PostgreSQL table %r in database %r" % (table, db))
    conn_str = "dbname=%s" % (db,)
    if host:
        conn_str += " host=%s" % (host,)
    if user:
        conn_str += " user=%s" % (user,)
    if passwd:
        conn_str += " password=%s" % (passwd,)
    conn = psycopg.connect(conn_str)
    store = PostgresSessionStore(conn, table)
    store.setup()

def main():
    args = sys.argv[1:]
    if not args:
        error(None, "no storage type specified")
    action = args.pop(0)
    if   action == "mysql":
        mysql(args)
    elif action == "psycopg":
        psycopg(args)
    elif action in ['help', '--help', '-h']:
        usage()
    else:
        error(None, "unrecognised storage type")

if __name__ == "__main__":  main()
