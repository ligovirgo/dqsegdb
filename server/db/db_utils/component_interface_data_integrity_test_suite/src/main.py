#!/usr/bin/env python
'''
DQSEGDB Regression Test Suite
Main file.
'''
# Import.
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
    print '\nKeyboardInterrupt caught'
    print 'DQSEGDB Regression Test Suite stopped manually'
    # Log event.
    log.info('Stopped DQSEGDB Regression Test Suite.')
    # Raise exception.
    raise