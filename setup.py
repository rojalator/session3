from distutils.core import setup

setup(name = 'session2',
      version = '0.6',
      description = 'Persistent sessions for Quixote 2.x',
      author = 'C. Titus Brown and Mike Orr',
      author_email = 'titus@caltech.edu, mso@oz.net',
      packages = ['session2', 'session2.store'],
      license='MIT',
      url = 'http://quixote.idyll.org/session2/')
