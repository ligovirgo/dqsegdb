'''
DQSEGDB Python Server
User handling class file
'''

# Import.
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
    def gridmap_authentication_authorisation(self, environ, authorise):
        # Init.
        a = False
        subject = None
        # Instantiate objects.
        constant = Constants.ConstantsHandle()
        # If SSL being used.
        try:
            environ['SSL_CLIENT_S_DN']
        except:
            pass
        else:
            # Get subject.
            try:
                subject = environ['SSL_CLIENT_S_DN']
            except:
                pass
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
                    pass
                else:
                    # Loop through file lines.
                    for l in f:
                        # Split the line.
                        ls = l.split('"')
                        # If subject exists in GridMap file
                        if ls[1] == subject:
                            #pprint.pprint(subject + ' - ' + ls[1])
                            a = True
                    # Close file.
                    f.close()
            return a