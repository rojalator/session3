#!/usr/bin/env python3
"""
Quixote test app for session3 integration testing.

Provides endpoints:
  /           - Show session status
  /login      - Login form and handler
  /logout     - Logout and expire session
  /counter    - Increment a counter in session
  /check      - Return session info as plain text
  /create_token - Create a form token in session
  /check_token  - Check if session has form tokens
  /delete_old - Delete old sessions from store

Run with: python -m quixote run --app test_runner
"""

import os
import sys
from quixote import get_user, get_session, get_session_manager, get_field
from quixote.directory import Directory
from quixote.html import htmltext

SESSION_DIR = '/tmp/session3_test_runner'


class RootDirectory(Directory):
    """Root directory with session-aware endpoints for testing."""

    _q_exports = ['', 'login', 'logout', 'counter', 'check', 'create_token', 'check_token', 'delete_old']

    def _q_index(self):
        user = get_user()
        session = get_session()
        if user:
            content = (htmltext('<p>Hello, %(user)s!</p><p>Session ID: %(session_id)s</p><p>Counter: %(counter)s</p><p>%(logout_link)s</p>') %
                       {'user': user, 'session_id': session.id[:16] + '...' if session.id else 'None', 'counter': getattr(session, 'counter', 0),
                        'logout_link': htmltext('<a href="logout">logout</a>')})
        else:
            content = htmltext('<p>Not logged in.</p><p><a href="login">login</a></p>')
        return htmltext('<html><head><title>Session3 Test</title></head><body>%(content)s</body></html>') % locals()

    def login(self):
        if get_field("name"):
            session = get_session()
            session.set_user(get_field("name"))
            session.counter = 0
            return htmltext('<html><body><p>Welcome! %(user)s</p><p><a href=".">back</a></p></body></html>') % {'user': get_user()}
        else:
            return htmltext('<html><body><form method="POST" action="login"><input name="name" /><input type="submit" value="Login" /></form></body></html>')

    def logout(self):
        get_session_manager().expire_session()
        return htmltext('<html><body><p>Goodbye!</p><p><a href=".">start over</a></p></body></html>')

    def counter(self):
        """Increment a counter in the session."""
        session = get_session()
        session.counter = getattr(session, 'counter', 0) + 1
        return htmltext('<html><body><p>Counter: %(counter)s</p><p><a href=".">back</a></p></body></html>') % {'counter': session.counter}

    def create_token(self):
        """Create a form token in the session."""
        session = get_session()
        token = session.create_form_token()
        return htmltext('<html><body><p>Token created: %(token)s</p><p><a href=".">back</a></p></body></html>') % {'token': token[:16] + '...'}

    def check_token(self):
        """Check if session has form tokens."""
        session = get_session()
        return '\n'.join([f"session_id: {session.id}", f"user: {session.user}", f"has_form_tokens: {len(session._form_tokens) > 0}",
                          f"form_token_count: {len(session._form_tokens)}", f"Access time: {session._access_time}"])

    def delete_old(self, minutes=0):
        """Call delete_old_sessions on the store."""
        store = get_session_manager().store
        deleted, remaining = store.delete_old_sessions(int(minutes))
        return (htmltext('<html><body><p>Deleted: %(deleted)s, Remaining: %(remaining)s</p></body></html>') %
                {'deleted': deleted, 'remaining': remaining})

    def check(self):
        """Return session info as plain text for testing."""
        session = get_session()
        return '\n'.join([f"session_id: {session.id}", f"user: {session.user}", f"counter: {getattr(session, 'counter', 'N/A')}",
                          f"has_info: {session.has_info()}", f"form_tokens_count: {len(session._form_tokens)}",
                          f"has_form_tokens: {len(session._form_tokens) > 0}", f"Access time: {session._access_time}"])


def create_publisher():
    """Create publisher with session3 - required by quixote run."""
    import shutil
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from session3.SessionManager import SessionManager
    from session3.store.DirectorySessionStore import DirectorySessionStore
    from quixote.publish import Publisher

    # Clean up any old session dir
    if os.path.exists(SESSION_DIR):
        shutil.rmtree(SESSION_DIR)
    os.makedirs(SESSION_DIR, exist_ok=True)

    # Create session store and manager
    store = DirectorySessionStore(SESSION_DIR, create=True)
    session_manager = SessionManager(store)

    return Publisher(RootDirectory(), session_manager=session_manager, display_exceptions='plain')
