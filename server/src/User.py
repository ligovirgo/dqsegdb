'''
DQSEGDB Python Server
User handling class file
'''

# Import.
import Admin
import Constants
import DAO
import pprint

class UserHandle:

    # Get a user ID, inserting the username to the database if necessary.
    def get_user_id(self,u):
        # Instantiate objects.
        dao = DAO.DAOHandle()
        # Init.
        i = 0
        # Attempt to get ID.
        try:
            i = dao.get_value_details(2, u)
        except:
            pass
        # If ID has not been found.
        if i == None or i == 0:
            # Attempt username insert.
            try:
                dao.insert_user(u)
            except:
                pass
            else:
                # Retrieve ID.
                i = dao.get_value_details(2, u)
        # Return.
        return i
    
    # Check authorisation against a Grid Map-file.
    def gridmap_authentication_authorisation(self, environ, req_method, full_uri, authorise):
        # Instantiate objects.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # If using HTTP.
        if not constant.use_https:
            # Set result to OK and carry on.
            r = [200]
        # Otherwise, using HTTPS.
        else:
            # Init.
            r = [401]
            subject = None
            # Determine which error log status code to call.
            if authorise:
                c = 36
            else:
                c = 35
            # If SSL being used.
            try:
                environ['SSL_CLIENT_S_DN']
            except:
                # Set HTTP code and log.
                r = admin.log_and_set_http_code(401, c, req_method, 'SSL client subject DN not found. Check if using HTTPS', full_uri)
            else:
                # Get subject.
                try:
                    subject = environ['SSL_CLIENT_S_DN']
                    r = admin.log_and_set_http_code(400, 37, environ['REQUEST_METHOD'], subject, environ['REQUEST_URI'])
                except:
                    # Set HTTP code and log.
                    r = admin.log_and_set_http_code(401, c, req_method, 'SSL client subject unreadable', full_uri)
                else:
                    # Get GridMap file authentication location.
                    if not authorise:
                        mf = constant.grid_map_get_file
                    # Get GridMap file authorisation location.
                    else:
                        mf = constant.grid_map_put_patch_file
                    try:
                        # Open file.
                        f = open(mf, 'r')
                    except:
                        # Add unable to open file msg.
                        r = admin.log_and_set_http_code(401, c, req_method, 'Unable to open Grid map file', full_uri)
                    else:
                        # Loop through file lines.
                        for l in f:
                            # Split the line.
                            ls = l.split('"')
                            # If subject exists in GridMap file
                            if ls[1] == subject:
                                r = [200]
                        # If certificate subject not found in GridMap file
                        if not r[0] == 200:
                            # Set HTTP code and log.
                            r = admin.log_and_set_http_code(401, c, req_method, 'Certificate subject DN not found in GridMap file', full_uri)
                        # Close file.
                        f.close()
        # Return.
        return r