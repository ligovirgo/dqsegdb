#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import glob
import os.path
import subprocess
from distutils import log
from setuptools import (setup, find_packages)
from setuptools.command import (build_py, install, sdist)

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


# -- custom install with etc scripts ------------------------------------------

Install = cmdclass.pop('install', install.install)


class DQSegDBInstall(Install):
    """Extension of setuptools install to write source script for
    users.
    """
    shenv = os.path.join('etc', '%s-user-env.sh' % PACKAGENAME)
    cshenv = os.path.join('etc', '%s-user-env.csh' % PACKAGENAME)

    def finalize_options(self):
        Install.finalize_options(self)
        try:
            etc = zip(*self.distribution.data_files)[0].index('etc')
        except TypeError:
            self.distribution.data_files = [('etc', [])]
            etc = 0
        except (ValueError, IndexError):
            self.distribution.data_files.append(('etc', []))
            etc = 0
        self.data_files = self.distribution.data_files[etc][1]

    def _get_install_paths(self):
        """Internal utility to get install and library paths for install.
        """
        installpath = self.install_scripts
        if self.install_purelib == self.install_platlib:
            pythonpath = self.install_purelib
        else:
            pythonpath = os.pathsep.join([self.install_platlib,
                                          self.install_purelib])
        if self.root:
            installpath = os.path.normpath(installpath.replace(self.root, ''))
            pythonpath = os.path.normpath(pythonpath.replace(self.root, ''))
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
        self.data_files.append(fp)

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
        self.data_files.append(fp)

    def run(self):
        self.write_env_sh()
        self.write_env_csh()
        Install.run(self)
        if not self.root:
            print("\n--------------------------------------------------")
            print("DQSegDB has been installed.")
            print("If you are running csh, you can set your environment by "
                  "running:\n")
            print("source %s\n" % os.path.join(self.install_base, self.cshenv))
            print("Otherwise, you can run:\n")
            print("source %s" % os.path.join(self.install_base, self.shenv))
            print("--------------------------------------------------")
    run.__doc__ = Install.__doc__

cmdclass['install'] = DQSegDBInstall


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
      use_2to3=True
      )
