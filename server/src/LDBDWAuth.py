import re
import Admin
import exceptions
import M2Crypto


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

def checkAuthorizationGridMap(environ, admin_handler, mapfile = None):
    """
    mapfile is a string containing the file system path to the grid-mapfile 
    to be used
    """
    # first make sure the client was verified
    verification = environ['SSL_CLIENT_VERIFY']
    if verification != 'SUCCESS':
        return (False, None)

    # grab the client cert
    clientCert = M2Crypto.X509.load_cert_string(environ['SSL_CLIENT_CERT'])
    clientSubject = clientCert.get_subject().__str__()
    #logger.debug("The client cert subject is %s" % clientSubject)

    # see if the client cert is a proxy
    try:
        clientCert.get_ext("proxyCertInfo")
        clientCertProxy = True
        #logger.debug("The client cert is a proxy")
    except LookupError:
        clientCertProxy = False
        #logger.debug("The client cert is not a proxy")

    if not clientCertProxy:
        subject = clientSubject

    else:
        # find the number of certificates in the client chain
        max = None
        for e in environ.keys():
            m = re.search('SSL_CLIENT_CERT_CHAIN_(\d+)', e)
            if m:
                #logger.debug("Found SSL_CLIENT_CERT_CHAIN_%s" % m.group(1))
                n = int(m.group(1))
                if n > max: max = n

        certChainLength = max + 1

        #logger.debug("There are %d certs in the chain" % certChainLength)

        # grab each certificate in the chain
        chainCerts = [ M2Crypto.X509.load_cert_string(environ['SSL_CLIENT_CERT_CHAIN_%d' % i]) for i in range(certChainLength) ]

        # walk the chain and find the first end entity certificate
        #logger.debug("Walking the cert chain now...")
        for c in chainCerts:
            s = c.get_subject().__str__()
            #logger.debug("Chain cert subject is %s" % s)
            try:
                c.get_ext("proxyCertInfo")
                #logger.debug("Chain cert %s is a proxy" % s)
            except LookupError:
                #logger.debug("Chain cert %s is not a proxy" % s)
                break
        subject = s

    #logger.debug("Authorizing against %s" % subject)

    # parse the grid-mapfile and see if subject in it
    authorized = False
    if not mapfile:
        mapfile = configuration['gridmap']
    try:
        g = GridMap(mapfile)
        if g.has_key(subject):
            authorized = True
        else:
            authorized = False
    except Exception, e:
        #logger.error("Unable to check authorization in grid-mapfile %s: %s" % (mapfile, e))
        print "Should raise some error if this happens"
    return (authorized, subject)
