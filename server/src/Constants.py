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
DQSEGDB Python Server
Constants class file
'''

class ConstantsHandle():
    
    ##########################
    # API version constants #
    ########################
    
    api_version = '2.1.17'

    ##############################
    # ODBC connection constants #
    ############################

    # If connecting via DSN, add DSN string ('DSN=[DSN_NAME];UID=[USER];PWD=[PASSWORD]'). Otherwise, set to None.
    odbc_dsn = 'DSN=DQSEGDB'    # /etc/odbc.ini
    
    # If DSN is set to None, use these constants to connect via direct string, add required variables below. Each should be set to None if not being used.
    odbc_driver = None  # ODBC Driver to be used to make connection.
    odbc_host = None    # Host on which database is found.
    odbc_db = None      # Database name.
    odbc_user = None    # Database connection user.
    odbc_pass = None    # Database connection user password.
    odbc_socket = None  # Socket used when connecting to database.
    
    ######################
    # Request constants #
    ####################
    
    segment_requests = ["active", "known"]  # Types of requests available in segment retrieval.
    metadata_requests = ["metadata", "insert_history"]  # Types of requests available in metadata retrieval.
    
    ######################
    # Logging constants #
    ####################
    
    log_file_location = '/opt/dqsegdb/python_server/logs/'  # Log-file write directory.

    #############################
    # HTTP(S) & GRID constants #
    ###########################
    
    use_https = True # False = Use HTTP; True = Use HTTPS.
    grid_map_get_file = '/etc/grid-security/grid-mapfile'  # Grid Map file used in authentication.
    grid_map_put_patch_file = '/etc/grid-security/grid-mapfile-insert'  # Grid Map file used in authorisation.

    ########################
    # SciTokens constants #
    ######################
    scitokens_issuer = 'https://test.cilogon.org'
    scitokens_audience = 'segments.ligo.org'

    #################################
    # Sub-second segment constants #
    ###############################
    
    use_sub_second_segments = True
    
    segment_requests = ["active", "known"]  # Types of requests available in segment retrieval.

    ###################
    # Time constants #
    #################
    
    gps_leap_secs = 17
