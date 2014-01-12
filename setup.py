#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os.path
from setuptools import setup, find_packages

utils = __import__('utils', fromlist=['version'], level=1)

PACKAGENAME = 'dqsegdb'
DESCRIPTION = 'Client library for DQSegDB'
LONG_DESCRIPTION = ''
AUTHOR = 'Ryan Fisher'
AUTHOR_EMAIL = 'ryan.fisher@ligo.org'
LICENSE = None

# set version information
VERSION_PY = '%s/version.py' % PACKAGENAME
vcinfo = utils.version.GitStatus()
vcinfo(VERSION_PY, PACKAGENAME, AUTHOR, AUTHOR_EMAIL)

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = vcinfo.version

# Indicates if this version is a release version
RELEASE = vcinfo.version != vcinfo.id and 'dev' not in VERSION

# Use the find_packages tool to locate all packages and modules
packagenames = find_packages()

# glob for all scripts
if os.path.isdir('bin'):
    scripts = glob.glob(os.path.join('bin', '*'))
else:
    scripts = []

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      packages=packagenames,
      ext_modules=[],
      scripts=scripts,
      install_requires=['glue', 'pyRXP'],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,
      use_2to3=True
      )
