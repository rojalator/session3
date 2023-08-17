
from collections import UserDict
from session3.Session import Session


class DictSession(UserDict, Session):
    """
    A session object that also acts like a dictionary.

    Unlike some object/dict hybrids, keys and attributes are distinct and not
    interchangeable.  Beware of assigning attributes that override dict
    methods.
    """
    def __init__(self, id):
        Session.__init__(self, id)
        UserDict.__init__(self)
