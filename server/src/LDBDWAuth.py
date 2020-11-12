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
Grid mapfile authentication and authorisation class.
'''

# Import.
import os
import Admin
import Constants
import exceptions
import M2Crypto
import re
import scitokens

class GridMapError(exceptions.Exception):
    """
    Raised for errors in GridMap class
    """
    pass

class GridMap(dict):
    """
    """
    def __init__(self, path=None):
        """
        """        
        self.path = path
        # initialize the base class
        dict.__init__(self)

        if not path:
            msg = "No path for grid-mapfile"
            raise GridMapError(msg)

    def parse(self):
        """
        """
        # clear any existing entries
        self.clear()

        # parse the grid-mapfile
        try:
            f = open(self.path, 'r')
        except Exception, e:
            msg = "Unable to open %s for reading: %s" % (self.path, e)
            raise GridMapError(msg)

        for line in f:
            s = line.strip().split('"')
            if len(s) == 3: subject = s[1]
            elif len(s) == 2: subject = s[1]
            elif len(s) == 1: subject = s[0]
            else:
                msg = "Error parsing line %s" % line
                raise GridMapError(msg)

            dict.__setitem__(self, subject, 1)

        f.close()

    def __getitem__(self, key):
        """
        """
        self.parse()

        return dict.__getitem__(self, key)

    def has_key(self, key):
        """
        """
        self.parse()

        return dict.has_key(self, key)

    def keys(self):
        """
        """
        self.parse()

        return dict.keys(self)

class GridmapAuthorization:
    
    # Chec GridMap authorization.
    def check_authorization_gridmap(self, environ, req_method, full_uri, authorise):
        # Instantiate.
        admin = Admin.AdminHandle()
        constant = Constants.ConstantsHandle()
        # If using HTTP.
        if not constant.use_https or str(environ['LocalAccess'])=='True':
            # Set result to OK and carry on.
            r = [200]
        # Otherwise, using HTTPS.
        else:
            # Init.
            r = [401]
            # If PUT/PATCH.
            if authorise:
                c=36
                mapfile = constant.grid_map_put_patch_file
            # If GET.
            else:
                c=35
                mapfile = constant.grid_map_get_file
            # If mapfile set correctly.
            try:
                mapfile
            except:
                # Set HTTP code and log.
                r = admin.log_and_set_http_code(401, c, req_method, 'Grid mapfile not passed. Check it is correctly set in Constants module.', full_uri)
            else:
                # If SSL_CLIENT_VERIFY key available.
                try:
                    environ['SSL_CLIENT_VERIFY']
                except:
                    #print "SSL_CLIENT_VERIFY not found"
                    # Set HTTP code and log.
                    r = admin.log_and_set_http_code(505, c, req_method, 'SSL_CLIENT_VERIFY key unavailable. Check you are using HTTPS', full_uri)
                else:
                    # If SSL_CLIENT_CERT found.
                    try:
                        environ['SSL_CLIENT_CERT']
                    except:
                        #print "SSL_CLIENT_CERT not found"
                        # Set HTTP code and log.
                        r = admin.log_and_set_http_code(401, c, req_method, 'SSL_CLIENT_CERT key unavailable', full_uri)
                    else:
                        # Try to lead certificate.
                        try:
                            # Grab the client cert
                            clientCert = M2Crypto.X509.load_cert_string(environ['SSL_CLIENT_CERT'])
                        except:
                            #print "Unable to load certificate"
                            # Set HTTP code and log.
                            r = admin.log_and_set_http_code(401, c, req_method, 'Unable to load certificate', full_uri)
                        else:
                            # Get the client cert subject.
                            clientSubject = clientCert.get_subject().__str__()
                            #print "The client cert subject is %s" % clientSubject
                            # Check if the client cert is a proxy
                            try:
                                clientCert.get_ext("proxyCertInfo")
                                clientCertProxy = True
                                #print "The client cert is a proxy"
                            # If client cert not a proxy.
                            except LookupError:
                                clientCertProxy = False
                                #print "The client cert is not a proxy"
                            # Set subject if client cert not proxy.
                            if not clientCertProxy:
                                subject = clientSubject
                            # Otherwise, if proxy.
                            else:
                                # Find the number of certificates in the client chain.
                                maximum = None
                                # Loop through environment keys.
                                for e in environ.keys():
                                    # Check if SSL client cert chain.
                                    m = re.search('SSL_CLIENT_CERT_CHAIN_(\d+)', e)
                                    # If client cert chain found.
                                    if m:
                                        #print "Found SSL_CLIENT_CERT_CHAIN_%s" % m.group(1)
                                        # Set maximum.
                                        n = int(m.group(1))
                                        if n > maximum: maximum = n
                                # Set cert chain lenght.
                                certChainLength = maximum + 1
                                #print "There are %d certs in the chain" % certChainLength
                                # Grab each certificate in the chain.
                                chainCerts = [ M2Crypto.X509.load_cert_string(environ['SSL_CLIENT_CERT_CHAIN_%d' % i]) for i in range(certChainLength) ]
                                # walk the chain and find the first end entity certificate
                                #print "Walking the cert chain now..."
                                for chain in chainCerts:
                                    # Get subject.
                                    s = chain.get_subject().__str__()
                                    #print "Chain cert subject is %s" % s
                                    # If a proxy.
                                    try:
                                        chain.get_ext("proxyCertInfo")
                                        #print"Chain cert %s is a proxy" % s
                                    # If not a proxy.
                                    except LookupError:
                                        #print "Chain cert %s is not a proxy" % s
                                        break
                                # Set subject.
                                subject = s
                            #print "Authorizing against %s" % subject
                            # Parse the Grid mapfile and see if subject in it
                            try:
                                g = GridMap(mapfile)
                                # If subject found.
                                if g.has_key(subject):
                                    r = [200]
                                # Otherwise, if subject not found.
                                else:
                                    # Set HTTP code and log.
                                    r = admin.log_and_set_http_code(401, c, req_method, "Subject not found in Grid mapfile: %s" % (mapfile), full_uri)
                            # If unable to parse Grid mapfile
                            except Exception, e:
                                # Set HTTP code and log.
                                r = admin.log_and_set_http_code(401, c, req_method, "Unable to check authorization in grid-mapfile %s: %s" % (mapfile, e), full_uri)
        # Return.
        return r

class SciTokensAuthorization():
    def __init__(self):
        self.admin = Admin.AdminHandle()
        self.constant = Constants.ConstantsHandle()
        os.environ['XDG_CACHE_HOME'] = self.constant.scitokens_cache_dir
        self.token_enforcer = scitokens.Enforcer(self.constant.scitokens_issuer, audience=self.constant.scitokens_audience)

    def check_authorization_scitoken(self, environ, req_method, full_uri, authorise):
        # Instantiate.
        # If using HTTP.
        if not self.constant.use_https or str(environ['LocalAccess'])=='True':
            # Set result to OK and carry on.
            r = [200]
        # Otherwise, using HTTPS.
        else:
            # Init.
            r = [401]
        
            if 'HTTP_AUTHORIZATION' not in environ:
                raise KeyError("No SciToken in HTTPS headers")
            auth_type, auth_payload = environ['HTTP_AUTHORIZATION'].split(' ')
            if auth_type != 'Bearer':
                raise TypeError("SciTokens authorization requires a bearer token")
            token = scitokens.SciToken.deserialize(auth_payload, audience=self.constant.scitokens_audience)
        
            # If PUT/PATCH.
            if authorise:
                if self.token_enforcer.test(token, "write", "/DQSegDB"):
                    r = [200]
                else:
                    r = self.admin.log_and_set_http_code(401, 36, req_method, "SciToken not valid for write access", full_uri)
            # GET
            else:
                if self.token_enforcer.test(token, "read", "/DQSegDB"):
                    r = [200]
                else:
                    r = self.admin.log_and_set_http_code(401, 35, req_method, "SciToken not valid for read access", full_uri)

        # Return.
        return r
