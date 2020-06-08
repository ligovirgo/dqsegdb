class Constants():
    '''
    DQSEGDB-Web Project constants class file
    '''
    #############################
    # Package version constants #
    #############################
    app_name = 'DQSEGDB-Web Project'
    app_version = '1.0'

    ###########################
    # DB connection constants #
    ###########################
    db_host = 'localhost'
    db = 'dqsegdb_wui'
    db_user = 'root'
    db_pass = ''

    #####################
    # Logging constants #
    #####################
    log_file_location = ''  # Log-file write directory.
    log_print_to_stdout = True
    sfdb_verbosity_levels = [0, 1, 2, 3]
    sfdb_verbosity_level_default = 1
