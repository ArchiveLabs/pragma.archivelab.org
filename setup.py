#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    setup.py
    ~~~~~~~~

    An API for citing Wayback Snapshots with OpenAnnotations

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

import codecs
import os
import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Taken from pypa pip setup.py:
    intentionally *not* adding an encoding option to open, See:
       https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    """
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='pragma',
    version=find_version("pragma", "__init__.py"),
    description='An API for citing Wayback Snapshots with OpenAnnotations',
    long_description=read('README.rst'),
    classifiers=[
        ],
    author='mek',
    author_email='michael.karpeles@gmail.com',
    url='',
    packages=[
        'pragma'
        ],
    platforms='any',
    license='LICENSE',
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask-routing',
        'flask-cors'
        ]
)
