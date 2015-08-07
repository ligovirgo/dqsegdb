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
    ldbdwauth = LDBDWAuth.GridmapAuthorization()
    # Set HTTP code and log.
    res = admin.log_and_set_http_code(400, 0, environ['REQUEST_METHOD'], None, environ['REQUEST_URI'])
    # Connect to DB.
    if dao.connect_to_db(environ['REQUEST_METHOD'], environ['REQUEST_URI']):
        # Respond to a GET request.
        if environ['REQUEST_METHOD'] == 'GET':
            # Authenticate.
            res = ldbdwauth.check_authorization_gridmap(environ, environ['REQUEST_METHOD'], environ['REQUEST_URI'], False)
            # If authentication successful.
            if res[0] == 200:
                # Get content for output.
                res = reqhan.serve_get_uri(environ['REQUEST_METHOD'], environ['REQUEST_URI'], environ['PATH_INFO'], environ['QUERY_STRING'])
        # Respond to a PUT request.
        elif environ['REQUEST_METHOD'] == 'PUT' or environ['REQUEST_METHOD'] == 'PATCH':
            # Authorise.
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