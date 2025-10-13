#!/usr/bin/env python3

# RJLRJL Converted to Python3

import sys

if sys.version_info < (3, 9, 0):
    sys.stderr.write("You need python 3.9.0 or later to run this script\n")
    exit(1)

import setuptools

with open("README.rst", "r") as fh:
    read_long_description = fh.read()

setuptools.setup(
    name="session3",
    version="3.4.1",
    author="R J Ladyman [C. Titus Brown (titus@caltech.edu), and Mike Orr (mso@oz.net) for session2]",
    author_email="it@file-away.co.uk",
    description="Persistent sessions for Quixote 3",
    long_description=read_long_description,
    long_description_content_type="text/x-rst",
    url="http://www.file-away.co.uk/session3/README.html",
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Session"
    ],
    python_requires='>=3.9',
    platforms='Most'
)
