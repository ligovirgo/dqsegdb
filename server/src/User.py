'''
DQSEGDB Python Server
User handling class file
'''

# Import.
import DAO

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