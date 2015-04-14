'''
DQSEGDB Python Server
Constants class file
'''

class ConstantsHandle():
    
    ##########################
    # API version constants #
    ########################
    
    api_version = 1

    #############################
    # Server version constants #
    ###########################
    
    py_server_version = 'v2r1'

    ##############################
    # ODBC connection constants #
    ############################

    # If connecting via DSN, add DSN string ('DSN=[DSN_NAME];UID=[USER];PWD=[PASSWORD]'). Otherwise, set to None.
    odbc_dsn = 'DSN=DQSEGDB'
    
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
    
    use_https = False # False = Use HTTP; True = Use HTTPS.
    grid_map_get_file = '/etc/grid-security/grid-mapfile'  # Grid Map file used in authentication.
    grid_map_put_patch_file = '/etc/grid-security/grid-mapfile-insert'  # Grid Map file used in authorisation.

    ###################
    # Time constants #
    #################
    
    gps_leap_secs = 16
