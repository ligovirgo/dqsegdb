# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.

# This program is free software: you can redistribute it and/or modify

# it under the terms of the GNU Affero General Public License as

# published by the Free Software Foundation, either version 3 of the

# License, or (at your option) any later version.

#

# This program is distributed in the hope that it will be useful,

# but WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

# GNU Affero General Public License for more details.

#

# You should have received a copy of the GNU Affero General Public License

# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#!/usr/bin/env python
'''
DQSEGDB Regression Test Suite
Main file.
'''
# Import.
from __future__ import print_function
import Tests
import Constants
import logging
import time

# Instantiate objects.
constant = Constants.ConstantsHandle()
# Set logger configuration.
logging.basicConfig(filename=constant.log_file_location + time.strftime("%Y-%m-%d",
                    time.localtime()) + '.log', format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.DEBUG)
# Instantiate logger.
log = logging.getLogger(__name__)

# Instantiate objects.
test = Tests.TestHandle()

# Log event.
log.info('Starting DQSEGDB Regression Test Suite (' + constant.app_version + ')...')

# Init.
loop = True

try:
    # Loop.
    while loop:
        # Begin attempt.
        try:
            test.run_test_suite()
        # If user stops server.
        except KeyboardInterrupt:
            # Log event.
            log.warning('DQSEGDB Regression Test Suite stopped manually using KeyboardInterrupt.')
            # Raise exception.
            raise
        else:
            # Log event.
            log.info('DQSEGDB Regression Test Suite (' + constant.app_version + ') finished.')
            # Set to stop loop.
            loop = False
# Catch keyboard interrupt.
except (KeyboardInterrupt, SystemExit):
    # Print warning messages.
    print('\nKeyboardInterrupt caught')
    print('DQSEGDB Regression Test Suite stopped manually')
    # Log event.
    log.info('Stopped DQSEGDB Regression Test Suite.')
    # Raise exception.
    raise
