'''
DQSEGDB Python Server
Administrative task handling class file
'''

# Import.
import Constants
import DAO
import gpstime
import logging
import Logging_Config
import os
import re
import socket
import time

# Instantiate logger.
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class AdminHandle:
    
    # Get flag metadata.
    def get_flag_metadata(self, ifo, flag, version, comment, uri, deactivated, badness):
        # Init.
        a = []
        # If Ifo, flag and version passed.
        if not ifo == None and not flag == None and not version == None:
#            a = ['here']
            # Build dictionary.
            a = {"ifo" : ifo,
                "name" : flag,
                 "version" : int(version),
                 "metadata" : {"comment" : comment,
                               "provenance_url" : uri,
                               "deactivated" : bool(deactivated),
                               "active_indicates_ifo_badness" : bool(badness)}}
        # Return.
        return a

    # Convert a boolean value to an integer.
    def convert_boolean_to_int(self, v):
        # Init.
        r = 0
        # If value passed.
        try:
            v
        except:
            pass
        else:
            # If True.
            if v == True or v == "true":
                r = 1
        # Return.
        return r

    # Add query information to results. # r CAN BE REMOVED FROM PASSED ARGS. 20131107
    def add_query_info_to_flag_resource(self, u, r, t1, t2, request_array, server_start_time):
        # Init.
        a = {}
        seqt = 0
        # If URI passed.
        try:
            u
        except:
            pass
        else:
            # Set times.
            if not t1 != None:
                t1 = 0
            if not t2 != None:
                t2 = 0
            # Instantiate objects.
            constant = Constants.ConstantsHandle()
            # If server elapsed query time passed.
            if not server_start_time == 0: 
                seqt = time.time() - server_start_time
                seqt = round(seqt,5)
            # Put the information together.
            a = {"query_information" : {"uri" : u,
                                        "server_timestamp" : gpstime.GpsSecondsFromPyUTC(time.time(), constant.gps_leap_secs),
                                        "server_elapsed_query_time" : seqt,
                                        "server" : socket.gethostname(),
                                        "server_code_version" : constant.py_server_version,
                                        "api_version" : constant.api_version,
                                        "start" : t1,
                                        "end" : t2,
                                        "include" : request_array}}
        # Return.
        return a
   
    # Check if a request made by a user is of a valid type.
    def check_request(self, t, r):
        # Init.
        res = False
        # If args passed.
        try:
            t, r
        except:
            pass
        else:
            # Instantiate objects.
            constant = Constants.ConstantsHandle()
            # If segment request.
            if t == 'seg':
                # Check if the request type is available.
                if r in constant.segment_requests:
                    # Set.
                    res = True
            # Otherwise, if a metadata-type request.
            elif t == 'meta':
                # Check if the request type is available.
                if r in constant.metadata_requests:
                    # Set.
                    res = True
        # Return.
        return res
    
    # Check JSON payload.
    def check_json_payload(self, j, req_method):
        # Get expected JSON payload definition.
        p = self.get_expected_json_payload(req_method)
        # Compare the two dictionaries.
        a = self.diff_dict(j, p)
        # Return.
        return a
    
    # Compare two dictionaries.
    def diff_dict(self, j, p):
        # If both are of dictionary type.
        if isinstance(j, dict) and isinstance(p, dict):
            # Init.
            a = {}
            # Loop payload definition.
            for key, value in p.iteritems():
                # Set.
                add_to_dict = False
                # If nested dictionary.
                if isinstance(value, dict):
                    # Go again.
                    inner_dict = self.diff_dict(j[key], p[key])
                    # If inner dictionary is not empty.
                    if inner_dict != {}:
                        # Add to test loop dictionary.
                        a[key] = {}
                        a[key].update(inner_dict)
                # Otherwise, if not dictionary type.
                else:
                    # If the expected key does not exist in the passed payload. 
                    if not j.has_key(key):
                        a[key] = 'MISSING' 
                    else:
                        # If the supplied element type is different to that expected. 
                        if not type(j[key]) == type(p[key]):
                            # If a string is expected.
                            if type(p[key]) == str:
                                # If passed type is incorrect.
                                if not type(j[key]) in [str, unicode]:
                                    # Set.
                                    add_to_dict = True
                            # If expecting Boolean.
                            elif type(p[key]) == bool:
                                # If passed type is incorrect.
                                if not str(type(j[key]))[7:-2] == 'NoneType':
                                    # Set.
                                    add_to_dict = True
                            # Otherwise, all other types. 
                            else:
                                # Set.
                                add_to_dict = True
                            # If adding to dictionary.
                            if add_to_dict:
                                a[key] = 'Wrong type used: ' + str(type(j[key]))[7:-2] + '. Expecting: ' + str(type(p[key]))[7:-2]
