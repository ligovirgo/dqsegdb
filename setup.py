# -*- coding: utf-8 -*-

import glob
import os.path
from setuptools import (setup, find_packages)

PACKAGENAME = 'dqsegdb'
DESCRIPTION = 'Client library for DQSegDB'
LONG_DESCRIPTION = ''
AUTHOR = 'Ryan Fisher'
AUTHOR_EMAIL = 'ryan.fisher@ligo.org'
LICENSE = 'GPLv3'

# -- versioning ---------------------------------------------------------------

import versioneer
__version__ = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()

# -- setup ---------------------------------------------------------------------

# Use the find_packages tool to locate all packages and modules
packagenames = find_packages()

# glob for all scripts
if os.path.isdir('bin'):
    scripts = glob.glob(os.path.join('bin', '*'))
else:
    scripts = []

setup(name=PACKAGENAME,
      cmdclass=cmdclass,
      version=__version__,
      description=DESCRIPTION,
      url="http://www.lsc-group.phys.uwm.edu/daswg/",
      packages=packagenames,
      ext_modules=[],
      scripts=scripts,
      setup_requires=['setuptools'],
      install_requires=[
          'pyRXP',
          'ligo-segments',
          'lscsoft-glue>=1.55.0',
          'pyOpenSSL>=0.14',
          'six',
          'gwdatafind',
      ],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,
      use_2to3=False
      )
