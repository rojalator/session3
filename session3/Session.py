# == Session storage class for Quixote 2.x. ==


from time import time, strftime, localtime
from quixote import get_request
from quixote.util import randbytes


class Session:
    """Holds information about the current session.

    The only information that is likely to be useful to applications is the `user` attribute,
    which applications can use as they please.[^1]

    *See Also: [[SessionManager.py]]*

    Instance attributes:-

     * id : string

        the session ID (generated by SessionManager and used as the
        value of the session cookie)

     * user : any

        an object to identify the human being on the other end of the
        line.  It's up to you whether to store just a string in `user`,
        or some more complex data structure or object.

     * _remote_address : string

        IP address of user owning this session (only set when the
        session is created)

     * _creation_time : float

     * _access_time : float

        two ways of keeping track of the "age" of the session.
        Note that `__access_time` is maintained by the `SessionManager` that
        owns this session, using [`_set_access_time()`](#methods-for-sessionmanager-only).

     * _form_tokens : string

        Added from N.S.'s code ---
        Outstanding form tokens.  This is used as a queue that can grow
        up to `MAX_FORM_TOKENS`.  Tokens are removed when forms are submitted.

    Feel free to access `id` and `user` directly, but do not modify
    `id`.  The preferred way to set `user` is with the `set_user()` method
    (which you might want to override for type-checking).

    [^1]:Note that this class may be split into a `SimpleSession` superclass
    and a `Session` subclass in the future.
    """

    # Maximum number of outstanding form tokens
    # Increased from 16 to 32, RJL 2019-10-22
    MAX_FORM_TOKENS = 32

    def __init__(self, id):
        r"""\__init__ is called only by `SessionManager.SessionManager`"""
        self.id = id
        self.user = None
        self._remote_address = get_request().get_environ("REMOTE_ADDR")
        self._creation_time = self._access_time = time()
        # `_form_tokens` is a queue  --- see the [Form token methods](#form-token-methods) below
        self._form_tokens = []

    def __repr__(self):
        return "<%s at %x: %s>" % (self.__class__.__name__, id(self), self.id)

    def __str__(self):
        if self.user:
            return "session %s (user %s)" % (self.id, self.user)
        else:
            return "session %s (no user)" % self.id

    def has_info(self):
        """() -> boolean
        Return True if this session contains any information that must
        be saved.
        """
        return self.user

    def dump(self, file=None, header=True, deep=True):
        time_fmt = "%Y-%m-%d %H:%M:%S"
        ctime = strftime(time_fmt, localtime(self._creation_time))
        atime = strftime(time_fmt, localtime(self._access_time))

        if header:
            file.write('session %s:' % self.id)
        file.write('  user %s' % self.user)
        file.write('  _remote_address: %s' % self._remote_address)
        file.write('  created %s, last accessed %s' % (ctime, atime))
        file.write('  _form_tokens: %s\n' % self._form_tokens)

    def start_request(self):
        """
        Called near the beginning of each request: after the `HTTPRequest`
        object has been built, but before we traverse the URL or call the
        callable object found by URL traversal.
        """
        pass

    # === Simple accessors and modifiers ===

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

    def get_remote_address(self):
        """
        Return the IP address (dotted-quad string) that made the initial request in this session.
        """
        return self._remote_address

    def get_creation_time(self):
        """
        Return the time that this session was created (seconds since epoch).
        """
        return self._creation_time

    def get_access_time(self):
        """
        Return the time that this session was last accessed (seconds since epoch).
        """
        return self._access_time

    def get_creation_age(self, _now=None):
        """
        Return the number of seconds since session was created.
         `_now` arg is not strictly necessary, but there for consistency
         with `get_access_age()`
         """
        return (_now or time()) - self._creation_time

    def get_access_age(self, _now=None):
        """
        Return the number of seconds since session was last accessed.

        `_now` arg is for `SessionManager`'s use
        """
        return (_now or time()) - self._access_time


    # === Methods for SessionManager only ===
    def _set_access_time(self, resolution):
        now = time()
        if now - self._access_time > resolution:
            self._access_time = now


    # === Form token methods ===

    def create_form_token(self):
        """() -> string

        Create a new form token and add it to a queue of outstanding form
        tokens for this session.  A maximum of `MAX_FORM_TOKENS` are saved.
        The new token is returned.
        """
        token = randbytes(16)
        self._form_tokens.append(token)
        extra = len(self._form_tokens) - self.MAX_FORM_TOKENS
        if extra > 0:
            del self._form_tokens[:extra]
        return token

    def has_form_token(self, token):
        """(token : string) -> boolean

        Return True if `token` is in the queue of outstanding tokens.
        """
        return token in self._form_tokens

    def remove_form_token(self, token):
        """(token : string)

        Remove `token` from the queue of outstanding tokens.
        """
        self._form_tokens.remove(token)

