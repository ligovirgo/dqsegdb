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
DQSEGDB Regression Test Suite
Utility function-handling class file
'''
# Import.
import json
import logging

# attempt at Python 2/Python 3 compatibility; there is a related change
#   in the call that was to urllib2 later
#import urllib2
try:
    # this should work in P2 but not P3
    from urllib2 import urlopen
except ImportError as error:
    # this should work in P3 (and P2, but we probably (?) don't want it to)
    from urllib.request import urlopen

# Instantiate logger.
log = logging.getLogger(__name__)

class UtilHandle:

    # Convert a URI-returned JSON payload to a Python dictionary. Args: Test Name, URI.
    def convert_uri_json_response_to_dict(self, n, uri):
        # Init.
        resp_dict = {'r' : False, 'm' : '', 'd' : {}}
        # Attempt to open url.
        try:
            # attempt at P2/P3 compatibility; see import statements
            #response = urllib2.urlopen(uri)
            response = urlopen(uri)
        except:
            # Log event.
            resp_dict['m'] = 'Unable to complete ' + n + ': ' + uri
            log.error(resp_dict['m'])
        else:
            # Attempt to read response.
            try:
                payload = response.read()
            except:
                # Log event.
                resp_dict['m'] = 'Unable to read payload returned by ' + n + ': ' + uri
                log.error(resp_dict['m'])
            else:
                # Attempt to convert JSON to dict.
                try:
                    resp_dict['d'] = json.loads(payload)
                except:
                    # Log event.
                    resp_dict['m'] = 'Unable to convert payload returned by ' + n + ': ' + uri
                    log.error(resp_dict['m'])
                # Otherwise, all OK.
                else:
                    resp_dict['r'] = True
        # Return.
        return resp_dict
