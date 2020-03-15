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
Constants class file
'''

class ConstantsHandle():
    
    ##########################
    # Application constants #
    ########################
    
    app_version = '1.2'

    ############################
    # DB connection constants #
    ##########################

    # If DSN is set to None, use these constants to connect via direct string, add required variables below. Each should be set to None if not being used.
    db_host = 'localhost'       # Host on which database is found.
    db = 'dqsegdb_regression_tests'     # Database name.
    db_user = 'dqsegdb_rts'     # Database connection user.
    db_pass = 'dqsegdb_rts_pw'  # Database connection user password.

    ###########################
    # DQSEGDB-host constants #
    #########################
    
    #dqsegdb_host = 'http://10.20.5.46'  #GEO (dqsegdb7)
    #dqsegdb_host = 'http://10.20.5.42'  #BACK-UP (dqsegdb3)
    dqsegdb_host = 'http://10.14.0.105'  # segments-backup.ligo.org

    ######################
    # Logging constants #
    ####################
    
    log_file_location = '/opt/dqsegdb/logs/regression_test_suite/'  # Log-file write directory.

    ###################
    # Time constants #
    #################
    
    gps_leap_secs = 17
