#!/usr/bin/env python3

# RJLRJL Converted to Python3

import sys

if sys.version_info < (3,4,0):
    sys.stderr.write("You need python 3.4.0 or later to run this script\n")
    exit(1)


from distutils.core import setup

setup(name = 'session3',
      version = '3.0.0',
      description = 'Persistent sessions for Quixote 3.0',
      author = 'R J Ladyman [C. Titus Brown (titus@caltech.edu), and Mike Orr (mso@oz.net) for session2]',
      author_email = 'it@file-away.co.uk',
      packages = ['session3', 'session3.store'],
      license='MIT',
      url = 'http://www.file-away.co.uk/quixote/session3/',
      long_description=open('README.txt').read()
      )

#    install_requires = [
#        "Quixote" = "3.0",
#        ]
