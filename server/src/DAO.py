'''
DQSEGDB Python Server
Data Access Object class file
'''

# Import.
import Admin
import Constants
import gpstime
import pyodbc
import time
import User

class DAOHandle:
    
    ##################################
    # DB CONNECTION HANDLING METHODS #
    ##################################

    cnxn = None

    # Establish ODBC connection and set cursor.
    def connect_to_db(self, req_method, full_uri):
        global cnxn
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # Determine ODBC connection string.
        connection_str = ''
        # If using DSN.
        if constant.odbc_dsn != None:
            connection_str = constant.odbc_dsn
        # Otherwise, build string using supplied values.
        elif constant.odbc_driver != None:
            connection_str = 'DRIVER=%s;SERVER=%s;SOCKET=%s;DATABASE=%s;UID=%s;PWD=%s' % constant.odbc_driver, constant.odbc_host, constant.odbc_socket, constant.odbc_db, constant.odbc_user, constant.odbc_pass
        # Attempt connection.
        try:
            # Set HTTP code and log.
            cnxn = pyodbc.connect(connection_str) # .odbc.ini in /home/gary/    FILE DATA SOURCES..: /usr/local/etc/ODBCDataSources    USER DATA SOURCES..: /root/.odbc.ini
        except:
            conn = False
            # Set HTTP code and log.
            admin.log_and_set_http_code(500, 3, req_method, None, full_uri)
        else:
            # If connection established.
            conn = True
        # Return.
        return conn
    
    #########################
    # DB-STATISTICS METHODS #
    #########################

    # Get earliest/latest segment boundaries.
    def get_segment_boundaries(self, ak, w, ifo):
        # Init.
        res = 0
        # If args passed.
        try:
            ak, w, ifo
        except:
            pass
        else:
            # Set ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set MIN/MAX.
                m = 'MIN'
                el = 'earliest'
                if w:
                    m = 'MAX'
                    el = 'latest'
                # Set IFO.
                j = ''
                iw = ''
                if not ifo == None:
                    j = ' LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id '
                    iw = ' WHERE dq_flag_ifo=' + str(ifo)
                # Get.
                cur.execute("""
                            SELECT """ + m + """(dq_flag_version_""" + ak + """_""" + el + """_segment_time) AS 'tot'
                            FROM tbl_dq_flag_versions """ + j + iw)
                # Loop.
                for row in cur:
                    # If tot exists.
                    if not row.tot == None:
                        # Set.
                        res = int(row.tot)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res
    
    # Get segment totals.
    def get_segment_totals(self, ak, ifo):
        # Init.
        res = 0
        # If args passed.
        try:
            ak, ifo
        except:
            pass
        else:
            # Set ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set IFO.
                j = ''
                iw = ''
                if not ifo == None:
                    j = ' LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id '
                    iw = ' WHERE dq_flag_ifo=' + str(ifo)
                # Get.
                cur.execute("""
                            SELECT SUM(dq_flag_version_""" + ak + """_segment_total) AS 'tot'
                            FROM tbl_dq_flag_versions """ + j  + iw)
                # Loop.
                for row in cur:
                    # If tot exists.
                    if not row.tot == None:
                        # Set.
                        res = int(row.tot)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res
    
    # Get last segment insert time.
    def get_last_segment_insert_time(self, ifo):
        # Init.
        res = 0
        # If args passed.
        try:
            ifo
        except:
            pass
        else:
            # Set ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set IFO.
                j = ''
                iw = ''
                if not ifo == None:
                    j = """
                        LEFT JOIN tbl_dq_flag_versions ON tbl_processes.dq_flag_version_fk = tbl_dq_flag_versions.dq_flag_version_id
                        LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id
                        """
                    iw = ' WHERE dq_flag_ifo=' + str(ifo)
                # Get.
                cur.execute("""
                            SELECT MAX(process_time_last_used) AS 'tot'
                            FROM tbl_processes """ + j  + iw)
                # Loop.
                for row in cur:
                    # If tot exists.
                    if not row.tot == None:
                        # Set.
                        res = int(row.tot)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res

    # Get flag totals.
    def get_flag_totals(self, ifo):
        # Init.
        res = 0
        # If arg passed.
        try:
            ifo
        except:
            pass
        else:
            # Set ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set IFO.
                iw = ''
                if not ifo == None:
                    iw = ' WHERE dq_flag_ifo=' + str(ifo)
                # Get.
                cur.execute("""
                            SELECT COUNT(dq_flag_id) AS 'tot'
                            FROM tbl_dq_flags """ + iw)
                # Loop.
                for row in cur:
                    # If tot exists.
                    if not row.tot == None:
                        # Set.
                        res = int(row.tot)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res

    # Get flag version totals.
    def get_flag_version_totals(self, ifo):
        # Init.
        res = 0
        # If arg passed.
        try:
            ifo
        except:
            pass
        else:
            # Set ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set IFO.
                j = ''
                iw = ''
                if not ifo == None:
                    j = ' LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id '
                    iw = ' WHERE dq_flag_ifo=' + str(ifo)
                # Get.
                cur.execute("""
                            SELECT COUNT(dq_flag_version_id) AS 'tot'
                            FROM tbl_dq_flag_versions """ + j  + iw)
                # Loop.
                for row in cur:
                    # If tot exists.
                    if not row.tot == None:
                        # Set.
                        res = int(row.tot)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res

    #########################
    # FLAG HANDLING METHODS #
    #########################

    # Insert flag.
    def insert_flag(self, req_method, full_uri, ifo_id, ifo, flag, data):
        # Init.
        e = []
        flag_id = None
        # If args passed.
        try:
            req_method, full_uri, ifo_id, flag, data
        except:
            pass
        else:
            # Instantiate objects.
            admin = Admin.AdminHandle()
            constant = Constants.ConstantsHandle()
            user = User.UserHandle()
            # If flag does not yet exist.
            if not self.get_flag_id(ifo_id, flag) == None:
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(400, 6, req_method, None, full_uri)
            else:
                # Get user id.
                uid = user.get_user_id(data['insert_history'][0]['insertion_metadata']['auth_user'])
                # If user ID does not exist.
                if uid == 0:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(404, 2, req_method, None, full_uri)
                else:
                    try:
                        # Set ODBC cursor.
                        cur = cnxn.cursor()
                    except:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(404, 4, req_method, None, full_uri)
                    else:
                        # If badness available in JSON.
                        badness = admin.convert_boolean_to_int(data['metadata']['active_indicates_ifo_badness'])
                        gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
                        # Insert flag.
                        cur.execute("""
                                    INSERT INTO tbl_dq_flags
                                    (dq_flag_name, dq_flag_ifo, dq_flag_assoc_versions, dq_flag_active_means_ifo_badness, dq_flag_creator, dq_flag_date_created)
                                    VALUES
                                    (?,?,?,'',?,?,?)
                                    """, flag, ifo_id, badness, uid, gps)
                        cnxn.commit()
                        # Get new flag ID.
                        cur.execute("""
                                    SELECT dq_flag_id
                                    FROM tbl_dq_flags
                                    WHERE dq_flag_ifo = ? AND dq_flag_name = ?
                                    ORDER BY dq_flag_id DESC
                                    LIMIT 1
                                    """, ifo_id, flag)
                        for row in cur:
                            # Set.
                            flag_id = row.dq_flag_id
                        # If no version ID found.
                        if not flag_id:
                            # Set HTTP code and log.
                            e = admin.log_and_set_http_code(400, 30, req_method, None, full_uri)
                        # Close ODBC cursor.
                        cur.close()
                        del cur
        # Return.
        return e
            
    # Insert flag version.
    def insert_flag_version(self, req_method, full_uri, ifo_id, ifo, flag_id, flag, version, data):
        # Init.
        e = []
        vid = None
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        user = User.UserHandle()
        # If args passed.
        try:
            req_method, full_uri, ifo_id, ifo, flag_id, flag, version, data
        except:
            pass
        else:
            # If the flag version already exists.
            if self.get_flag_version_id(flag_id, version):
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(400, 7, req_method, None, full_uri)
            else:
                # Get user id.
                uid = user.get_user_id(data['insert_history'][0]['insertion_metadata']['auth_user'])
                # If user ID does not exist.
                if uid == 0:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(404, 2, req_method, None, full_uri)
                else:
                    try:
                        # Set ODBC cursor.
                        cur = cnxn.cursor()
                    except:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(404, 4, req_method, None, full_uri)
                    else:
                        # Set required value formats.
                        deactivated = admin.convert_boolean_to_int(data['metadata']['deactivated'])
                        gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
                        comment = str(data['metadata']['flag_description'])
                        # Insert version.
                        cur.execute("""
                                    INSERT INTO tbl_dq_flag_versions
                                    (dq_flag_fk, dq_flag_description, dq_flag_version, dq_flag_version_deactivated, dq_flag_version_last_modifier, dq_flag_version_comment, dq_flag_version_uri, dq_flag_version_date_created, dq_flag_version_date_last_modified)
                                    VALUES
                                    (?,?,?,?,?,?,?,?,?)
                                    """, flag_id, comment, version, deactivated, uid, str(data['metadata']['flag_version_comment']), str(data['metadata']['further_info_url']), gps, gps)
                        #cnxn.commit()
                        # Get version ID.
                        vid = self.get_flag_version_id(flag_id, version)
                        # If no version ID found.
                        if not vid:
                            # Set HTTP code and log.
                            e = admin.log_and_set_http_code(400, 29, req_method, None, full_uri)
                        # Otherwise.
                        else:
                            # Append version to list of associated versions in flag table.
                            cur.execute("""
                                        UPDATE tbl_dq_flags
                                        SET dq_flag_assoc_versions = IF(dq_flag_assoc_versions='',?,CONCAT(dq_flag_assoc_versions,',',?))
                                        WHERE dq_flag_id = ?
                                        """, version, version, flag_id)
                            #cnxn.commit()
                        # Close ODBC cursor.
                        cur.close()
                        del cur
        # Return.
        return e
    
    # Get flag ID.
    def get_flag_id(self,ifo_id,flag):
        # Init.
        res = None
        # If args passed.
        try:
            ifo_id, flag
        except:
            pass
        else:
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT dq_flag_id
                            FROM tbl_dq_flags
                            WHERE dq_flag_ifo = ? AND dq_flag_name LIKE ?
                            ORDER BY dq_flag_id DESC
                            LIMIT 1
                            """, ifo_id, flag)
                # Loop.
                for row in cur:
                    # Set.
                    res = row.dq_flag_id
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res

    # Get flag version ID.
    def get_flag_version_id(self, flag_id, version):
        # Init.
        res = None
        # If args passed.
        try:
            flag_id, version
        except:
            pass
        else:
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT dq_flag_version_id
                            FROM tbl_dq_flag_versions
                            WHERE dq_flag_fk = ? AND dq_flag_version = ?
                            ORDER BY dq_flag_version_id DESC
                            LIMIT 1
                            """, flag_id, version)
                # Loop.
                for row in cur:
                    # Set.
                    res = row.dq_flag_version_id
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res

    # Get a list of flags.
    def get_flag_list(self, ifo):
        # Init.
        a = []
        # If arg passed.
        try:
            ifo
        except:
            pass
        else:
            # Get IFO ID.
            ifo_id = self.get_value_details(1,ifo)
            # If Ifo ID exists.
            if ifo_id != None:
                try:
                    # Set ODBC cursor.
                    cur = cnxn.cursor()
                except:
                    pass
                else:
                    # Get flags.
                    cur.execute("""
                                SELECT dq_flag_name
                                FROM tbl_dq_flags
                                WHERE dq_flag_ifo = ?
                                ORDER BY dq_flag_name
                                """, ifo_id)
                    # Loop.
                    for row in cur:
                        # Set.
                        a.append(row.dq_flag_name)
                    # Close ODBC cursor.
                    cur.close()
                    del cur
                    # Include inside named list.
                    a = {"results" : a}
        # Return.
        return a
            
    # Get a list of flag versions.
    def get_flag_version_list(self, ifo, flag):
        # Init.
        a = []
        # If args passed.
        try:
            ifo, flag
        except:
            pass
        else:
            # Get IFO ID.
            ifo_id = self.get_value_details(1,ifo)
            # If Ifo ID exists.
            if ifo_id != None:
                # Get flag ID.
                flag_id = self.get_flag_id(ifo_id,flag)
                # If flag ID exists.
                if flag_id != None:
                    try:
                        # Set ODBC cursor.
                        cur = cnxn.cursor()
                    except:
                        pass
                    else:
                        # Get flags.
                        cur.execute("""
                                    SELECT dq_flag_assoc_versions
                                    FROM tbl_dq_flags
                                    WHERE dq_flag_id = ?
                                    """, flag_id)
                        # Loop.
                        for row in cur:
                            # Set.
                            versions = row.dq_flag_assoc_versions
                            # If associated versions are available.
                            if not versions == '':
                                # Explode the versions.
                                assoc_versions = [int(x) for x in versions.split(",")]
                                # Loop versions.
                                for dq_flag_version in assoc_versions:
                                    # Set.
                                    a.append(dq_flag_version)
                        # Close ODBC cursor.
                        cur.close()
                        del cur
        # Return.
        return a

    # Get a flags version history.
    def get_flag_version_insert_history(self, vid):
        # Init.
        a = []
        # If arg passed.
        try:
            vid
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT tbl_processes.process_id, dq_flag_version_uri, dq_flag_version_last_modifier, insertion_time, value_txt AS 'auth_user', affected_active_data_start, affected_active_data_stop, affected_active_data_segment_total, affected_known_data_start, affected_known_data_stop, affected_known_data_segment_total, pid, process_full_name, fqdn, process_time_started 
                            FROM tbl_processes
                            LEFT JOIN tbl_dq_flag_versions ON tbl_processes.dq_flag_version_fk = tbl_dq_flag_versions.dq_flag_version_id
                            LEFT JOIN tbl_values ON tbl_processes.user_fk = tbl_values.value_id 
                            WHERE dq_flag_version_fk = ?
                            ORDER BY tbl_processes.process_id
                            """, vid)
                # Loop.
                for row in cur:
                    # Get associated args.
                    args = self.get_process_args(row.process_id)
                    # Set.
                    a.append({"insertion_metadata" : {"uri" : row.dq_flag_version_uri,
                                                 "timestamp" : int(row.insertion_time),
                                                 "auth_user" : self.get_value_detail_from_ID(row.dq_flag_version_last_modifier),
                                                 "insert_active_data_start" : int(row.affected_active_data_start),
                                                 "insert_active_data_stop" : int(row.affected_active_data_stop),
                                                 "insert_active_segment_total" : int(row.affected_active_data_segment_total),
                                                 "insert_known_data_start" : int(row.affected_known_data_start),
                                                 "insert_known_data_stop" : int(row.affected_known_data_stop),
                                                 "insert_known_segment_total" : int(row.affected_known_data_segment_total)},
                         "process_metadata" : {"pid" : row.pid,
                                               "name" : row.process_full_name,
                                               "args" : args,
                                               "fqdn" : row.fqdn,
                                               "uid" : row.auth_user,
                                               "process_start_timestamp" : int(row.process_time_started)}})
                # Close ODBC cursor.
                cur.close()
                del cur
        # Include inside dictionary under insertion history parent.
        a = {"insert_history" : a}
        # Return.
        return a

    # Get flag version metadata.
    def get_flag_version_metadata(self, request, ifo, flag, version, version_id):
        # Init.
        a = []
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # If arg passed.
        try:
            version_id
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get flags.
                cur.execute("""
                            SELECT *
                            FROM tbl_dq_flag_versions
                            LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id
                            WHERE dq_flag_version_id = ?
                            ORDER BY dq_flag_version_id
                            LIMIT 1
                            """, version_id)
                # Loop.
                for row in cur:
                        # Set.
                        description = row.dq_flag_description
                        comment = row.dq_flag_version_comment
                        uri = row.dq_flag_version_uri
                        deactivated = row.dq_flag_version_deactivated
                        badness = row.dq_flag_active_means_ifo_badness
                        a = admin.get_flag_metadata(ifo, flag, version, description, comment, uri, deactivated, badness)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return a

    # Get a list of all flags with versions for report.
    def get_flags_with_versions_for_report(self, req_method, full_uri):
        # Init.
        a = [];
        # If args passed.
        try:
            req_method, full_uri
        except:
            pass
        else:
            # Instantiate objects.
            admin = Admin.AdminHandle()
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT dq_flag_name, dq_flag_assoc_versions, value_txt
                            FROM tbl_dq_flags
                            LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
                            ORDER BY value_txt, dq_flag_name
                            """)
                # Loop.
                for row in cur:
                    # Set.
                    ifo = row.value_txt
                    flag = row.dq_flag_name
                    versions = row.dq_flag_assoc_versions
                    call_uri = '/dq/' + ifo + '/' + flag + '/'
                    # If no associated versions are available.
                    if versions == '':
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(409, 38, req_method, 'Check: ' + call_uri, full_uri)
                    # Otherwise, associated versions are available.
                    else:
                        # Explode the versions.
                        assoc_versions = [int(x) for x in versions.split(",")]
                        # Loop versions.
                        for dq_flag_version in assoc_versions:
                            # Add flag to available resource.
                            a.append(call_uri + str(dq_flag_version))
            # Include inside named array.
            a = {'results' : a}
        # Return.
        return a
    
    ##########################
    # VALUE HANDLING METHODS #
    ##########################
    
    # Get a value normalised ID using its string value.
    def get_value_details(self, g, v):
        # Init.
        res = None
        try:
            g, v
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT value_id
                            FROM tbl_values
                            WHERE value_group_fk=? AND value_txt LIKE ?
                            """, g, str(v))
                # Loop.
                for row in cur:
                    # Set.
                    res = row.value_id
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res
    
    # Get a value detail from its ID.
    def get_value_detail_from_ID(self, v):
        # Init.
        res = ''
        # If arg passed.
        try:
            v
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT value_txt
                            FROM tbl_values
                            WHERE value_id = ?
                            """, v)
                # Loop.
                for row in cur:
                    # Set.
                    res = row.value_txt
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res
    
    # Get a value group name using its ID.
    def get_value_group_details(self, g):
        # Init.
        res = None
        # If args passed.
        try:
            g
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT value_group
                            FROM tbl_value_groups
                            WHERE value_group_id=?
                            """, g)
                # Loop.
                for row in cur:
                    # Set.
                    res = row.value_group
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res

    # Get a list of values belonging to a specific group as a list.
    def get_value_list(self, g):
        # Init.
        a = []
        # If arg passed.
        try:
            g
        except:
            pass
        else:
            try:
                # Set ODBC cursor
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get value group name.
                group = self.get_value_group_details(g)
                # If group name obtained.
                if not group == None:
                    # Get.
                    cur.execute("""
                                SELECT value_txt
                                FROM tbl_values
                                WHERE value_group_fk LIKE ?
                                ORDER BY value_txt
                                """, g)
                    # Loop.
                    for row in cur:
                        # Set.
                        a.append(row.value_txt)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Include inside named list.
        a = {"Ifos" : a}
        # Return.
        return a

    ##########################
    # USER HANDLING METHODS #
    ########################
    
    # Insert new user to database.
    def insert_user(self, u):
        # Init
        uid = None
        # If arg passed.
        try:
            u
        except:
            pass
        else:
            try: 
                uid = self.get_value_details(2, u)
            except:
                pass
            # If user does not exist.
            if uid == None:
                try:
                    cur = cnxn.cursor()
                except:
                    pass
                else:
                        # Insert flag.
                        cur.execute("""
                                    INSERT INTO tbl_values
                                    (value_group_fk, value_txt)
                                    VALUES
                                    (2,?)
                                    """, str(u))
                        cnxn.commit()
                        # Close ODBC cursor.
                        cur.close()
                        del cur
                    
    #############################
    # PROCESS HANDLING METHODS #
    ###########################
        
    # Insert process to DB and get id.
    def insert_process(self, request, data, vid, uid, seg_tot, seg_start, seg_stop):
        # If arg passed.
        try:
            request
        except:
            pass
        else:
            # Instantiate objects.
            constant = Constants.ConstantsHandle()
            user = User.UserHandle()
            # Loop through insert history dictionary.
            for key in data['insert_history']:
                # Get a process ID from a version ID, pid and timestamp.
                process_id = self.get_process_id_from_vid_pid_timestamp(vid, key['process_metadata']['pid'], uid)
                # If this process has not already been inserted into the database.
                if process_id == 0:
                    # Get user id if not passed.
                    if uid == 0 or uid == None:
                        try:
                            uid = user.get_user_id(key['insertion_metadata']['auth_user'])
                        except:
                            pass
                    # Re-check user id and make sure version ID has been passed.
                    if not uid == 0 and not uid == None and not vid == None:
                        # If database connection established.
                        try:
                            cur = cnxn.cursor()
                        except:
                            pass
                        else:
                            # Get values.
                            gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
                            # data_format = self.get_value_details(3, data['flag']['data_format'])
                            data_format = 5 # Was 8, fixed until removal
                            # Insert process.
                            cur.execute("""
	                                    INSERT INTO tbl_processes
	                                    (dq_flag_version_fk, process_full_name, pid, fqdn, data_format_fk, user_fk, insertion_time, process_time_started)
	                                    VALUES
	                                    (?,?,?,?,?,?,?,?);
	                                    """, vid, str(key['process_metadata']['name']), int(key['process_metadata']['pid']), str(key['process_metadata']['fqdn']), data_format, uid, gps, str(key['process_metadata']['process_start_timestamp']))
                            #cnxn.commit()
                            # Get ID of process committed.
                            process_id = self.get_new_process_id(vid, int(key['process_metadata']['pid']), uid, gps)
                            # If new process ID found.
                            if not process_id == 0:
                                # Insert process args.
                                self.insert_process_args(process_id, key['process_metadata']['args'])
                            # Close ODBC cursor.
                            cur.close()
                            del cur
            # Update the process global values.
            self.update_process_global_values(request, process_id, vid, seg_tot, seg_start, seg_stop)

    # Get ID of process committed.
    def get_new_process_id(self, vid, pid, uid, gps):
        # Init.
        r = 0;
        # If args passed.
        try:
            vid, pid, uid, gps
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT process_id
                            FROM tbl_processes
                            WHERE dq_flag_version_fk=? AND pid=? AND user_fk=? AND insertion_time=?
                            ORDER BY process_id DESC
                            LIMIT 1
                            """, vid, pid, uid, gps)
                # Loop.
                for row in cur:
                    # Set.
                    r = row.process_id
        # Return.
        return r
        
    # Insert process args.
    def insert_process_args(self, pid, args):
        # If args passed.
        try:
            pid, args
        except:
            pass
        else:
            # If database connection established.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Loop through args.
                for argv in args:
                    # Insert process.
                    cur.execute("""
                                 INSERT INTO tbl_process_args
                                 (process_fk, process_argv)
                                 VALUES
                                 (?,?);
                                 """, pid, str(argv))
                    #cnxn.commit()
                # Close ODBC cursor.
                cur.close()
                del cur

    # Get a list of all args associated to a process.
    def get_process_args(self, pid):
        # Init.
        a = [];
        # If arg passed.
        try:
            pid
        except:
            pass
        else:
            try:
                # Set ODBC cursor.
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT process_argv
                            FROM tbl_process_args
                            WHERE process_fk=?
                            ORDER BY process_arg_id
                            """, pid)
                # Loop.
                for row in cur:
                    # Set.
                    argv = row.process_argv
                    # Add process to list.
                    a.append(argv)
        # Return.
        return a

    # Get a process ID from a version ID, pid and timestamp.
    def get_process_id_from_vid_pid_timestamp(self, vid, pid, u):
        # Init.
        r = 0
        # If args passed.
        try:
            vid, pid, u
        except:
            pass
        else:
            # If database connection established.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # WHERE dq_flag_version_fk=? AND pid=? AND process_time_started=?
                # Get.
                cur.execute("""
                            SELECT process_id
                            FROM tbl_processes
                            WHERE dq_flag_version_fk=? AND pid=? AND user_fk=?
			                ORDER BY process_id DESC
                            LIMIT 1
                            """, vid, pid, u)
                # Loop.
                for row in cur:
                    # Set.
                    r = row.process_id
                # Close ODBC cursor.
                cur.close()
                del cur            
        # Return.
        return r
            
    #############################
    # SEGMENT HANDLING METHODS #
    ###########################
    
    # Insert segments.
    def insert_segments(self, request, req_method, full_uri, ifo_id, ifo, flag_id, flag, version_id, version, data):
        # Init.
        e = []
        # Instantiate objects.
        admin = Admin.AdminHandle()
        user = User.UserHandle()
        # Check args passed.
        try:
            request, req_method, full_uri, ifo_id, ifo, flag_id, flag, version_id, version, data
        except:
            pass
        else:
            # Check whether the requested segment type is in the data dictionary.
            if not request in data:
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(400, 11, req_method, None, full_uri)
            else:
                # Get user id.
                uid = user.get_user_id(data['insert_history'][0]['insertion_metadata']['auth_user'])
                # If user ID does not exist.
                if uid == 0:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(404, 2, req_method, None, full_uri)
                else:
                    # Initialise ODBC cursor.
                    try:
                        cur = cnxn.cursor()
                    except:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(404, 4, req_method, None, full_uri)
                    else:
                        # Init segment global values.
                        seg_tot = 0
                        seg_first_gps = 0
                        seg_last_gps = 0
                        # Get segments into SQL for insert.
                        sql = ''
                        for k, v in data[request]:
                            sql = sql + ',(' + str(version_id) + ',' + str(k) + ',' + str(v) + ')'
                            # Set segment global values.
                            seg_tot += 1
                            seg_first_gps = admin.set_var_if_higher_lower('l', k, seg_first_gps) 
                            seg_last_gps = admin.set_var_if_higher_lower('h', v, seg_last_gps)
                        '''
                        # If segments do not exist.
                        if seg_tot == 0:
                            # Set HTTP code and log.
                            admin.log_and_set_http_code(200, 12, req_method, request, full_uri)
                        # Otherwise, insert segments.
                        else:
                            # Set HTTP code and log.
                            admin.log_and_set_http_code(200, 34, req_method, request, full_uri)
                        '''
                        # If segments exist.
                        if seg_tot != 0:
                            # Remove first delimiter.
                            sql = sql[1:]
                            # Set table to use dependent upon type of insert.
                            tbl = 's'
                            if request == 'known':
                                tbl = '_summary'
                            # Insert segment.
                            cur.execute("INSERT INTO tbl_segment" + tbl + " (dq_flag_version_fk, segment_start_time, segment_stop_time) VALUES" + sql)
                            #cnxn.commit()
                            # Update version segment global values.
                            self.update_segment_global_values(request, version_id, seg_tot, seg_first_gps, seg_last_gps)
                            # Insert process.
                            self.insert_process(request, data, version_id, uid, seg_tot, seg_first_gps, seg_last_gps)
                            # Close ODBC cursor.
                            cur.close()
                            del cur
        # Return
        return e

    # Commit transaction to database.
    def commit_transaction_to_db(self):
        # Commit transaction.
        cnxn.commit()

    # Update version segment global values.
    def update_segment_global_values(self, request, vid, tot, start, stop):
        # If args passed.
        try:
            request, vid, tot, start, stop
        except:
            pass
        else:
            # Instantiate objects.
            admin = Admin.AdminHandle()
            # Initialise ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT dq_flag_version_""" + request + """_segment_total AS 'tot', dq_flag_version_""" + request + """_earliest_segment_time AS 'earliest', dq_flag_version_""" + request + """_latest_segment_time AS 'latest'
                            FROM tbl_dq_flag_versions
                            WHERE dq_flag_version_id=?
                            """, vid)
                # Loop.
                for row in cur:
                    # Set.
                    start = admin.set_var_if_higher_lower('l', start, row.earliest) 
                    stop = admin.set_var_if_higher_lower('h', stop, row.latest)
                    tot = tot + row.tot
            # Update segment global values.
            cur.execute("""
                        UPDATE tbl_dq_flag_versions
                        SET dq_flag_version_""" + request + """_segment_total=?, dq_flag_version_""" + request + """_earliest_segment_time=?, dq_flag_version_""" + request + """_latest_segment_time=?
                        WHERE dq_flag_version_id=?
                        """, tot, int(start), int(stop), vid)
            #cnxn.commit()
            # Close ODBC cursor.
            cur.close()
            del cur                            

    # Update process segment global values.
    def update_process_global_values(self, request, process_id, vid, tot, start, stop):
        # If args passed.
        try:
            request, process_id, vid, tot, start, stop
        except:
            pass
        else:
            # Instantiate objects.
            admin = Admin.AdminHandle()
            # Initialise ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT process_id, affected_""" + request + """_data_segment_total AS 'tot', affected_""" + request + """_data_start AS 'earliest', affected_""" + request + """_data_stop AS 'latest'
                            FROM tbl_processes
                            WHERE process_id=?
                            """, process_id)
                # Loop.
                for row in cur:
                    # Set.
                    start = admin.set_var_if_higher_lower('l', start, row.earliest)
                    stop = admin.set_var_if_higher_lower('h', stop, row.latest)
                    tot = tot + row.tot
            # Update segment global values.
            cur.execute("""
                        UPDATE tbl_processes
                        SET affected_""" + request + """_data_segment_total=?, affected_""" + request + """_data_start=?, affected_""" + request + """_data_stop=?
                        WHERE process_id=?
                        """, tot, int(start), int(stop), process_id)
            #cnxn.commit()
            # Close ODBC cursor.
            cur.close()
            del cur                            

    # Get total number of segments associated to a version.
    def get_flag_version_segment_total(self, request, vid):
        # Init.
        r = 0
        # If arg passed.
        try:
            vid
        except:
            pass
        else:
            # Initialise ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Get.
                cur.execute("""
                            SELECT dq_flag_version_""" + request + """_segment_total AS 'tot'
                            FROM tbl_dq_flag_versions
                            WHERE dq_flag_version_id=?
                            """, vid)
                # Loop.
                for row in cur:
                    # Set.
                    r = row.tot
        # Return.
        return r

    # Get specific flag & version segments.
    def get_flag_version_segments(self, request, version_id, t1, t2):
        # Init.
        a = []
        w = ''
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # If required args passed.
        try:
            request
        except:
            pass
        else:
            # Set WHERE SQL.
            if t1 and not t2:
                w = ' segment_stop_time >= ' + t1
            elif not t1 and t2:
                w = ' segment_start_time <= ' + t2
            elif t1 and t2:
                w = ' segment_stop_time >= ' + t1 + ' AND segment_start_time <= ' + t2
            # Initialise ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set table to use dependent upon type of insert.
                tbl = 's'
                if request == 'known':
                    tbl = '_summary'
                # If request within acceptable range, i.e. 'active', 'known', etc., get list of all flags over period requested by args.
                if not admin.check_request('seg', request) == False:
                    # If Ifo, flag and version passed.
                    try:
                        version_id
                    except:
                        pass
                    else:
                        # If version ID found.
                        if not version_id == None:
                            # Add the AND operator is added if necessary.
                            if not w == '':
                                w += ' AND '
                            # Add version to the WHERE clause.
                            x = 'dq_flag_version_fk = %d' % (version_id)
                            w += x
                    if not w == '':
                        w = 'WHERE ' + w
                    # Get.
                    cur.execute("""
                                SELECT segment_start_time, segment_stop_time
                                FROM tbl_segment""" + tbl + """
                                """ + w + """
                                ORDER BY segment_start_time""")
                    # Loop.
                    for row in cur:
                        # Set.
                        t1 = int(row.segment_start_time)
                        t2 = int(row.segment_stop_time)
                        # Append segments to list.
                        a.append([t1,t2])
                    # Close ODBC cursor.
                    cur.close()
                    del cur
            # Insert in request dictionary.
            a = {request : a}
        # Return.
        return a
    
    # Get report segments.
    def get_report_segments(self, request, t1, t2, request_array):
        # Init.
        a = []
        flag_array = []
        flag_json = []
        seg_sql = ''
        w = ''
        pre_v_fk = 0
        i = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # If required args passed.
        try:
            request
        except:
            pass
        else:
            # Set WHERE clause.
            if t1 and not t2:
                w = ' segment_stop_time >= ' + t1
            elif not t1 and t2:
                w = ' segment_start_time <= ' + t2
            elif t1 and t2:
                w = ' segment_stop_time >= ' + t1 + ' AND segment_start_time <= ' + t2
            # If WHERE clause has been set.
            if not w == '':
                w = ' WHERE ' + w
            # Initialise ODBC cursor.
            try:
                cur = cnxn.cursor()
            except:
                pass
            else:
                # Set table to use dependent upon type of insert.
                tbl = 's'
                if request == 'known':
                    tbl = '_summary'
                # If request within acceptable range, i.e. 'active', 'known', etc., get list of all flags over period requested by args.
                if not admin.check_request('seg', request) == False:
                    # If 'known' or 'active' segments or everything included.
                    if 'known' in request_array or 'active' in request_array or not request_array:
                        # Get the additional fields from the DB.
                        seg_sql = ', segment_start_time, segment_stop_time '
                    # Get.
                    cur.execute("""
                                SELECT dq_flag_name, value_txt AS 'dq_flag_ifo_txt', dq_flag_description, dq_flag_active_means_ifo_badness, dq_flag_version_uri, dq_flag_version_deactivated, dq_flag_version, dq_flag_version_fk""" + seg_sql + """
                                FROM
                                (SELECT dq_flag_version_fk""" + seg_sql + """
                                FROM tbl_segment""" + tbl + w + """
                                ORDER BY dq_flag_version_fk) AS t1
                                LEFT JOIN tbl_dq_flag_versions ON t1.dq_flag_version_fk = tbl_dq_flag_versions.dq_flag_version_id
                                LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id
                                LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
                                """)
                    # Loop.
                    for row in cur:
                        # If this is a different flag.
                        if not pre_v_fk == row.dq_flag_version_fk:
                            # If metadata or everything included.
                            if 'metadata' in request_array or not request_array:
                                # Get metadata for this flag.
                                flag_json = admin.get_flag_metadata(row.dq_flag_ifo_txt, row.dq_flag_name, str(row.dq_flag_version), row.dq_flag_description, row.dq_flag_version_uri, row.dq_flag_version_deactivated, row.dq_flag_active_means_ifo_badness)
                            # If 'known' or 'active' segments or everything included.
                            if 'known' in request_array or 'active' in request_array or not request_array:
                                # Reset segment array.
                                flag_json[request] = []
                            # Add segment array to metadata.
                            flag_array.append(flag_json)
                            # If not on the first loop.
                            if not pre_v_fk == 0:
                                # Increment array key.
                                i += 1
                        # If 'known' segments or everything included.
                        if 'known' in request_array or not request_array:
                            # Set segment start/stop times.
                            t1 = int(row.segment_start_time)
                            t2 = int(row.segment_stop_time)
                            # Append segments to list.
                            flag_array[i][request].append([t1,t2])
                        # Set previous version FK for use in next loop. 
                        pre_v_fk = row.dq_flag_version_fk
                    # Close ODBC cursor.
                    cur.close()
                    del cur
            # Set in overall dictionary.
            a = {'results' : flag_array}
        # Return.
        return a
