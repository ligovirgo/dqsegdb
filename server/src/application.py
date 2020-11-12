# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.
# Written by Ryan Fisher, Gary Hemming, and Duncan Brown. 
# See the NOTICE file distributed with this work for additional information regarding copyright ownership.
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
Applcation class file
'''
# Import.
import Admin
import Constants
import DAO
import Request
import LDBDWAuth
import logging
import time

def application(environ, start_response):
    # Instantiate logger.
    constant = Constants.ConstantsHandle()
    logging.basicConfig(filename=constant.log_file_location + time.strftime("%Y-%m-%d",
                        time.localtime()) + '.log', format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.DEBUG)
    # Instantiate objects.
    admin = Admin.AdminHandle()
    dao = DAO.DAOHandle()
    reqhan = Request.RequestHandle()
    ldbdsauth = LDBDWAuth.SciTokensAuthorization()
    ldbdwauth = LDBDWAuth.GridmapAuthorization()
    # Set HTTP code and log.
    res = admin.log_and_set_http_code(400, 0, environ['REQUEST_METHOD'], None, environ['REQUEST_URI'])
    # Connect to DB.
    if dao.connect_to_db(environ['REQUEST_METHOD'], environ['REQUEST_URI']):
        # Respond to a GET request.
        if environ['REQUEST_METHOD'] == 'GET':
            # Authenticate.
            try:
                res = ldbdsauth.check_authorization_scitoken(environ, environ['REQUEST_METHOD'], environ['REQUEST_URI'], False)
            except:
                res = ldbdwauth.check_authorization_gridmap(environ, environ['REQUEST_METHOD'], environ['REQUEST_URI'], False)
            # If authentication successful.
            if res[0] == 200:
                # Get content for output.
                res = reqhan.serve_get_uri(environ['REQUEST_METHOD'], environ['REQUEST_URI'], environ['PATH_INFO'], environ['QUERY_STRING'])
        # Respond to a PUT request.
        elif environ['REQUEST_METHOD'] == 'PUT' or environ['REQUEST_METHOD'] == 'PATCH':
            # Authorise.
            try:
                res = ldbdsauth.check_authorization_scitoken(environ, environ['REQUEST_METHOD'], environ['REQUEST_URI'], True)
            except:
                res = ldbdwauth.check_authorization_gridmap(environ, environ['REQUEST_METHOD'], environ['REQUEST_URI'], True)
            # If authorisation successful.
            if res[0] == 200:
                # Get the size of the requested JSON.
                try:
                    request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                except:
                    request_body_size = 0
                # Process PUT or PATCH request.
                res = reqhan.serve_put_or_patch_uri(environ['REQUEST_METHOD'], environ['REQUEST_URI'], environ['PATH_INFO'], environ['QUERY_STRING'], environ['wsgi.input'].read(request_body_size))
    # Check first character to check content is Python dictionary converted to JSON.
    if not res[1][:1] == '{':
        # Handle error.
        content_type = 'text/html'
        res[1] = admin.get_http_msg_for_display(res[0], res[1])
    else:
        content_type = 'application/json'
    # Set headers.
    response_headers = [('Content-type', content_type),
                        ('Content-Length', str(len(res[1])))]
    # Start response - Status / Headers.
    start_response(res[0], response_headers)
    # Return.
    return [res[1]]
