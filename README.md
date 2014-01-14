dqsegdb
=======

DQSEGDB client library and functions

Currently must be used from CIT (ex: ldas-pcdev1.ligo.caltech.edu) or sugar (ex: sugar.phy.syr.edu) head nodes.

To use the new client tools, run the following commands:

```

# Clone the repository
git clone 

# cd into the repo
cd dqsegdb

# "Build" the package, placing binaries and libraries into standard directories
python setup.py install --user

# Setup your environment to look at the new directories
# Follow instructions provided at end of previous command
# Example:
#  source /home/rfisher/.local/etc/dqsegdb-user-env.sh
# This must be run each time you log in, or put it in your log in scripts (.bashrc)

```
