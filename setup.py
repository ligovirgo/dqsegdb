#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import glob
import os.path
from distutils.command import install
from setuptools import (setup, find_packages)

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

# extend install to write environment scripts
shenv = os.path.join('etc', '%s-user-env.sh' % PACKAGENAME)
cshenv = os.path.join('etc', '%s-user-env.csh' % PACKAGENAME)

class DQSegDBInstall(install.install):
    """Extension of setuptools install to write source script for
    users.
    """
    def _get_install_paths(self):
        """Internal utility to get install and library paths for install.
        """
        installpath = self.install_scripts
        if self.install_purelib == self.install_platlib:
            pythonpath = self.install_purelib
        else:
            pythonpath = os.pathsep.join([self.install_platlib,
                                          self.install_purelib])
        return installpath, pythonpath

    def write_env_sh(self, fp=shenv):
        """Write the shell environment script for DQSegDB.

        Parameters
        ----------
        fp : `str`
            path (relative to install prefix) of output csh file
        """
        installpath, pythonpath = self._get_install_paths()
        with open(fp, 'w') as env:
            print('#!/bin/sh\n', file=env)
            print('PATH=%s:${PATH}' % (installpath), file=env)
            print('export PATH', file=env)
            print('PYTHONPATH=%s:${PYTHONPATH}' % (pythonpath), file=env)
            print('export PYTHONPATH', file=env)

    def write_env_csh(self, fp=cshenv):
        """Write the shell environment script for DQSegDB.

        Parameters
        ----------
        fp : `str`
            path (relative to install prefix) of output csh file
        """
        installpath, pythonpath = self._get_install_paths()
        with open(fp, 'w') as env:
            print('setenv PATH %s:${PATH}' % (installpath), file=env)
            print('setenv PYTHONPATH %s:${PYTHONPATH}' % (pythonpath),
                  file=env)

    def run(self):
        self.write_env_sh()
        self.write_env_csh()
        install.install.run(self)
        print("\n--------------------------------------------------")
        print("DQSegDB has been installed.")
        print("If you are running csh, you can set your environment by "
              "running:\n")
        print("source %s\n" % os.path.join(self.install_base, cshenv))
        print("Otherwise, you can run:\n")
        print("source %s" % os.path.join(self.install_base, shenv))
        print("--------------------------------------------------")
    run.__doc__ = install.install.__doc__


setup(name=PACKAGENAME,
      cmdclass={'install': DQSegDBInstall},
      version=VERSION,
      description=DESCRIPTION,
      packages=packagenames,
      ext_modules=[],
      scripts=scripts,
      data_files=[('etc', [shenv, cshenv])],
      install_requires=['glue', 'pyRXP'],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,
      use_2to3=True
      )
