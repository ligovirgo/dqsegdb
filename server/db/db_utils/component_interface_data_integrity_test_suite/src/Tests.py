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
'''
DQSEGDB Regression Test Suite
Test-handling class file
'''
# Import.
from __future__ import print_function
import Constants
import DAO
import logging
import time
import Utils

# Instantiate logger.
log = logging.getLogger(__name__)

class TestHandle:
    
    # Run regression test suite.
    def run_test_suite(self):
        # Init.
        failures = 0
        # Instantiate.
        constant = Constants.ConstantsHandle()
        dao = DAO.DAOHandle()
        # If connection established.
        if dao.connect_to_db():
            # Set time.
            t_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # Insert test run to database.
            run_id = dao.insert_test_run(constant.dqsegdb_host, t_start)
            # If no run ID returned.
            if run_id == 0:
                # Log event.
                log.error('Unable to write test run to DB.')
            else:
                # Check simple connection.
                failures += self.check_simple_connection(run_id)
                # Check flag versions.
                failures += self.check_flag_versions(run_id)
                # Check active flag-version coverage.
                failures += self.check_flag_version_coverage(run_id, 'active')
                # Check known flag-version coverage.
                failures += self.check_flag_version_coverage(run_id, 'known')
                # Check flag version active segment boundaries.    
                failures += self.check_flag_version_boundaries(run_id, 'active')
                # Check flag version known segment boundaries.    
                failures += self.check_flag_version_boundaries(run_id, 'known')
                # Set time.
                t_stop = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # Close test run in database.
                dao.close_test_run(run_id, t_stop, failures)
            # Close database connection.
            dao.close_db_connection()
        # Otherwise, problem with database connection. stop everything.
        else:
            # Log event.
            log.critical('No database connection available.')
    
    # Check a simple connection.    
    def check_simple_connection(self, run_id):
        # Init.
        l = 'Failure'
        n = 'simple connection check'
        m = ''
        r = 1
        # Log event.
        log.info('Starting ' + n)
        # Instantiate.
        constant = Constants.ConstantsHandle()
        dao = DAO.DAOHandle()
        util = Utils.UtilHandle()
        # Set call URI.
        uri = constant.dqsegdb_host + '/dq'
        # Attempt to open url and convert JSON payload to dictionary..
        try:
            reply = util.convert_uri_json_response_to_dict(n, uri)
        except:
            # Log event.
            m = 'Unable to convert payload returned by ' + n + ': ' + uri + ' to dictionary'
            log.error(m)
        else:
            # If payload reply is not good.
            if not reply['r'] == True:
                # Log event.
                m = 'Problem in payload conversion ' + n + ': ' + uri + ' to dictionary'
                log.error(m)
            else:
                m = reply['m']
                d = reply['d']
                # If the Ifos key is not available in the dictionary.
                if not 'Ifos' in d:
                    # Log event.
                    m = 'Ifos key not available in payload returned by ' + n + ': ' + uri + ' to dictionary'
                    log.error(m)
                # Otherwise, if key exists.
                else:
                    # Log event.
                    m = n + ' completed successfully. Resource returned ' + str(d['Ifos'])
                    log.info(m)
                    # Set.
                    l = 'Success'
                    r = 0
        # Write result to database.
        dao.insert_test_result(run_id, n, l, m)
        # Return.
        return r
    
    # Check flag versions.    
    def check_flag_versions(self, run_id):
        # Init.
        l = 'Failure'
        n = 'flag version check'
        m = ''
        r = 1
        # Log event.
        log.info('Starting ' + n)
        # Instantiate.
        constant = Constants.ConstantsHandle()
        dao = DAO.DAOHandle()
        util = Utils.UtilHandle()
        # Set call URI.
        uri = constant.dqsegdb_host + '/report/flags'
        # Attempt to open url and convert JSON payload to dictionary..
        try:
            reply = util.convert_uri_json_response_to_dict(n, uri)
        except:
            # Log event.
            m = 'Unable to convert payload returned by ' + n + ': ' + uri + ' to dictionary'
            log.error(m)
        else:
            # If payload reply is not good.
            if not reply['r'] == True:
                # Log event.
                m = 'Problem in payload conversion ' + n + ': ' + uri + ' to dictionary'
                log.error(m)
            else:
                m = reply['m']
                d = reply['d']
                # If the Ifos key is not available in the dictionary.
                if not 'results' in d:
                    # Log event.
                    m = 'results key not available in payload returned by ' + n + ': ' + uri + ' to dictionary'
                    log.error(m)
                # Otherwise, if key exists.
                else:
                    # Set error list.
                    l_error = []
                    # Loop through and get flags and versions.
                    for f_v in d['results']:
                        # Set flag-version URI.
                        f_v_uri = constant.dqsegdb_host + f_v + '?include=metadata'
                        # Check resource returns response.
                        try:
                            reply = util.convert_uri_json_response_to_dict(n, f_v_uri)
                        except:
                            # Log event.
                            m = 'Unable to convert payload returned by ' + n + ': ' + f_v_uri + ' to dictionary'
                            log.error(m)
                        else:
                            # If payload reply is not good.
                            if not reply['r'] == True:
                                # Set reply message
                                l_error.append(f_v_uri)
                    # If reply error messages have been set.
                    if l_error:
                        m = n + ' produced failures. Incorrect responses for following URI: ' + str(l_error)
                        log.error(m)
                    # Otherwise, error messages returned.
                    else:
                        # Log event.
                        m = n + ' completed successfully. Resource returned ' + str(d['results'])
                        log.info(m)
                        # Set.
                        l = 'Success'
                        r = 0
        # Write result to database.
        dao.insert_test_result(run_id, n, l, m)
        # Return.
        return r
    
    # Check flag version active/known segment coverage.    
    def check_flag_version_coverage(self, run_id, ak):
        # Init.
        l = 'Failure'
        n = ak  + ' flag version coverage check'
        m = ''
        r = 1
        # Log event.
        log.info('Starting ' + n)
        # Instantiate.
        constant = Constants.ConstantsHandle()
        dao = DAO.DAOHandle()
        util = Utils.UtilHandle()
        # Set call URI.
        uri = constant.dqsegdb_host + '/report/coverage'
        # Attempt to open url and convert JSON payload to dictionary..
        try:
            reply = util.convert_uri_json_response_to_dict(n, uri)
        except:
            # Log event.
            m = 'Unable to convert payload returned by ' + n + ' ' + uri + ' to dictionary'
            log.error(m)
        else:
            # If payload reply is not good.
            if not reply['r'] == True:
                # Log event.
                m = 'Problem in payload conversion ' + n + ' ' + uri + ' to dictionary'
                log.error(m)
            else:
                m = reply['m']
                d = reply['d']
                # If the Ifos key is not available in the dictionary.
                if not 'results' in d:
                    # Log event.
                    m = 'results key not available in payload returned by ' + n + ' ' + uri + ' to dictionary'
                    log.error(m)
                # Otherwise, if key exists.
                else:
                    # Set error list.
                    l_error = []
                    # Loop through and get flags, versions and totals.
                    for f_v, totals in list(d['results'].items()):
                        # Set flag-version URI.
                        f_v_uri = constant.dqsegdb_host + f_v + '?include=' + ak
                        # Check resource returns response.
                        try:
                            reply_b = util.convert_uri_json_response_to_dict(n, f_v_uri)
                        except:
                            # Log event.
                            m = 'Unable to convert payload returned by ' + n + ' ' + f_v_uri + ' to dictionary'
                            log.error(m)
                        else:
                            # If payload reply is not good.
                            if not reply_b['r'] == True:
                                # Append to error list.
                                l_error.append(f_v_uri + ' - problem with returned payload')
                            else:
                                # Count active/known segments in payload.
                                tot = len(reply_b['d'][ak])
                                # If counted active/known total different to coverage totals.
                                if not tot == totals['total_' + ak + '_segments']:
                                    # Append to error list.
                                    l_error.append(f_v_uri + ' - ' + ak + ' totals are incongruent - DB: ' + str(totals['total_' + ak + '_segments']) + '; JSON: ' + str(tot))
                                print(f_v + ' - ' + ak + '; DB: ' + str(totals['total_' + ak + '_segments']) + '; JSON: ' + str(tot))
                    # If reply error messages have been set.
                    if l_error:
                        m = n + ' produced failures. Incorrect responses for following URI: ' + str(l_error)
                        log.error(m)
                    # Otherwise, error messages returned.
                    else:
                        # Log event.
                        m = n + ' completed successfully.'
                        log.info(m)
                        # Set.
                        l = 'Success'
                        r = 0
        # Write result to database.
        dao.insert_test_result(run_id, n, l, m)
        # Return.
        return r
    
    # Check flag version active/known segment boundaries.    
    def check_flag_version_boundaries(self, run_id, ak):
        # Init.
        l = 'Failure'
        n = ak  + ' flag version boundary check'
        m = ''
        r = 1
        defaut_earliest_boundary = 999999999999999
        # Log event.
        log.info('Starting ' + n)
        # Instantiate.
        constant = Constants.ConstantsHandle()
        dao = DAO.DAOHandle()
        util = Utils.UtilHandle()
        # Set call URI.
        uri = constant.dqsegdb_host + '/report/coverage'
        # Attempt to open url and convert JSON payload to dictionary..
        try:
            reply = util.convert_uri_json_response_to_dict(n, uri)
        except:
            # Log event.
            m = 'Unable to convert payload returned by ' + n + ' ' + uri + ' to dictionary'
            log.error(m)
        else:
            # If payload reply is not good.
            if not reply['r'] == True:
                # Log event.
                m = 'Problem in payload conversion ' + n + ' ' + uri + ' to dictionary'
                log.error(m)
            else:
                m = reply['m']
                d = reply['d']
                # If the Ifos key is not available in the dictionary.
                if not 'results' in d:
                    # Log event.
                    m = 'results key not available in payload returned by ' + n + ' ' + uri + ' to dictionary'
                    log.error(m)
                # Otherwise, if key exists.
                else:
                    # Set error list.
                    l_error = []
                    # Loop through and get flags, versions and totals.
                    for f_v, totals in list(d['results'].items()):
                        # Set flag-version URI.
                        f_v_uri = constant.dqsegdb_host + f_v + '?include=' + ak
                        # Check resource returns response.
                        try:
                            reply_b = util.convert_uri_json_response_to_dict(n, f_v_uri)
                        except:
                            # Log event.
                            m = 'Unable to convert payload returned by ' + n + ' ' + f_v_uri + ' to dictionary'
                            log.error(m)
                        else:
                            # If payload reply is not good.
                            if not reply_b['r'] == True:
                                # Append to error list.
                                l_error.append(f_v_uri + ' - problem with returned payload')
                            else:
                                # Set first start/stop boundaries
                                earliest_boundary = defaut_earliest_boundary
                                latest_boundary = 0
                                # Loop through segments in list.
                                for start, stop in reply_b['d'][ak]:
                                    # If start lower than earliest boundary set so far.
                                    if start < earliest_boundary:
                                        # Reset earliest boundary.
                                        earliest_boundary = start
                                    # If stop higher than latest boundary set so far.
                                    if stop < latest_boundary:
                                        # Reset earliest boundary.
                                        latest_boundary = stop
                                # If the earliest boundary hasn't changed from when first set.
                                if earliest_boundary == defaut_earliest_boundary:
                                    # Set the earliest boundary to zero.
                                    earliest_boundary = 0
                                # If earliest boundary different to coverage totals.
                                if not earliest_boundary == totals['earliest_' + ak + '_segment']:
                                    # Append to error list.
                                    l_error.append(f_v_uri + ' - ' + ak + ' boundaries are incongruent - DB: ' + str(totals['earliest_' + ak + '_segment']) + '; JSON: ' + str(earliest_boundary))
                                print(f_v + ' - ' + ak + '; DB: ' + str(totals['earliest_' + ak + '_segment']) + '; JSON: ' + str(earliest_boundary))
                    # If reply error messages have been set.
                    if l_error:
                        m = n + ' produced failures. Incorrect responses for following URI: ' + str(l_error)
                        log.error(m)
                    # Otherwise, error messages returned.
                    else:
                        # Log event.
                        m = n + ' completed successfully.'
                        log.info(m)
                        # Set.
                        l = 'Success'
                        r = 0
        # Write result to database.
        dao.insert_test_result(run_id, n, l, m)
        # Return.
        return r
