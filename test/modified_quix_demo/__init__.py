from quixote import enable_ptl
from quixote.publish import Publisher

enable_ptl()
from .root import RootDirectory


print('Modified demo running for session3 tests')


def create_publisher():
    # from quixote.demo.root import RootDirectory
    # import RootDirectory
    return Publisher(RootDirectory(), display_exceptions='plain')
