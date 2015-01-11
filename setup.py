#!/usr/bin/env python3

# RJLRJL Converted to Python3

import sys

if sys.version_info < (3,4,0):
    sys.stderr.write("You need python 3.4.0 or later to run this script\n")
    exit(1)


from distutils.core import setup

setup(name = 'session3',
      version = '3.0',
      description = 'Persistent sessions for Quixote 2.x',
      author = 'C. Titus Brown and Mike Orr',
      author_email = 'titus@caltech.edu, mso@oz.net',
      packages = ['session3', 'session3.store'],
      license='MIT',
      url = 'http://quixote.idyll.org/session2/')
