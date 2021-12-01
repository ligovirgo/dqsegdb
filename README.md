dqsegdb
=======

[![Build and test](https://github.com/ligovirgo/dqsegdb/actions/workflows/test.yml/badge.svg)](https://github.com/ligovirgo/dqsegdb/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/ligovirgo/dqsegdb/branch/master/graph/badge.svg?token=4q02Rv0Gkw)](https://codecov.io/gh/ligovirgo/dqsegdb)


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
