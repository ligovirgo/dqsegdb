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
LICENSE = None
#rel_version="0.9"
rel_version="1.0"
release=True


# ------------------------------------------------------------------------------
# VCS info

version_py = os.path.join(PACKAGENAME, 'version.py')


def write_vcs_info(target):
    """Generate target file with versioning information from git VCS
    """
    log.info("generating %s" % target)
    import vcs
    gitstatus = vcs.GitStatus()
    gitstatus.run(target, PACKAGENAME, AUTHOR, AUTHOR_EMAIL)


# ------------------------------------------------------------------------------
# custom commands

class DQSegDBBuildPy(build_py.build_py):
    def run(self):
        try:
            write_vcs_info(version_py)
        except subprocess.CalledProcessError:
            # failed to generate version.py because git call did'nt work
            if os.path.exists(version_py):
                log.info("cannot determine git status, using existing %s"
                         % version_py)
        build_py.build_py.run(self)


class DQSegDBSDist(sdist.sdist):
    def run(self):
        write_vcs_info(version_py)
        sdist.sdist.run(self)


class DQSegDBInstall(install.install):
    """Extension of setuptools install to write source script for
    users.
    """
    shenv = os.path.join('etc', '%s-user-env.sh' % PACKAGENAME)
    cshenv = os.path.join('etc', '%s-user-env.csh' % PACKAGENAME)

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
        if not self.root:
            print("\n--------------------------------------------------")
            print("DQSegDB has been installed.")
            print("If you are running csh, you can set your environment by "
                  "running:\n")
            print("source %s\n" % os.path.join(self.install_base, self.cshenv))
            print("Otherwise, you can run:\n")
            print("source %s" % os.path.join(self.install_base, self.shenv))
            print("--------------------------------------------------")
    run.__doc__ = install.install.__doc__


# ------------------------------------------------------------------------------
# run setup

# get version metadata
try:
    from dqsegdb import version
except ImportError:
    VERSION = None
    RELEASE = False
else:
    VERSION = version.version
    RELEASE = version.version != version.git_id and 'dev' not in VERSION

# Use the find_packages tool to locate all packages and modules
packagenames = find_packages()

# glob for all scripts
if os.path.isdir('bin'):
    scripts = glob.glob(os.path.join('bin', '*'))
else:
    scripts = []

if release:
    VERSION=rel_version


# old: packages=packagenames,

setup(name=PACKAGENAME,
      cmdclass={
          'install': DQSegDBInstall,
          'build_py': DQSegDBBuildPy,
          'sdist': DQSegDBSDist,
          },
      version=VERSION,
      description=DESCRIPTION,
      packages=['dqsegdb'],
      ext_modules=[],
      scripts=scripts,
      data_files=[('etc', [DQSegDBInstall.shenv, DQSegDBInstall.cshenv])],
      install_requires=['glue'],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,
      use_2to3=True
      )
