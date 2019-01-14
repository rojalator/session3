#!/usr/bin/env python3

# RJLRJL Converted to Python3

import sys

if sys.version_info < (3,4,0):
    sys.stderr.write("You need python 3.4.0 or later to run this script\n")
    exit(1)

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="session3",
    version="3.0.post0",
    author="R J Ladyman [C. Titus Brown (titus@caltech.edu), and Mike Orr (mso@oz.net) for session2]",
    author_email="it@file-away.co.uk",
    description="Persistent sessions for Quixote 3.0.0",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="http://www.file-away.co.uk/quixote/session3/",
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
	install_requires = ["Quixote>=3.0.0,<=3.0.0"],
    python_requires='>=3.4',
    platforms='Most'
)


