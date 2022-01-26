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
Data Access Object class file
'''

# Import.
import Constants
import logging
import MySQLdb

# Instantiate logger.
log = logging.getLogger(__name__)

class DAOHandle:
    
    ##################################
    # DB CONNECTION HANDLING METHODS #
    ##################################

    cnxn = None

    # Establish ODBC connection and set cursor.
    def connect_to_db(self):
        # Make connection available across module.
        global cnxn
        # Instantiate objects.
        constant = Constants.ConstantsHandle()
        # Attempt connection.
        try:
            # Attempt DB connection.
            cnxn = MySQLdb.connect(host=constant.db_host,
                                   user=constant.db_user,
                                   passwd=constant.db_pass,
                                   db=constant.db)
        except MySQLdb.OperationalError as err:
            conn = False
            # Log event.
            log.error('** Problem establishing database connection: ' + str(err))
        else:
            # If connection established.
            conn = True
        # Return.
        return conn
    
    # Close DB connection.
    def close_db_connection(self):
        # If connection exists.
        try:
            cnxn
        except:
            # Log event.
            log.warning('** Database connection has already already closed.')
        else:
            # Close
            try:
                cnxn.close()
            except:
                # Log event.
                log.error('** Problem closing database connection.')
            else:
                # Log event.
                log.info('** Closed database connection.')
    
    #############################
    # TEST-RUN-HANDLING METHODS #
    #############################
    
    # Write the test run to the database.
    def insert_test_run(self, h, t):
        # Log event.
        log.debug('Writing test run to DB at ' + str(t) + ' and using dataset ' + h + '...')
        # Init.
        run_id = 0
        try:
            # Set DB cursor
            cur = cnxn.cursor()
        except MySQLdb.OperationalError as err:
            # Log event.
            log.error('Unable to create cursor on database connection: ' + str(err))
        else:

            # Try to get the dataset host ID.
            try:
                dataset_id = self.get_value_id(4, h)
            except:
                # Log event.
                log.error('Unable to retrieve dataset host normalised ID for:' + h)
            else:
                # If dataset host does not exist.
                if dataset_id == 0:
                    # Insert the test name.
                    self.insert_value(4, h)
                    # Attempt to get the new ID for this dataset host.
                    dataset_id = self.get_value_id(4, h)
                # If test name still does not exist.
                if dataset_id == 0:
                    # Log event.
                    log.error('Unable to retrieve dataset host normalised ID for:' + h + '. The dataset host has not been successfully inserted into tbl_values.')
                else:
                    try:
                        # Insert.
                        cur.execute("""
                                    INSERT INTO tbl_test_runs
                                    (dataset_fk, test_run_start_time)
                                    VALUES
                                    (%s, %s)
                                    """, (str(dataset_id), str(t)))
                        # Commit to database.
                        cnxn.commit()
                    except MySQLdb.OperationalError as err:
                        # Rollback.
                        cnxn.rollback()
                        # Log event.
                        log.error('Unable to execute INSERT statement: ' + str(err))
                    else:
                        # Log event.
                        log.debug('Test run written to DB.')
                        # Get.
                        cur.execute("""
                                    SELECT test_run_id
                                    FROM tbl_test_runs
                                    WHERE dataset_fk=%s
                                    ORDER BY test_run_id DESC
                                    LIMIT 1
                                    """, str(dataset_id))
                        # Get number of rows.
                        numrows = int(cur.rowcount)
                        # Loop result.
                        for x in range(0, numrows):
                            row = cur.fetchone()
                            run_id = row[0]
        # Return.
        return run_id
        
    # Close test run in database.
    def close_test_run(self, run_id, t, f):
        # Log event.
        log.debug('Closing test run in DB...')
        try:
            # Set DB cursor
            cur = cnxn.cursor()
        except MySQLdb.OperationalError as err:
            # Log event.
            log.error('Unable to create cursor on database connection: ' + str(err))
        else:
            try:
                # Insert.
                cur.execute("""
                            UPDATE tbl_test_runs
                            SET test_run_stop_time=%s, test_run_failures=%s
                            WHERE test_run_id=%s
                            """, (str(t), str(f), str(run_id)))
                # Commit to database.
                cnxn.commit()
            except MySQLdb.OperationalError as err:
                # Rollback.
                cnxn.rollback()
                # Log event.
                log.error('Unable to execute INSERT statement: ' + str(err))
        # Log event.
        log.debug('Test run closed in DB.')

    #########################
    # TEST-HANDLING METHODS #
    #########################

    # Write the result of a test to the database. Args: Test Run ID, Test name, Test result, Test Details.
    def insert_test_result(self, run_id, n, l, m):
        # Log event.
        log.debug('Writing test result to DB...')
        try:
            # Set DB cursor
            cur = cnxn.cursor()
        except MySQLdb.OperationalError as err:
            # Log event.
            log.error('Unable to create cursor on database connection: ' + str(err))
        else:
            # Try to get the test ID.
            try:
                test_id = self.get_value_id(2, n)
            except:
                # Log event.
                log.error('Unable to retrieve test normalised ID for:' + n)
            else:
                # If test name does not exist.
                if test_id == 0:
                    # Insert the test name.
                    self.insert_value(2, n)
                    # Attempt to get the new ID for this test.
                    test_id = self.get_value_id(2, n)
                # If test name still does not exist.
                if test_id == 0:
                    # Log event.
                    log.error('Unable to retrieve test normalised ID for:' + n + '. The test name has not been successfully inserted into tbl_values.')
                else:
                    # Try to get the success-level ID.
                    try:
                        success_level_id = self.get_value_id(3, l)
                    except:
                        # Log event.
                        log.error('Unable to retrieve success-level normalised ID for:' + n)
                    else:
                        # Log event.
                        log.debug('Test ID: ' + str(test_id) + '; Success-level ID: ' + str(success_level_id))
                        try:
                            # Insert.
                            cur.execute("""
                                        INSERT INTO tbl_test_results
                                        (test_run_fk, test_name_fk, test_success_level_fk, test_details)
                                        VALUES
                                        (%s, %s, %s, %s)
                                        """, (str(run_id), str(test_id), str(success_level_id), m))
                            # Commit to database.
                            cnxn.commit()
                        except MySQLdb.OperationalError as err:
                            # Rollback.
                            cnxn.rollback()
                            # Log event.
                            log.error('Unable to execute INSERT statement: ' + str(err))
        # Log event.
        log.debug('Test result written to DB.')
        
    ##########################
    # VALUE-HANDLING METHODS #
    ##########################
    
    # Get a value normalised ID using its group and string value.
    def get_value_id(self, g, v):
        # Init.
        r = 0
        err_msg = 'retrieving value ID'
        try:
            # Set DB cursor.
            cur = cnxn.cursor()
        except MySQLdb.OperationalError as err:
            # Log event.
            log.error('**** Problem ' + err_msg + '. Unable to create cursor on database connection: ' + str(err))
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT value_id
                            FROM tbl_values
                            WHERE value_group_fk=%s AND value_txt LIKE %s
                            LIMIT 1
                            """, (g, str(v)))
                # Get number of rows.
                numrows = int(cur.rowcount)
                # Loop result.
                for x in range(0, numrows):
                    row = cur.fetchone()
                    r = row[0]
            except MySQLdb.OperationalError as err:
                # Log event.
                log.error('**** Problem ' + err_msg + '. Unable to execute SQL statement: ' + str(err))
        # Return.
        return r
    
    # Insert a test name.
    def insert_value(self, g, v):
        # Init.
        r = True
        err_msg = 'inserting value (' + v + ') in group (' + str(g) + ') to database'
        try:
            # Set DB cursor
            cur = cnxn.cursor()
        except MySQLdb.OperationalError as err:
            # Log event.
            log.error('**** Problem ' + err_msg + '. Unable to create cursor on database connection: ' + str(err))
        else:
            try:
                # Insert.
                cur.execute("""
                            INSERT INTO tbl_values
                            (value_group_fk, value_txt)
                            VALUES
                            (%s, %s)
                            """, (str(g), v))
                # Commit to database.
                cnxn.commit()
            except MySQLdb.OperationalError as err:
                # Rollback.
                cnxn.rollback()
                # Log event.
                log.error('**** Problem ' + err_msg + '. Unable to execute INSERT statement: ' + str(err))
                # Set result.
                r = False
        # Return
        return r