'''
DQSEGDB Regression Test Suite
Utility function-handling class file
'''
# Import.
import json
import logging
import urllib2

# Instantiate logger.
log = logging.getLogger(__name__)

class UtilHandle:

    # Convert a URI-returned JSON payload to a Python dictionary. Args: Test Name, URI.
    def convert_uri_json_response_to_dict(self, n, uri):
        # Init.
        resp_dict = {'r' : False, 'm' : '', 'd' : {}}
        # Attempt to open url.
        try:
            response = urllib2.urlopen(uri)
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