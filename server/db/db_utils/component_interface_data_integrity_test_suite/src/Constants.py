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
