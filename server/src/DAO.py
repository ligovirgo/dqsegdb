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
Data Access Object class file
'''

# Import.
import Admin
import Constants
import gpstime
import pyodbc
import time
import User
from collections import defaultdict

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
            cnxn = pyodbc.connect(connection_str) # .odbc.ini in /etc/    FILE DATA SOURCES..: /usr/local/etc/ODBCDataSources    USER DATA SOURCES..: /root/.odbc.ini
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
    def get_segment_boundaries(self, ak, w, ifo, req_method, full_uri):
        # Init.
        res = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # Set ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
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
            # If looking at specific IFO.
            if not ifo == None:
                j = ' LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id '
                iw = ' AND dq_flag_ifo=' + str(ifo)
                
            try:
                # Get.
                cur.execute("""
                            SELECT """ + m + """(dq_flag_version_""" + ak + """_""" + el + """_segment_time) AS 'tot'
                            FROM tbl_dq_flag_versions """
                            + j +
                            """WHERE dq_flag_version_""" + ak + """_""" + el + """_segment_time <> 0 """
                            + iw)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # If tot exists.
                    if not row.tot == None:
                        # If using sub-second segments.
                        if constant.use_sub_second_segments:
                            # Set.
                            res = float(row.tot)
                        # Otherwise, integers.
                        else:
                            # Set.
                            res = int(row.tot)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Return.
        return res
    
    # Get segment totals.
    def get_segment_totals(self, ak, ifo, req_method, full_uri):
        # Init.
        res = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # Set ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            # Set IFO.
            j = ''
            iw = ''
            if not ifo == None:
                j = ' LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id '
                iw = ' WHERE dq_flag_ifo=' + str(ifo)
            try:
                # Get.
                cur.execute("""
                            SELECT SUM(dq_flag_version_""" + ak + """_segment_total) AS 'tot'
                            FROM tbl_dq_flag_versions """ + j  + iw)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
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
    def get_last_segment_insert_time(self, ifo, req_method, full_uri):
        # Init.
        res = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # Set ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
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
            try:
                # Get.
                cur.execute("""
                            SELECT MAX(insertion_time) AS 'tot'
                            FROM tbl_processes """ + j  + iw)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
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
    def get_flag_totals(self, ifo, req_method, full_uri):
        # Init.
        res = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # Set ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            # Set IFO.
            iw = ''
            if not ifo == None:
                iw = ' WHERE dq_flag_ifo=' + str(ifo)
            try:
                # Get.
                cur.execute("""
                            SELECT COUNT(dq_flag_id) AS 'tot'
                            FROM tbl_dq_flags """ + iw)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
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
    def get_flag_version_totals(self, ifo, req_method, full_uri):
        # Init.
        res = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # Set ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            # Set IFO.
            j = ''
            iw = ''
            if not ifo == None:
                j = ' LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id '
                iw = ' WHERE dq_flag_ifo=' + str(ifo)
            try:
                # Get.
                cur.execute("""
                            SELECT COUNT(dq_flag_version_id) AS 'tot'
                            FROM tbl_dq_flag_versions """ + j  + iw)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
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
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        user = User.UserHandle()
        # If flag does not yet exist.
        if not self.get_flag_id(ifo_id, flag, req_method, full_uri) == None:
            # Set HTTP code and log.
            e = admin.log_and_set_http_code(400, 6, req_method, None, full_uri)
        else:
            # Get user id.
            uid = user.get_user_id(data['insert_history'][0]['insertion_metadata']['auth_user'], req_method, full_uri)
            # If user ID does not exist.
            if uid == 0:
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(404, 2, req_method, None, full_uri)
            else:
                # Set ODBC cursor.
                try:
                    cur = cnxn.cursor()
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(500, 40, req_method, str(err), full_uri)
                else:
                    # If badness available in JSON.
                    badness = admin.convert_boolean_to_int(data['metadata']['active_indicates_ifo_badness'])
                    gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
                    try:
                        # Insert flag.
                        cur.execute("""
                                    INSERT INTO tbl_dq_flags
                                    (dq_flag_name, dq_flag_ifo, dq_flag_active_means_ifo_badness, dq_flag_creator, dq_flag_date_created)
                                    VALUES
                                    (?,?,?,?,?)
                                    """, flag, ifo_id, badness, uid, gps)
                        cnxn.commit()
                    except pyodbc.Error as err:
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                    else:
                        try:
                            # Get new flag ID.
                            cur.execute("""
                                        SELECT dq_flag_id
                                        FROM tbl_dq_flags
                                        WHERE dq_flag_ifo = ? AND dq_flag_name = ?
                                        ORDER BY dq_flag_id DESC
                                        LIMIT 1
                                        """, ifo_id, flag)
                        except pyodbc.Error as err:
                            # Set HTTP code and log.
                            admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                        else:
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
        # If the flag version already exists.
        if self.get_flag_version_id(flag_id, version, req_method, full_uri):
            # Set HTTP code and log.
            e = admin.log_and_set_http_code(400, 7, req_method, None, full_uri)
        else:
            # Get user id.
            uid = user.get_user_id(data['insert_history'][0]['insertion_metadata']['auth_user'], req_method, full_uri)
            # If user ID does not exist.
            if uid == 0:
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(404, 2, req_method, None, full_uri)
            else:
                try:
                    # Set ODBC cursor.
                    cur = cnxn.cursor()
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(500, 40, req_method, str(err), full_uri)
                else:
                    # Set required value formats.
                    deactivated = admin.convert_boolean_to_int(data['metadata']['deactivated'])
                    gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
                    comment = str(data['metadata']['flag_description'])
                    try:
                        # Insert version.
                        cur.execute("""
                                    INSERT INTO tbl_dq_flag_versions
                                    (dq_flag_fk, dq_flag_description, dq_flag_version, dq_flag_version_deactivated, dq_flag_version_last_modifier, dq_flag_version_comment, dq_flag_version_uri, dq_flag_version_date_created, dq_flag_version_date_last_modified)
                                    VALUES
                                    (?,?,?,?,?,?,?,?,?)
                                    """, flag_id, comment, version, deactivated, uid, str(data['metadata']['flag_version_comment']), str(data['metadata']['further_info_url']), gps, gps)
                    except pyodbc.Error as err:
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                    else:
                        # Get version ID.
                        vid = self.get_flag_version_id(flag_id, version, req_method, full_uri)
                        # If no version ID found.
                        if not vid:
                            # Set HTTP code and log.
                            e = admin.log_and_set_http_code(400, 29, req_method, None, full_uri)
                        # Otherwise.
                        else:
                            try:
                                # Append version to list of associated versions in flag table.
                                cur.execute("""
                                            UPDATE tbl_dq_flags
                                            SET dq_flag_assoc_versions = IF(dq_flag_assoc_versions='',?,CONCAT(dq_flag_assoc_versions,',',?))
                                            WHERE dq_flag_id = ?
                                            """, version, version, flag_id)
                            except pyodbc.Error as err:
                                # Set HTTP code and log.
                                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                    # Close ODBC cursor.
                    cur.close()
                    del cur
        # Return.
        return e
    
    # Get flag ID.
    def get_flag_id(self, ifo_id, flag, req_method, full_uri):
        # Init.
        res = None
        # Escape the flag wildcards characters.
        flag = flag.replace('_', '\_')
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT dq_flag_id
                            FROM tbl_dq_flags
                            WHERE dq_flag_ifo = ? AND dq_flag_name LIKE ?
                            ORDER BY dq_flag_id DESC
                            LIMIT 1
                            """, ifo_id, flag)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
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
    def get_flag_version_id(self, flag_id, version, req_method, full_uri):
        # Init.
        res = None
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT dq_flag_version_id
                            FROM tbl_dq_flag_versions
                            WHERE dq_flag_fk = ? AND dq_flag_version = ?
                            ORDER BY dq_flag_version_id DESC
                            LIMIT 1
                            """, flag_id, version)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
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
    def get_flag_list(self, ifo, req_method, full_uri):
        # Init.
        a = []
        # Get IFO ID.
        ifo_id = self.get_value_details(1, ifo, req_method, full_uri)
        # If Ifo ID exists.
        if ifo_id != None:
            # Instantiate objects.
            admin = Admin.AdminHandle()
            try:
                cur = cnxn.cursor()
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
            else:
                try:
                    # Get flags.
                    cur.execute("""
                                SELECT dq_flag_name
                                FROM tbl_dq_flags
                                WHERE dq_flag_ifo = ?
                                ORDER BY dq_flag_name
                                """, ifo_id)
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                else:
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
    def get_flag_version_list(self, ifo, flag, req_method, full_uri):
        # Init.
        a = []
        # Get IFO ID.
        ifo_id = self.get_value_details(1, ifo, req_method, full_uri)
        # If Ifo ID exists.
        if ifo_id != None:
            # Get flag ID.
            flag_id = self.get_flag_id(ifo_id,flag, req_method, full_uri)
            # If flag ID exists.
            if flag_id != None:
                # Instantiate objects.
                admin = Admin.AdminHandle()
                try:
                    cur = cnxn.cursor()
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
                else:
                    try:
                        # Get flags.
                        cur.execute("""
                                    SELECT dq_flag_assoc_versions
                                    FROM tbl_dq_flags
                                    WHERE dq_flag_id = ?
                                    """, flag_id)
                    except pyodbc.Error as err:
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                    else:
                        # Loop.
                        for row in cur:
                            # Set.
                            versions = row.dq_flag_assoc_versions
                            # If associated versions are available.
                            if not versions == '' and not versions == None:
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
    def get_flag_version_insert_history(self, vid, req_method, full_uri):
        # Init.
        a = []
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT tbl_processes.process_id, process_comment, dq_flag_version_last_modifier, insertion_time, value_txt AS 'auth_user', affected_active_data_start, affected_active_data_stop, affected_active_data_segment_total, affected_known_data_start, affected_known_data_stop, affected_known_data_segment_total, pid, process_full_name, fqdn, process_args, process_time_started 
                            FROM tbl_processes
                            LEFT JOIN tbl_dq_flag_versions ON tbl_processes.dq_flag_version_fk = tbl_dq_flag_versions.dq_flag_version_id
                            LEFT JOIN tbl_values ON tbl_processes.user_fk = tbl_values.value_id 
                            WHERE dq_flag_version_fk = ?
                            ORDER BY tbl_processes.process_id
                            """, vid)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # If using sub-second segments.
                    if constant.use_sub_second_segments:
                        # Set.
                        affected_active_data_start = float(row.affected_active_data_start)
                        affected_active_data_stop = float(row.affected_active_data_stop)
                        affected_known_data_start = float(row.affected_known_data_start)
                        affected_known_data_stop = float(row.affected_known_data_stop)
                    # Otherwise, integers.
                    else:
                        # Set.
                        affected_active_data_start = int(row.affected_active_data_start)
                        affected_active_data_stop = int(row.affected_active_data_stop)
                        affected_known_data_start = int(row.affected_known_data_start)
                        affected_known_data_stop = int(row.affected_known_data_stop)
                    # Set.
                    a.append({"insertion_metadata" : {"comment" : row.process_comment,
                                                      "timestamp" : int(row.insertion_time),
                                                      "auth_user" : self.get_value_detail_from_ID(row.dq_flag_version_last_modifier, req_method, full_uri),
                                                      "insert_active_data_start" : affected_active_data_start,
                                                      "insert_active_data_stop" : affected_active_data_stop,
                                                      "insert_active_segment_total" : int(row.affected_active_data_segment_total),
                                                      "insert_known_data_start" : affected_known_data_start,
                                                      "insert_known_data_stop" : affected_known_data_stop,
                                                      "insert_known_segment_total" : int(row.affected_known_data_segment_total)},
                              "process_metadata" : {"pid" : row.pid,
                                                    "name" : row.process_full_name,
                                                    "args" : row.process_args,
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
    def get_flag_version_metadata(self, request, ifo, flag, version, version_id, req_method, full_uri):
        # Init.
        d = {}
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get flags.
                cur.execute("""
                            SELECT *
                            FROM tbl_dq_flag_versions
                            LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id
                            WHERE dq_flag_version_id = ?
                            ORDER BY dq_flag_version_id
                            LIMIT 1
                            """, version_id)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    description = row.dq_flag_description
                    comment = row.dq_flag_version_comment
                    uri = row.dq_flag_version_uri
                    deactivated = row.dq_flag_version_deactivated
                    badness = row.dq_flag_active_means_ifo_badness
                    d = admin.get_flag_metadata(ifo, flag, version, description, comment, uri, deactivated, badness)
            # Close ODBC cursor.
            cur.close()
            del cur
        # Return.
        return d

    # Get a list of all flags with versions for report.
    def get_flags_with_versions_for_report(self, req_method, full_uri):
        # Init.
        l = []
        d = {}
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT dq_flag_name, dq_flag_assoc_versions, value_txt
                            FROM tbl_dq_flags
                            LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
                            ORDER BY value_txt, dq_flag_name
                            """)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    ifo = row.value_txt
                    flag = row.dq_flag_name
                    versions = row.dq_flag_assoc_versions
                    call_uri = '/dq/' + ifo + '/' + flag + '/'
                    # If no associated versions are available.
                    if versions == '' or versions == None:
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(409, 38, req_method, 'Check: ' + call_uri, full_uri)
                    # Otherwise, associated versions are available.
                    else:
                        # Explode the versions.
                        assoc_versions = [int(x) for x in versions.split(",")]
                        # Loop versions.
                        for dq_flag_version in assoc_versions:
                            # Add flag to available resource.
                            l.append(call_uri + str(dq_flag_version))
        # Include inside named dictionary.
        d['results'] = l
        # Return.
        return d

    # Get a dictionary of all flags with coverage statistics for report.
    def get_flag_version_coverage(self, req_method, full_uri):
        # Init.
        f = {}
        d = {}
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT dq_flag_name, dq_flag_version, value_txt, dq_flag_version_active_segment_total, dq_flag_version_active_earliest_segment_time, dq_flag_version_active_latest_segment_time, dq_flag_version_known_segment_total, dq_flag_version_known_earliest_segment_time, dq_flag_version_known_latest_segment_time
                            FROM tbl_dq_flags
                            LEFT JOIN tbl_dq_flag_versions ON tbl_dq_flags.dq_flag_id = tbl_dq_flag_versions.dq_flag_fk
                            LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
                            ORDER BY value_txt, dq_flag_name
                            """)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set call URI.
                    call_uri = '/dq/' + row.value_txt + '/' + row.dq_flag_name + '/' + str(row.dq_flag_version)
                    # If using sub-second segments.
                    if constant.use_sub_second_segments:
                        # Set segment info.
                        active_earliest = float(row.dq_flag_version_active_earliest_segment_time)
                        active_latest = float(row.dq_flag_version_active_latest_segment_time)
                        known_earliest = float(row.dq_flag_version_known_earliest_segment_time)
                        known_latest = float(row.dq_flag_version_known_latest_segment_time)
                    # Otherwise, integers.
                    else:
                        # Set segment info.
                        active_earliest = int(row.dq_flag_version_active_earliest_segment_time)
                        active_latest = int(row.dq_flag_version_active_latest_segment_time)
                        known_earliest = int(row.dq_flag_version_known_earliest_segment_time)
                        known_latest = int(row.dq_flag_version_known_latest_segment_time)
                    # Build dictionary.
                    f.update({
                            call_uri : {
                                            'total_active_segments' : row.dq_flag_version_active_segment_total,
                                            'earliest_active_segment' : 0 if active_earliest is None else active_earliest,
                                            'latest_active_segment' : 0 if active_latest is None else active_latest,
                                            'total_known_segments' : row.dq_flag_version_known_segment_total,
                                            'earliest_known_segment' : 0 if known_earliest is None else known_earliest,
                                            'latest_known_segment' : 0 if known_latest is None else known_latest
                                        }
                         })
        # Include inside named dictionary.
        d['results'] = f
        # Return.
        return d

    ##########################
    # VALUE HANDLING METHODS #
    ##########################
    
    # Get a value normalised ID using its string value.
    def get_value_details(self, g, v, req_method, full_uri):
        # Init.
        r = None
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT value_id
                            FROM tbl_values
                            WHERE value_group_fk=? AND value_txt LIKE ?
                            """, g, str(v))
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    r = row.value_id
            # Close ODBC cursor.
            cur.close()
            del cur
        # Return.
        return r
    
    # Get a value detail from its ID.
    def get_value_detail_from_ID(self, v, req_method, full_uri):
        # Init.
        r = ''
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT value_txt
                            FROM tbl_values
                            WHERE value_id = ?
                            """, v)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    r = row.value_txt
            # Close ODBC cursor.
            cur.close()
            del cur
        # Return.
        return r
    
    # Get a value group name using its ID.
    def get_value_group_details(self, g, req_method, full_uri):
        # Init.
        r = None
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT value_group
                            FROM tbl_value_groups
                            WHERE value_group_id=?
                            """, g)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    r = row.value_group
            # Close ODBC cursor.
            cur.close()
            del cur
        # Return.
        return r

    # Get a list of values belonging to a specific group as a list.
    def get_value_list(self, g, req_method, full_uri):
        # Init.
        l = []
        d = {}
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            # Get value group name.
            group = self.get_value_group_details(g, req_method, full_uri)
            # If group name obtained.
            if not group == None:
                try:
                    # Get.
                    cur.execute("""
                                SELECT value_txt
                                FROM tbl_values
                                WHERE value_group_fk LIKE ?
                                ORDER BY value_txt
                                """, g)
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                else:
                    # Loop.
                    for row in cur:
                        # Set.
                        l.append(row.value_txt)
            # Close ODBC cursor.
            cur.close()
            del cur
        # Include inside named list.
        d['Ifos'] = l
        # Return.
        return d

    ##########################
    # USER HANDLING METHODS #
    ########################
    
    # Insert new user to database.
    def insert_user(self, u, req_method, full_uri):
        # Init
        uid = None
        try: 
            uid = self.get_value_details(2, u, req_method, full_uri)
        except:
            pass
        else:
            # If user does not exist.
            if uid == None:
                # Instantiate objects.
                admin = Admin.AdminHandle()
                try:
                    # Set ODBC cursor.
                    cur = cnxn.cursor()
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
                else:
                    try:
                        # Insert flag.
                        cur.execute("""
                                    INSERT INTO tbl_values
                                    (value_group_fk, value_txt)
                                    VALUES
                                    (2,?)
                                    """, str(u))
                        cnxn.commit()
                    except pyodbc.Error as err:
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                    # Close ODBC cursor.
                    cur.close()
                    del cur
                    
    #############################
    # PROCESS HANDLING METHODS #
    ###########################
        
    # Insert process to DB and get id.
    def insert_process(self, data, vid, uid, known_seg_tot, known_seg_start, known_seg_stop, active_seg_tot, active_seg_start, active_seg_stop, req_method, full_uri):
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        user = User.UserHandle()
        # Init.
        inserted = defaultdict(list)
        # Loop through insert history dictionary.
        for key in data['insert_history']:
            # Set concatenated history.
            history_concat = str(key['process_metadata'])
            # If this history has not yet been inserted.
            if not history_concat in inserted:
                # Get user id if not passed.
                if uid == 0 or uid == None:
                    try:
                        uid = user.get_user_id(key['insertion_metadata']['auth_user'], req_method, full_uri)
                    except:
                        pass
                # Re-check user id and make sure version ID has been passed.
                if not uid == 0 and not uid == None and not vid == None:
                    # If database connection established.
                    try:
                        cur = cnxn.cursor()
                    except pyodbc.Error as err:
                        # Set HTTP code and log.
                        admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
                    else:
                        # Get values.
                        gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
                        try:
                            # If using sub-second segments.
                            if constant.use_sub_second_segments:
                                # Set.
                                known_seg_start = float(known_seg_start)
                                known_seg_stop = float(known_seg_stop)
                                active_seg_start = float(active_seg_start)
                                active_seg_stop = float(active_seg_stop)
                            # Otherwise, integers.
                            else:
                                # Set.
                                known_seg_start = int(known_seg_start)
                                known_seg_stop = int(known_seg_stop)
                                active_seg_start = int(active_seg_start)
                                active_seg_stop = int(active_seg_stop)
                            # Insert process.
                            cur.execute("""
        	                            INSERT INTO tbl_processes
        	                            (dq_flag_version_fk,
                                         process_full_name,
                                         pid,
                                         fqdn,
                                         process_args,
                                         user_fk,
                                         insertion_time,
                                         affected_known_data_segment_total,
                                         affected_known_data_start,
                                         affected_known_data_stop,
                                         affected_active_data_segment_total,
                                         affected_active_data_start,
                                         affected_active_data_stop,
                                         process_time_started,
                                         process_time_last_used
                                        )
        	                            VALUES
                                        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
        	                            """, vid,
                                             str(key['process_metadata']['name']),
                                             int(key['process_metadata']['pid']),
                                             str(key['process_metadata']['fqdn']),
                                             str(key['process_metadata']['args']),
                                             uid,
                                             gps,
                                             known_seg_tot,
                                             known_seg_start,
                                             known_seg_stop,
                                             active_seg_tot,
                                             active_seg_start,
                                             active_seg_stop,
                                             str(key['process_metadata']['process_start_timestamp']),
                                             str(key['process_metadata']['process_start_timestamp']))
                        except pyodbc.Error as err:
                            # Set HTTP code and log.
                            admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                        else:
                            # Add to inserted insert history list.
                            inserted[history_concat]
                        # Close ODBC cursor.
                        cur.close()
                        del cur

    # Get dictionary of recent processes.
    def get_processes_for_report(self, req_method, full_uri):
        # Init.
        p = {}
        d = {}
        # Instantiate objects.
        admin = Admin.AdminHandle()
        try:
            # Set ODBC cursor.
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT process_id,
                                   process_full_name,
                                   value_txt AS 'username',
                                   dq_flag_ifo,
                                   dq_flag_name,
                                   dq_flag_version,
                                   pid,
                                   fqdn,
                                   process_args,
                                   affected_active_data_segment_total,
                                   affected_active_data_start,
                                   affected_active_data_stop,
                                   affected_known_data_segment_total,
                                   affected_known_data_start,
                                   affected_known_data_stop,
                                   process_time_started,
                                   process_time_last_used
                            FROM tbl_processes
                            LEFT JOIN tbl_values ON tbl_processes.user_fk = tbl_values.value_id
                            LEFT JOIN tbl_dq_flag_versions ON tbl_processes.dq_flag_version_fk = tbl_dq_flag_versions.dq_flag_version_id
                            LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id
                            WHERE process_time_last_used <> 0
                            ORDER BY process_time_last_used DESC, process_time_started DESC
                            LIMIT 50
                            """)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set process dictionary.
                    p[row.process_id] = {
                        "process_full_name" : row.process_full_name,
                        "pid" : row.pid,
                        "username" : row.username,
                        "fqdn" : row.fqdn,
                        "args" : row.process_args,
                        "uri" : self.get_value_detail_from_ID(row.dq_flag_ifo, req_method, full_uri) + "/" + row.dq_flag_name + "/" + str(row.dq_flag_version),
                        "total_active_segments" : row.affected_active_data_segment_total,
                        "earliest_active_segment" : row.affected_active_data_start,
                        "latest_active_segment" : row.affected_active_data_stop,
                        "total_known_segments" : row.affected_known_data_segment_total,
                        "earliest_known_segment" : row.affected_known_data_start,
                        "latest_known_segment" : row.affected_known_data_stop,
                        "process_time_started" : row.process_time_started,
                        "process_time_last_used" : row.process_time_last_used
                    }
        # Include inside named dictionary.
        d['results'] = p
        # Return.
        return d

    #############################
    # SEGMENT HANDLING METHODS #
    ###########################
    
    # Insert segments.
    def insert_segments(self, request, req_method, full_uri, ifo_id, ifo, flag_id, flag, version_id, version, data):
        # Init.
        e = []
        seg_tot = 0
        seg_first_gps = 0
        seg_last_gps = 0
        uid = 0
        inserted = False
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        user = User.UserHandle()
        # Check whether the requested segment type is in the data dictionary.
        if not request in data:
            # Set HTTP code and log.
            e = admin.log_and_set_http_code(400, 11, req_method, None, full_uri)
        else:
            # Get user id.
            uid = user.get_user_id(data['insert_history'][0]['insertion_metadata']['auth_user'], req_method, full_uri)
            # If user ID does not exist.
            if uid == 0:
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(404, 2, req_method, None, full_uri)
            else:
                # Initialise ODBC cursor.
                try:
                    cur = cnxn.cursor()
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(500, 40, req_method, str(err), full_uri)
                else:
                    # Init segment global values.
                    seg_tot = 0
                    seg_first_gps = 0
                    seg_last_gps = 0
                    # Get segments into SQL for insert.
                    sql = ''
                    for k, v in data[request]:
                        # If using sub-second segments.
                        if constant.use_sub_second_segments:
                            # Set,
                            k_sql = '%.5f'%k
                            v_sql = '%.5f'%v
                        # Otherwise, integers.
                        else:
                            k_sql = str(k)
                            v_sql = str(v)                            
                        sql = sql + ',(' + str(version_id) + ',' + k_sql + ',' + v_sql + ')'
                        # Set segment global values.
                        seg_tot += 1
                        seg_first_gps = admin.set_var_if_higher_lower('l', k, seg_first_gps) 
                        seg_last_gps = admin.set_var_if_higher_lower('h', v, seg_last_gps)
                    # If segments exist.
                    if seg_tot != 0:
                        # Remove first delimiter.
                        sql = sql[1:]
                        # Set table to use dependent upon type of insert.
                        tbl = 's'
                        if request == 'known':
                            tbl = '_summary'
                        try:
                            # Insert segment.
                            cur.execute("INSERT INTO tbl_segment" + tbl + " (dq_flag_version_fk, segment_start_time, segment_stop_time) VALUES" + sql)
                        except pyodbc.Error as err:
                            # Set HTTP code and log.
                            admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                        else:
                            # Set inserted.
                            inserted = True
                        # Close ODBC cursor.
                        cur.close()
                        del cur
        # Set return dictionary.
        d = {
             "error_info" : e,
             "seg_tot" : seg_tot,
             "seg_first_gps" : seg_first_gps,
             "seg_last_gps" : seg_last_gps,
             "inserted" : inserted,
             "uid" : uid
            }
        # Return.
        return d

    # Commit transaction to database.
    def commit_transaction_to_db(self):
        # Commit transaction.
        cnxn.commit()

    # Update version segment global values.
    def update_segment_global_values(self, vid, known_tot, known_start, known_stop, active_tot, active_start, active_stop, req_method, full_uri):
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # Initialise ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            # Get GPS time.
            gps = gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs)
            # Attempt to retrieve current totals from database.
            try:
                # Get.
                cur.execute("""
                            SELECT dq_flag_version_known_segment_total AS 'known_tot', dq_flag_version_known_earliest_segment_time AS 'known_earliest', dq_flag_version_known_latest_segment_time AS 'known_latest', dq_flag_version_active_segment_total AS 'active_tot', dq_flag_version_active_earliest_segment_time AS 'active_earliest', dq_flag_version_active_latest_segment_time AS 'active_latest'
                            FROM tbl_dq_flag_versions
                            WHERE dq_flag_version_id=?
                            """, vid)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    known_start = admin.set_var_if_higher_lower('l', known_start, row.known_earliest) 
                    known_stop = admin.set_var_if_higher_lower('h', known_stop, row.known_latest)
                    known_tot = known_tot + row.known_tot
                    active_start = admin.set_var_if_higher_lower('l', active_start, row.active_earliest) 
                    active_stop = admin.set_var_if_higher_lower('h', active_stop, row.active_latest)
                    active_tot = active_tot + row.active_tot
                    # If using sub-second segments.
                    if constant.use_sub_second_segments:
                        # Set,
                        known_start = float(known_start)
                        known_stop = float(known_stop)
                        active_start = float(active_start)
                        active_stop = float(active_stop)
                    # Otherwise, integers.
                    else:
                        # Set,
                        known_start = int(known_start)
                        known_stop = int(known_stop)
                        active_start = int(active_start)
                        active_stop = int(active_stop)
                try:
                    # Update segment global values.
                    cur.execute("""
                                UPDATE tbl_dq_flag_versions
                                SET dq_flag_version_known_segment_total=?, dq_flag_version_known_earliest_segment_time=?, dq_flag_version_known_latest_segment_time=?, dq_flag_version_active_segment_total=?, dq_flag_version_active_earliest_segment_time=?, dq_flag_version_active_latest_segment_time=?, dq_flag_version_date_last_modified=?
                                WHERE dq_flag_version_id=?
                                """, known_tot, known_start, known_stop, active_tot, active_start, active_stop, gps, vid)
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            # Close ODBC cursor.
            cur.close()
            del cur                            

    # Get total number of segments associated to a version.
    def get_flag_version_segment_total(self, request, vid, req_method, full_uri):
        # Init.
        r = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        # Initialise ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get.
                cur.execute("""
                            SELECT dq_flag_version_""" + request + """_segment_total AS 'tot'
                            FROM tbl_dq_flag_versions
                            WHERE dq_flag_version_id=?
                            """, vid)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Loop.
                for row in cur:
                    # Set.
                    r = row.tot
        # Return.
        return r

    # Get specific flag & version segments.
    def get_flag_version_segments(self, request, version_id, t1, t2, req_method, full_uri):
        # Init.
        l = []
        d = {}
        w = ''
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
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
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            # Set table to use dependent upon type of insert.
            tbl = 's'
            if request == 'known':
                tbl = '_summary'
            # If request within acceptable range, i.e. 'active', 'known', etc., get list of all flags over period requested by args.
            if not admin.check_request('seg', request) == False:
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
                try:
                    # Get.
                    cur.execute("""
                                SELECT segment_start_time, segment_stop_time
                                FROM tbl_segment""" + tbl + """
                                """ + w + """
                                ORDER BY segment_start_time""")
                    # Loop.
                    for row in cur:
                        # If using sub-second segments.
                        if constant.use_sub_second_segments:
                            # Set.
                            t1 = float(row.segment_start_time)
                            t2 = float(row.segment_stop_time)
                        # Otherwise, integers.
                        else:
                            # Set.
                            t1 = int(row.segment_start_time)
                            t2 = int(row.segment_stop_time)
                        # Append segments to list.
                        l.append([t1,t2])
                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                # Close ODBC cursor.
                cur.close()
                del cur
        # Insert in request dictionary.
        d[request] = l
        # Return.
        return d
    
    # Get report segments.
    def get_report_segments(self, request, t1, t2, request_array, req_method, full_uri):
        # Init.
        d = {}
        payload = {}
        seg_sql = ''
        w = ''
        pre_v_fk = 0
        i = 0
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # Initialise ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
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
            # Set table to use dependent upon type of insert.
            tbl = 's'
            if request == 'known' or request == 'all':
                tbl = '_summary'
            # If request within acceptable range, i.e. 'active', 'known', etc., get list of all flags over period requested by args.
            if (not admin.check_request('seg', request) == False) or request == 'all':
                # If user is not requesting just the metadata.
                if not 'metadata' in request_array:
                    # Get the segment start/stop fields from the DB.
                    seg_sql = ', segment_start_time, segment_stop_time '
                try:
                    if request == 'all':
                        active_data_dictionary=self.get_active_segments_only(w, seg_sql, req_method, full_uri)
                    # Get.
                    cur.execute("""
                                SELECT dq_flag_name, value_txt AS 'dq_flag_ifo_txt', dq_flag_description, dq_flag_version_comment, dq_flag_active_means_ifo_badness, dq_flag_version_uri, dq_flag_version_deactivated, dq_flag_version, dq_flag_version_fk""" + seg_sql + """
                                FROM
                                (SELECT dq_flag_version_fk""" + seg_sql + """
                                FROM tbl_segment""" + tbl + w + """
                                ORDER BY dq_flag_version_fk) AS t1
                                LEFT JOIN tbl_dq_flag_versions ON t1.dq_flag_version_fk = tbl_dq_flag_versions.dq_flag_version_id
                                LEFT JOIN tbl_dq_flags ON tbl_dq_flag_versions.dq_flag_fk = tbl_dq_flags.dq_flag_id
                                LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
                                """)

                except pyodbc.Error as err:
                    # Set HTTP code and log.
                    admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
                else:
                    # Loop.
                    for row in cur:
                        # If this is a different flag.
                        if not pre_v_fk == row.dq_flag_version_fk:
                            # Increment counter.
                            i = row.dq_flag_version_fk
                            # Get metadata for this flag.
                            payload[i] = admin.get_flag_metadata(row.dq_flag_ifo_txt, row.dq_flag_name, str(row.dq_flag_version), row.dq_flag_description, row.dq_flag_version_comment, row.dq_flag_version_uri, row.dq_flag_version_deactivated, row.dq_flag_active_means_ifo_badness)
                            # If 'known' or 'active' segments or no limitations have been set.
                            if request == 'known' or request == 'active': 
                                # Reset segment list.
                                payload[i][request] = []
                            elif request == 'all': 
                                payload[i]['known']=[]
                                # Append all the active segments into this flag's payload
                                if i in list(active_data_dictionary.keys()):
                                    # Not every flag will have active segments
                                    payload[i]['active']=active_data_dictionary[i]
                        if request == 'all':
                            # If using sub-second segments.
                            if constant.use_sub_second_segments:
                                # Set.
                                t1 = float(row.segment_start_time)
                                t2 = float(row.segment_stop_time)
                            # Otherwise, integers.
                            else:
                                # Set.
                                t1 = int(row.segment_start_time)
                                t2 = int(row.segment_stop_time)
                            payload[i]['known'].append([t1,t2])
                        # If user is not requesting just the metadata.
                        elif not 'metadata' in request_array:
                            # If using sub-second segments.
                            if constant.use_sub_second_segments:
                                # Set.
                                t1 = float(row.segment_start_time)
                                t2 = float(row.segment_stop_time)
                            # Otherwise, integers.
                            else:
                                # Set.
                                t1 = int(row.segment_start_time)
                                t2 = int(row.segment_stop_time)
                            # Append segments to list.
                            payload[i][request].append([t1,t2])
                        # Set previous version FK for use in next loop. 
                        pre_v_fk = row.dq_flag_version_fk
                # Close ODBC cursor.
                cur.close()
                del cur
        # Set in overall dictionary.
        # Fix? for incompatible API change going to 2.1.10
        # Also hack to fix API change that Ryan didn't handle properly in the parseKnown function in the current client release:
        payload_vals=list(payload.values())
        for i,j in enumerate(payload_vals):
            payload_vals[i]['metadata']['comment']=j['metadata']['flag_description']
        d['results'] = payload_vals
        # Return.
        return d

    def get_active_segments_only(self, w, seg_sql, req_method, full_uri):
        """ 
        Function used by /report/all to get the active segments.
        Returns a dictionary with keys of dq_flag_version_fk and buckets
        containing the active flags for that flag_version_fk in a list.
        """
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # Initialise ODBC cursor.
        try:
            cur = cnxn.cursor()
        except pyodbc.Error as err:
            # Set HTTP code and log.
            admin.log_and_set_http_code(0, 40, req_method, str(err), full_uri)
        else:
            try:
                # Get active segments and flag_version_fk.
                # w = ' segment_stop_time >= ' + t1 + ' AND segment_start_time <= ' + t2
                # w = ' WHERE ' + w
                # seg_sql = ', segment_start_time, segment_stop_time ' 
                cur.execute("""
                           SELECT dq_flag_version_fk""" + seg_sql + """
                           FROM tbl_segments""" + w + """
                           ORDER BY dq_flag_version_fk
                           """)
            except pyodbc.Error as err:
                # Set HTTP code and log.
                admin.log_and_set_http_code(0, 41, req_method, str(err), full_uri)
            else:
                # Define output.
                output = {}
                # Loop.
                for row in cur:
                    i = row.dq_flag_version_fk
                    if i not in list(output.keys()):
                        output[i] = []
                    # If using sub-second segments.
                    if constant.use_sub_second_segments:
                        # Set.
                        t1 = float(row.segment_start_time)
                        t2 = float(row.segment_stop_time)
                    # Otherwise, integers.
                    else:
                        t1 = int(row.segment_start_time)
                        t2 = int(row.segment_stop_time)
                    # Append segments to list.  
                    output[i].append([t1,t2])
            # Close ODBC cursor.
            cur.close()
            del cur
        # Return.
        return output