#                        a[key] = 'YES' 
            # Return.
            return a
    
    # Get expected JSON payload definition.
    def get_expected_json_payload(self, req_method):
        # Define expected payload.
        d = {
                "ifo" : '',
                "name" : '',
                "version" : 0,
                "known" : [],
                "active" : [],
                "insert_history" : [{
                    "insertion_metadata" : {
                        "uri" : '',
                        "timestamp" : 0,
                        "auth_user" : ''
                    },
                    "process_metadata" : {
                        "pid" : 0,
                        "name" : '',
                        "args" : [],
                        "fqdn" : '',
                        "uid" : '',
                        "process_start_timestamp": 0
                    }
                }]
             }
        # If PUTting.
        if req_method == 'PUT':
            # Add required metadata dictionary.
            d.update({
                      "metadata" : {
                                    "flag_comment" : '',
                                    "version_comment" : '',
                                    "provenance_url" : '',
                                    "deactivated" : False,
                                    "active_indicates_ifo_badness" : False
                                    }
                      })
        # Return.
        return d

    # Log event and set the required HTTP error code.
    def log_and_set_http_code(self, code, state, req_method, add_info, uri):
        # Init.
        r = []
        # If args passed.
        try:
            code, state, req_method, uri
        except:
            pass
        else:
            # Get event state dictionary.
            d = self.get_log_state_dictionary()
            # Get HTTP state dictionary.
            h = self.get_http_state_dictionary()
            # If additional information has been sent, add it within parentheses.
            if add_info:
                add_info = ' (' + add_info + ') '
            else:
                add_info = ''
            # Set group and message info.
            log_group = d[state][0]
            log_message = req_method + ' ' + uri + ' - ' + str(d[state][1]) + add_info
            # If reply exists, but this is just logging.
            if log_group == 0:
                log.info(log_message)
            # Otherwise, if reply exists, but debug.
            elif log_group == 1:
                log.debug(log_message)
            # Otherwise, if reply exists, but warning.
            elif log_group == 2:
                log.warning(log_message)
            # Otherwise, if reply exists, but error.
            elif log_group == 3:
                log.error(log_message)
            # Otherwise, if reply exists, but critical.
            elif log_group == 4:
                log.critical(log_message)
            # Set list.
            r = [str(code) + ' ' + h[code], log_message]
            
        # Return.
        return r
    
    # Get the event state dictionary used by the logger
    def get_log_state_dictionary(self):
        # Set dictionary.
        log_state_dictionary = {
                                    0: [0, 'Attempt made'],
                                    1: [3, 'JSON decode error'],
                                    2: [2, 'Unrecognised user'],
                                    3: [4, 'Problem with ODBC connection'],
                                    4: [0, 'Completed successfully'],
                                    5: [2, 'IFO does not exist in the database'],
                                    6: [2, 'Flag already exists in the database'],
                                    7: [1, 'Flag version already exists in the database'],
                                    8: [2, 'Flag does not exist in the database'],
                                    10: [2, 'Flag version does not exist in the database'],
                                    11: [1, 'Request not within acceptable range, i.e. \'active\', \'known\', etc.'],
                                    12: [1, 'No segments to upload'],
                                    13: [2, 'Requested resource unavailable'],
                                    14: [0, 'Not in this request'],
                                    15: [2, 'Problem writing/retrieving flag version from database'],
                                    16: [2, 'Trailing slash found in requested URI'],
                                    17: [1, 'Args not correctly passed to function'],
                                    18: [2, 'Segments already associated to this flag version. Use PATCH method to append'],
                                    19: [2, 'Too many resources in request URI'],
                                    20: [4, 'Attempt unsuccessful'],
                                    21: [2, 'No IFOs available'],
                                    22: [1, 'No flags available for this IFO'],
                                    23: [1, 'No versions available for this flag'],
                                    24: [2, 'Flag metadata not built correctly'],
                                    25: [2, 'Flag version insertion history not built correctly'],
                                    26: [2, 'Available resources dictionary not built correctly'],
                                    27: [2, 'IFO, flag and version dictionary not available'],
                                    28: [1, 'No segments available'],
                                    29: [3, 'Flag version not correctly inserted to the database'],
                                    30: [3, 'Flag not correctly inserted to the database'],
                                    31: [2, 'Incorrect use of HTTP PATCH method. Use PUT'],
                                    32: [0, 'ODBC connection successful'],
                                    33: [2, 'JSON payload element problem: '],
                                    34: [1, 'Segments to upload'],
                                    35: [3, 'Authentication failure'],
                                    36: [3, 'Authorisation failure']
                                }
        # Return.
        return log_state_dictionary

    # Get the HTTP state dictionary used by the logger
    def get_http_state_dictionary(self):
        # Set dictionary.
        http_state_dictionary = {
                                    200: 'OK',
                                    400: 'Bad Request',
                                    401: 'Unauthorized',
                                    404: 'Not Found',
                                    414: 'Request-URI Too Long'
                                }
        # Return.
        return http_state_dictionary

    # Get HTTP error message for display.
    def get_http_msg_for_display(self, code, error):
        # Init.
        r = ''
        # If args passed.
        try:
            code, error
        except:
            pass
        else:
            r = '<h1>' + str(code) + '</h1>\n'
            r += "<p>" + error + "</p>\n"
        # Return.
        return r

    # Set an integer if it is higher/lower than another passed variable.
    def set_var_if_higher_lower(self, hl, v1, v2):
        # Init.
        r = v2
        # If args passed.
        try:
            hl, v1, v2
        except:
            pass
        else:
            # If higher or lower.
            if ((hl == 'h' and v1 > v2) or (hl == 'l' and (v1 < v2 or v2 == 0))):
                # Set.
                r = v1
        # Return.
        return r
    
    # Check for last string character.
    def check_for_last_str_char(self, s, c):
        # Init.
        r = False;
        # If args passed.
        try:
            s, c
        except:
            pass
        else:
            # If last character matches passed character.
            if s[::-1][0] == c:
                # Set.
                r = True;
        # Return.
        return r
    
    # Get a list of available resources.
    def get_available_resources(self):
        # Set resource array.
        a = {"results" : ['/report/flags', '/report/known']}
        # Return.
        return a