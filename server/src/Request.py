'''
DQSEGDB Python Server
URI + HTTP request management class file
'''

# Import.
import Admin
import DAO
import json
import time
from urlparse import urlparse, parse_qs #Re-named urllib.parse as of #3.x

class RequestHandle():
    # Decide which GET URI to serve.
    def serve_get_uri(self, req_method, full_uri, script_url, qs):
        # Init.
        r = {}
        e = []
        t1 = None
        t2 = None
        request_array = []
        meta = []
        a_segs = []
        k_segs = []
        i_hist = []
        arg = []
        # Instantiate objects.
        admin = Admin.AdminHandle()
        dao = DAO.DAOHandle()
        # If trailing slash found.
        if admin.check_for_last_str_char(full_uri, '/'):
            # Set HTTP code and log.
            e = admin.log_and_set_http_code(400, 16, req_method, None, full_uri)
        # Otherwise, trailing slash not found at end of URI.
        else:
            # Get server request timestamp.
            server_start_time = time.time()
            # Split the script URL to a list.
            o = script_url.split('/')
            # Filter out empty values.
            f = filter(None, o)
            # Get list size.
            l = len(f)
            # Start serving requests.
            if f[0] == 'dq':
                # Get ifo list.
                if l == 1:
                    r = dao.get_value_list(1, req_method, full_uri)
                    # If list not supplied.
                    if not r:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(200, 21, req_method, None, full_uri)
                # Otherwise, prepare more complex requests.
                elif l > 1:
                    ifo = f[1]
                    ifo_id = dao.get_value_details(1,ifo, req_method, full_uri) 
                    # Check IFO exists in database.
                    if ifo_id == None:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(404, 5, req_method, None, full_uri)
                    else:
                        # Get flag list.
                        if l == 2:
                            r = dao.get_flag_list(ifo, req_method, full_uri)
                            # If list not supplied.
                            if not r:
                                # Set HTTP code and log.
                                admin.log_and_set_http_code(200, 22, req_method, None, full_uri)
                        # Otherwise, prepare more complex requests.
                        elif l > 2:
                            flag = f[2]
                            flag_id = dao.get_flag_id(ifo_id, flag, req_method, full_uri)
                            # If flag does not exist in database.
                            if flag_id == None:
                                # Set HTTP code and log.
                                e = admin.log_and_set_http_code(404, 8, req_method, None, full_uri)
                            else:
                                # If three URI array elements supplied.
                                if l == 3:
                                    # Get version list.
                                    v_l = dao.get_flag_version_list(ifo, flag, req_method, full_uri)
                                    # If list not supplied.
                                    if not v_l:
                                        # Set HTTP code and log.
                                        e = admin.log_and_set_http_code(409, 38, req_method, None, full_uri)
                                    # Otherwise.
                                    else:
                                        # Put list into response dictionary.
                                        r = admin.put_version_list_into_dict(v_l)
                                # Otherwise, get version and segment info. Ensuring URI is not ended with a trailing slash.
                                elif l == 4:
                                    version = f[3]
                                    # If query string being passed.
                                    if qs:
                                        arg = parse_qs(urlparse(full_uri).query)
        #                               print 'Args as tuples: [%s]' % ', '.join(map(str, arg))
                                        # If include exists.
                                        try:
                                            arg['include']
                                        except:
                                            pass
                                        else:
                                            request_array = arg['include'][0].split(',')
                                        # Get t1 and t2.
                                        try:
                                            arg['s'][0]
                                        except:
                                            pass
                                        else:
                                            t1 = arg['s'][0]
                                        try:
                                            arg['e'][0]
                                        except:
                                            pass
                                        else:
                                            t2 = arg['e'][0]
                                    # Get version ID.
                                    version_id = dao.get_flag_version_id(flag_id, version, req_method, full_uri)
                                    # If version ID found.
                                    if version_id == None:
                                        # Set HTTP code and log.
                                        e = admin.log_and_set_http_code(404, 10, req_method, None, full_uri)
                                    else:
                                        # If metadata or everything included.
                                        if 'metadata' in request_array or not request_array:
                                            # Get metadata.
                                            meta = dao.get_flag_version_metadata('metadata', ifo, flag, version, version_id, req_method, full_uri)
                                            # If metadata not built.
                                            if not meta:
                                                # Set HTTP code and log.
                                                e = admin.log_and_set_http_code(404, 24, req_method, None, full_uri)
                                        # If 'active' segments or everything included.
                                        if 'active' in request_array or not request_array:
                                            # Get segments.
                                            a_segs = dao.get_flag_version_segments('active', version_id, t1, t2, req_method, full_uri)
                                        # If 'known' segments or everything included.
                                        if 'known' in request_array or not request_array:
                                            # Get segments.
                                            k_segs = dao.get_flag_version_segments('known', version_id, t1, t2, req_method, full_uri)
                                        # If insert history or everything included.
                                        if 'insert_history' in request_array or not request_array:
                                            # Get insert history.
                                            i_hist = dao.get_flag_version_insert_history(version_id, req_method, full_uri)
                                            # If insert history not built.
                                            if not i_hist:
                                                # Set HTTP code and log.
                                                e = admin.log_and_set_http_code(404, 25, req_method, None, full_uri)
                                        # Set segments as result so far, with any insert history that has been set.
                                        r.update(meta)
                                        r.update(k_segs)
                                        r.update(a_segs)
                                        r.update(i_hist)
                                # Otherwise, request is too long.
                                elif l > 4:
                                    # Set HTTP code and log.
                                    e = admin.log_and_set_http_code(414, 19, req_method, None, full_uri)
            # Reports.
            elif f[0] == 'report':
                # Get report options.
                if l == 1:
                    r = admin.get_available_resources(req_method, full_uri)
                    # If dictionary not supplied.
                    if not r:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(404, 26, req_method, None, full_uri)
                # Otherwise, prepare more complex requests. Ensuring URI is not ended with a trailing slash.
                elif l > 1:
                    request = f[1]
                    if l == 2:
                        # If request is flags.
                        if request == 'flags':
                            # Get list of all flags.
                            r = dao.get_flags_with_versions_for_report(req_method, full_uri)
                            # If dictionary not supplied.
                            if not r:
                                # Set HTTP code and log.
                                admin.log_and_set_http_code(200, 27, req_method, None, full_uri)
                        # If request is coverage.
                        elif request == 'coverage':
                            # Get list of all flags.
                            r = dao.get_flag_version_coverage(req_method, full_uri)
                            # If dictionary not supplied.
                            if not r:
                                # Set HTTP code and log.
                                admin.log_and_set_http_code(200, 42, req_method, None, full_uri)
                        # If request is db.
                        elif request == 'db':
                            # Get DB-related statistics.
                            r = admin.get_db_statistics_payload(None, req_method, full_uri)
                            # If dictionary not supplied.
                            if not r:
                                # Set HTTP code and log.
                                admin.log_and_set_http_code(200, 39, req_method, None, full_uri)
                        # If request within acceptable range, i.e. 'active', 'known', etc., get list of all flags over period requested by args.
                        elif admin.check_request('seg', request) == False:
                            # Set HTTP code and log.
                            e = admin.log_and_set_http_code(404, 11, req_method, None, full_uri)
                        # Otherwise, it must be 'known' or 'active'.
                        else:
                            # If query string being passed.
                            if qs:
                                arg = parse_qs(urlparse(full_uri).query)
                                # If include exists.
                                try:
                                    arg['include']
                                except:
                                    pass
                                else:
                                    request_array = arg['include'][0].split(',')
                                # Get t1 and t2.
                                try:
                                    arg['s'][0]
                                except:
                                    pass
                                else:
                                    t1 = arg['s'][0]
                                try:
                                    arg['e'][0]
                                except:
                                    pass
                                else:
                                    t2 = arg['e'][0]
                            # Get report segments.
                            r = dao.get_report_segments(request, t1, t2, request_array, req_method, full_uri)
                            # If no segments supplied.
                            if not r:
                                # Set HTTP code and log.
                                admin.log_and_set_http_code(200, 28, req_method, None, full_uri)
                    # Otherwise, if handling DB-statistics request.
                    elif l == 3:
                        # Report error if not in report.
                        if not request == 'db':
                            # Set HTTP code and log.
                            admin.log_and_set_http_code(200, 13, req_method, None, full_uri)
                        else:
                            # Get IFO id.
                            ifo = f[2]
                            ifo_id = dao.get_value_details(1, ifo, req_method, full_uri) 
                            # Check IFO exists in database.
                            if ifo_id == None:
                                # Set HTTP code and log.
                                e = admin.log_and_set_http_code(404, 5, req_method, None, full_uri)
                            else:
                                # Get DB-related statistics for this IFO.
                                r = admin.get_db_statistics_payload(ifo_id, req_method, full_uri)                            
                    # Otherwise, request is too long.
                    elif l > 3:
                        # Set HTTP code and log.
                        e = admin.log_and_set_http_code(414, 19, req_method, None, full_uri)
        # If results have been found and there are no errors.
        if r and not e:
            # Add query info to results.
            r.update(admin.add_query_info_to_flag_resource(full_uri, r, t1, t2, request_array, server_start_time))
            # Encode final dictionary to JSON.
            r = json.dumps(r)
            # Incorporate into list to pass back to application.
            r = ['200 OK', r]
            # Set HTTP code and log.
            admin.log_and_set_http_code(200, 4, req_method, None, full_uri)
        # Otherwise, if errors have been found.
        elif e:
            # Set the reply as an error.
            r = e
        # Otherwise, complete error.
        else:
            # Set HTTP code and log.
            r = admin.log_and_set_http_code(404, 20, req_method, None, full_uri)
        # Return content.
        return r
    
    # Decide which PUT or PATCH URI to serve.
    def serve_put_or_patch_uri(self, req_method, full_uri, script_url, qs, j):
        # Init.
        r = {}
        e = []
        request_array = []
        # Instantiate objects.
        admin = Admin.AdminHandle()
        dao = DAO.DAOHandle()
        # If trailing slash found.
        if admin.check_for_last_str_char(full_uri, '/'):
            # Set HTTP code and log.
            e = admin.log_and_set_http_code(400, 16, req_method, None, full_uri)
        # Otherwise, trailing slash not found at end of URI.
        else:
            # Load JSON to array.
            try:
                a = json.loads(j)
            except:
                # Set HTTP code and log.
                e = admin.log_and_set_http_code(400, 1, req_method, None, full_uri)
            else:
                # Check the payload.
                payload_check = admin.check_json_payload(a, req_method)
                # If problem found.
                if payload_check:
                    # Set HTTP code and log.
                    e = admin.log_and_set_http_code(400, 33, req_method, str(payload_check), full_uri)
                else:
                    # Get server request timestamp.
                    server_start_time = time.time()
                    # Split the script URL to a list.
                    o = script_url.split('/')
                    # Filter out empty values.
                    f = filter(None, o)
                    # Get list size.
                    l = len(f)
                    # Start serving requests.
                    if l > 2:
                        ifo = f[1]
                        ifo_id = dao.get_value_details(1, ifo, req_method, full_uri)
                        # If IFO does not exist.
                        if ifo_id == None:
                            # Set HTTP code and log.
                            e = admin.log_and_set_http_code(404, 5, req_method, None, full_uri)
                        else:
                            flag = f[2]
                            # Add query info to passed JSON.
                            a.update(admin.add_query_info_to_flag_resource(full_uri, a, 0, 0, request_array, server_start_time))
                            # Put new flag.
                            if l == 3:
                                # If PUT.
                                if req_method == 'PUT':
                                    e = dao.insert_flag(req_method, full_uri, ifo_id, ifo, flag, a)
                                else:
                                    # Set HTTP code and log.
                                    e = admin.log_and_set_http_code(400, 31, req_method, None, full_uri)
                            # Otherwise, prepare more complex requests.
                            if l > 3:
                                # Set version.
                                version = f[3]
                                # Get flag ID.
                                flag_id = dao.get_flag_id(ifo_id, flag, req_method, full_uri)
                                # If flag ID does not exist.
                                if flag_id == None:
                                    # Set HTTP code and log.
                                    e = admin.log_and_set_http_code(404, 8, req_method, None, full_uri)
                                else:
                                    # Insert version.
                                    if l == 4:
                                        # If PUT.
                                        if req_method == 'PUT':
                                            # Insert new version.
                                            e = dao.insert_flag_version(req_method, full_uri, ifo_id, ifo, flag_id, flag, version, a)
                                        # Get version ID.
                                        version_id = dao.get_flag_version_id(flag_id, version, req_method, full_uri)
                                        # If version does not exist.
                                        if version_id == None:
                                            # Set HTTP code and log.
                                            e = admin.log_and_set_http_code(404, 10, req_method, None, full_uri)
                                        else:
                                            # If putting and this version already has Known segments associated to it.
                                            if req_method == 'PUT' and dao.get_flag_version_segment_total('known', version_id, req_method, full_uri) > 0:
                                                # Set HTTP code and log.
                                                e = admin.log_and_set_http_code(400, 18, req_method, None, full_uri)
                                            else:
                                                # Put new 'known' segments.
                                                e = dao.insert_segments('known', req_method, full_uri, ifo_id, ifo, flag_id, flag, version_id, version, a)
                                                # Put new 'active' segments.
                                                e = dao.insert_segments('active', req_method, full_uri, ifo_id, ifo, flag_id, flag, version_id, version, a)
                                                # Commit the transaction to the DB.
                                                dao.commit_transaction_to_db()
                                    # Otherwise, URI too long.                
                                    elif l > 4:
                                        # Set HTTP code and log.
                                        e = admin.log_and_set_http_code(414, 19, req_method, None, full_uri)
        # If errors have been found.
        if e:
            # Set the reply as an error.
            r = e
        # Otherwise, set as completed.
        else:
            # Set HTTP code and log.
            r = admin.log_and_set_http_code(200, 4, req_method, None, full_uri)
        # Return content.
        return r
