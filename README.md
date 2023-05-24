dqsegdb
=======

[![Build and test](https://github.com/ligovirgo/dqsegdb/actions/workflows/test.yml/badge.svg)](https://github.com/ligovirgo/dqsegdb/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/ligovirgo/dqsegdb/branch/master/graph/badge.svg?token=4q02Rv0Gkw)](https://codecov.io/gh/ligovirgo/dqsegdb)

NOTICE: This repo has moved, as of Sept. 2022.  The code in this GitHub repo ( https://github.com/ligovirgo/dqsegdb ) is not being updated any more.  The new DQSegDB repo is https://git.ligo.org/computing/dqsegdb, with the code split up as follows:
- server code: https://git.ligo.org/computing/dqsegdb/server
- client tools: https://git.ligo.org/computing/dqsegdb/client
- web server code: https://git.ligo.org/computing/dqsegdb/web

The current code in this (GitHub) repo will not likely be installable without manual modification, to prevent users from accidentally installing an old version of the code.

All information below this line is preserved from before the repo moved, and some of it is already obsolete.
=======

DQSEGDB client library and functions

Please see documentation at: 

http://ligovirgo.github.io/dqsegdb/

The DQSEGDB package should be installed and available for use on all LIGO Tier 1 and 2 clusters.  

Within this project, the bdist directory includes complete (including dependencies) distributable Python executables, built with PyInstaller.

To use the new client tools as a user, run the following commands:

```
# Clone the repository:
git clone https://github.com/ligovirgo/dqsegdb.git

# cd into the repo
cd dqsegdb

# "Build" the package, placing binaries and libraries into standard directories
python setup.py install --user

# Set up your environment to look at the new directories
# Follow instructions provided at end of previous command
# Example:
#  source /home/rfisher/.local/etc/dqsegdb-user-env.sh
# This must be run each time you log in, or put it in your login scripts (.bashrc)

```
dqsegdb architecture as used by IGWN
=======
<div align="center">
  <img src="https://raw.githubusercontent.com/ligovirgo/dqsegdb/master/system_architecture_20200212.png">
</div>
