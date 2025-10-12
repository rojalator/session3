from __future__ import annotations

from quixote import get_request, get_publisher, get_cookie, get_response
from quixote.util import randbytes
from session3.Session import Session


class SessionManager:
    """
    A persistent session manager for Quixote.
    """
    ACCESS_TIME_RESOLUTION = 1  # in seconds
    
    def __init__(self, store_obj, session_class=Session):
        """
        `__init__` takes a session store instance and (optionally) the
        session class to use for storing session information. (This defaults to `Session.Session`).
        """
        self.store = store_obj
        self.session_class = session_class
        self.expired_sessions = {}
    
    def __repr__(self):
        return "<%s at %x>" % (self.__class__.__name__, id(self))
    
    def get_session(self) -> Session:
        """
        Fetch or create a session object for the current session, and
        return it.  If a session cookie is found in the HTTP request
        object, use it to look up and return an existing session object.
        If no session cookie is found, create a new session.

        Note that this method does *not* cause the new session to be
        stored in the session manager, nor does it drop a session cookie
        on the user --- those are both the responsibility of [`finish_successful_request()`](#section-14).
        """
        config = get_publisher().config
        id = self._get_session_id(config)
        session = None
        if id:
            session = self.store.load_session(id)
        if session is None:
            session = self._create_session()
        session._set_access_time(self.ACCESS_TIME_RESOLUTION)
        return session
    
    def maintain_session(self, session) -> bool:
        """
        Maintain session information.  This method is called after servicing
        an HTTP request, just before the response is returned.  If a session
        contains information a cookie is dropped on the client and True is
        returned.  If not, the session is forcibly expired and False is
        returned.
        """
        if not session.has_info():
            # Session has no useful info -- forget it.  If it previously
            # had useful information and no longer does, we have to explicitly forget it.
            if session.id and self.has_session(session.id):
                self.expire_session()
            return False
        
        if session.id is None:
            # This is the first time this session has had useful
            # info -- store it and set the session cookie.
            session.id = self._make_session_id()
            self.set_session_cookie(session.id)
        
        return True
    
    def expire_session(self):
        """
        Expire the current session, ie. revoke the session cookie from
        the client, remove the session object from the current request,
        and list it for permanent removal.
        """
        self.revoke_session_cookie()
        request = get_request()
        
        if request.session:
            self.expired_sessions[request] = request.session
            request.session = None
    
    def has_session(self, session_id: str) -> bool:
        """
        Return true if a session identified by 'session_id' exists in
        the session manager.
        """
        return self.store.load_session(session_id)
    
    def clear_session(self, request):
        """
        Clear any residual session information for this request.
        """
        if request in self.expired_sessions:
            del self.expired_sessions[request]
    
    # === Hooks into the Quixote main loop ===
    
    def start_request(self):
        """
        Called near the beginning of each request: after the HTTPRequest
        object has been built, but before we traverse the URL or call the
        callable object found by URL traversal.
        """
        session = self.get_session()
        get_request().session = session
        session.start_request()
    
    def finish_successful_request(self):
        """Called near the end of each successful request.  Not called if
        there were any errors processing the request.
        """
        request = get_request()
        session = request.session
        
        # keep session?
        if session and self.maintain_session(session):
            self.store.save_session(session)
        
        # ...or delete, because it's expired?
        elif request in self.expired_sessions:
            session = self.expired_sessions[request]
            if session.id:
                self.store.delete_session(session)
        
        self.clear_session(request)
    
    def finish_failed_request(self):
        """Called near the end of a failed request (i.e. a exception that was
        not a PublisherError was raised.
        """
        
        request = get_request()
        self.clear_session(request)
    
    # ### CTB: no changes below this line; stolen from SessionManager.
    
    # === Session management ===
    
    # These build on the storage mechanism implemented by the
    # above mapping methods, and are concerned with all the high-
    # level details of managing web sessions
    
    def new_session(self, id: str | None) -> Session:
        """
        Return a new session object, ie. an instance of the session_class
        class passed to the constructor (defaults to `Session`).
        """
        return self.session_class(id)
    
    def _get_session_id(self, config) -> str | None:
        """
        Find the ID of the current session by looking for the session
        cookie in the request.  Return None if no such cookie or the
        cookie has been expired, otherwise return the cookie's value.
        """
        id = get_cookie(config.session_cookie_name)
        if id == "" or id == "*del*":
            return None
        else:
            return id
    
    def _make_session_id(self):
        # Generate a session ID, which is just the value of the session
        # cookie we are about to drop on the user.  (It's also the key
        # used with the session manager mapping interface.)
        id = None
        while id is None or self.has_session(id):
            id = randbytes(8)  # 64-bit random number
        return id
    
    def _create_session(self):
        # Create a new session object, with no ID for now - one will
        # be assigned later if we save the session.
        return self.new_session(None)
    
    def _set_cookie(self, value, **attrs):
        config = get_publisher().config
        name = config.session_cookie_name
        if config.session_cookie_path:
            path = config.session_cookie_path
        else:
            path = get_request().get_environ('SCRIPT_NAME')
            if not path.endswith("/"):
                path += "/"
        domain = config.session_cookie_domain
        
        # Include `secure` and `httponly` as per Quixote 2.7b1
        attrs = attrs.copy()
        if config.session_cookie_secure:
            attrs['secure'] = 1
        if config.session_cookie_httponly:
            attrs['httponly'] = 1
        get_response().set_cookie(name, value, domain=domain, path=path, **attrs)
        return name
    
    def set_session_cookie(self, session_id: str):
        """
        Ensure that a session cookie with value 'session_id' will be
        returned to the client via the response object.
        """
        self._set_cookie(session_id)
    
    def revoke_session_cookie(self):
        """
        Remove the session cookie from the remote user's session by
        resetting the value and maximum age in the response object.  Also
        remove the cookie from the request so that further processing of
        this request does not see the cookie's revoked value.
        """
        cookie_name = self._set_cookie("", max_age=0)
        if get_cookie(cookie_name) is not None:
            del get_request().cookies[cookie_name]
    
    def has_session_cookie(self, must_exist: bool = False) -> bool:
        """
        Return true if the request already has a cookie identifying a
        session object.  If 'must_exist' is true, the cookie must
        correspond to a currently existing session; otherwise (the
        default), we just check for the existence of the session cookie
        and don't inspect its content at all.
        """
        config = get_publisher().config
        id = get_cookie(config.session_cookie_name)
        if id is None:
            return False
        if must_exist:
            return self.has_session(id)
        else:
            return True
