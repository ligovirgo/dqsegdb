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
User handling class file
'''

# Import.
import DAO

class UserHandle:

    # Get a user ID, inserting the username to the database if necessary.
    def get_user_id(self, u, req_method, full_uri):
        # Instantiate objects.
        dao = DAO.DAOHandle()
        # Init.
        i = 0
        # Attempt to get ID.
        try:
            i = dao.get_value_details(2, u, req_method, full_uri)
        except:
            pass
        # If ID has not been found.
        if i == None or i == 0:
            # Attempt username insert.
            try:
                dao.insert_user(u, req_method, full_uri)
            except:
                pass
            else:
                # Retrieve ID.
                i = dao.get_value_details(2, u, req_method, full_uri)
        # Return.
        return i