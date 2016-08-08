#!/bin/bash
#
# Travis CI test runner: test --help for all command-line executables
# Author: Duncan Macleod <duncan.macleod@ligo.org> (2016)

# loop over all bin/ scripts
for EXE in bin/*_dqsegdb; do
    # get file-name as PATH executable
    EXENAME=`basename ${EXE}`
    EXEPATH=`which ${EXENAME}`
    # execute --help with coverage
    echo "Testing $EXENAME --help..."
    coverage run --append --source=dqsegdb ${EXEPATH} --help 1>/dev/null;
done
