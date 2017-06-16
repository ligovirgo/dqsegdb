# Copyright (C) 2015 Ryan Fisher, Gary Hemming
#
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

from __future__ import print_function

from warnings import warn
import sys
import httplib
import urlparse
import urllib2
import socket
import calendar
import time
import os
from OpenSSL import crypto

#
# =============================================================================
#
#                Library for DQSEGDB API Providing URL Functions
#
# =============================================================================
#

class HTTPSClientAuthConnection(httplib.HTTPSConnection):
  def __init__(self, host, timeout=None):
      try:
          certfile,keyfile=findCredential()
      except:
          warn("Warning:  No proxy found or other error encountered during check for authentication credentials, connections to https will not work.")
          certfile=""
          keyfile=""
          ### Fix!!! This doesn't actually seem to work because someone thought sys.exit was good error handling... Beyond that:  What does HTTPSConnection expect in this case?  The connections will fail, but we might want to report that carefully...
      httplib.HTTPSConnection.__init__(self, host, key_file=keyfile, cert_file=certfile)
      self.timeout = timeout # Only valid in Python 2.6

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
  def https_open(self, req):
      return self.do_open(HTTPSClientAuthConnection, req)


def getDataHttplib(url):
    """
    DEPRECATED!
    Optional fall back in case of failure in getDataUrllib2
    Takes a url such as:
    url="http://segdb-test-internal/dq/H1/DMT-SCIENCE/1/active?s=10&e=20"
    Returns JSON response from server
    """
    warn("Warning: using function that my not work any more!")
    urlsplit=urlparse.urlparse(url)
    conn=httplib.HTTPConnection(urlsplit.netloc)
    conn.request("GET",'?'.join([urlsplit.path,urlsplit.query]))
    r1=conn.getresponse()
    if r1.status!=200:
        warn("Return status code: %s, %s; URL=%s" % (str(r1.status),str(r1.reason),url))
        raise(urllib2.URLError)
    data1=r1.read()
    return data1

def getDataUrllib2(url,timeout=900,logger=None,warnings=True):
    socket.setdefaulttimeout(timeout)
    """
    Takes a url such as:
    url="http://segdb-test-internal/dq/dq/H1/DMT-SCIENCE/1/active?s=10&e=20"
    Returns JSON response from server
    Also handles https requests with grid certs (or proxy certs).
    """
    if logger:
        logger.debug("Beginning url call: %s" % url)
    try:
        if urlparse.urlparse(url).scheme == 'https':
            #print("attempting to send https query")
            #print(certfile)
            #print(keyfile)
            opener=urllib2.build_opener(HTTPSClientAuthHandler)
            #print(opener.handle_open.items())
            request = urllib2.Request(url)
            output=opener.open(request)
        else:
            #print("attempting to send http query")
            output=urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        #print("Warnings setting FIX:")
        #print(warnings)
        if warnings:
            handleHTTPError("GET",url,e)
        else:
            handleHTTPError("QUIET",url,e)

        ##print(e.read())
        #print("Warning: Issue accessing url: %s" % url)
        #print("Code: ")
        #print(e.code)
        #print(e.msg)
        ##import pdb
        ##pdb.set_trace()
        ##print(e.reason)
        ##print(url)
        #print("May be handled cleanly by calling instance: otherwise will result in an error.")
        raise
    except urllib2.URLError as e:
        #print(e.read())
        warn("Issue accesing url: %s; Reason: %s" % (url,str(e.reason)))
        try:
            type, value, traceback_stack = sys.exc_info()
            warnmsg="Trying custom URLError."
            warnmsg+=" "
            warnmsg+=str(type)
            warnmsg+=str(value)
            warn(warnmsg)
            import traceback
            traceback.print_tb(traceback_stack)
            raise e

        except:
            warn(url)
            raise
    if logger:
        logger.debug("Completed url call: %s" % url)
    return output.read()

def constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime):
    """
    Simple url construction method for dqsegdb server flag:version queries
    including restrictions on time ranges.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    ifo : `string`
        Ex: 'L1'
    name: `string`
        Ex: 'DMT-SCIENCE'
    version : `string` or `int`
        Ex: '1'
    include_list_string : `string`
        Ex: "metadata,known,active"
    startTime : `int`
        Ex: 999999999
    endTime : `int`
        Ex: 999999999

    """
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo,name,str(version)])
    # include_list_string should be a comma seperated list expressed as a string for the URL
    # Let's pass it as a python string for now?  Fix!!!
    start='s=%i' % startTime
    end='e=%i' % endTime
    url3=url2+'?'+start+'&'+end+'&include='+include_list_string
    return url3

def constructSegmentQueryURL(protocol,server,ifo,name,version,include_list_string):
    """
    Simple url construction method for dqsegdb server flag:version queries
    not including restrictions on time ranges.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    ifo : `string`
        Ex: 'L1'
    name: `string`
        Ex: 'DMT-SCIENCE'
    version : `string` or `int`
        Ex: '1'
    include_list_string : `string`
        Ex: "metadata,known,active"
    """
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo,name,version])
    url3=url2+'?'+'include='+include_list_string
    return url3

def constructVersionQueryURL(protocol,server,ifo,name):
    """
    Simple url construction method for dqsegdb server version queries.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    ifo : `string`
        Ex: 'L1'
    name: `string`
        Ex: 'DMT-SCIENCE'
    """
    ## Simple url construction method:
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo,name])
    return url2

def constructFlagQueryURL(protocol,server,ifo):
    """
    Simple url construction method for dqsegdb server flag queries.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    ifo : `string`
        Ex: 'L1'
    """
    ## Simple url construction method:
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo])
    return url2

def putDataUrllib2(url,payload,timeout=900,logger=None):
    """
    Wrapper method for urllib2 that supports PUTs to a url.

    Parameters
    ----------
    url : `string`
        Ex: 'https://dqsegdb5.phy.syr.edu/L1/DMT-SCIENCE/1'
    payload : `string`
        JSON formatted string

    """
    socket.setdefaulttimeout(timeout)
    #BEFORE HTTPS: opener = urllib2.build_opener(urllib2.HTTPHandler)
    if urlparse.urlparse(url).scheme == 'https':
        opener=urllib2.build_opener(HTTPSClientAuthHandler)
    else:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=payload)
    request.add_header('Content-Type', 'JSON')
    request.get_method = lambda: 'PUT'
    if logger:
        logger.debug("Beginning url call: %s" % url)
    try:
        urlreturned = opener.open(request)
    except urllib2.HTTPError as e:
        handleHTTPError("PUT",url,e)
        ##print(e.read())
        #if int(e.code)==404:
        #    print("Flag does not exist in database yet for url: %s" % url)
        #else:
        #    print("Warning: Issue accessing url: %s" % url)
        #    print("Code: ")
        #    print(e.code)
        #    print("Message: ")
        #    print(e.msg)
        #    #print(e.reason)
        #    #print(url)
        #    print("May be handled cleanly by calling instance: otherwise will result in an error.")
        ##print(e.reason)
        ##print(urlreturned)
        raise
    except urllib2.URLError as e:
        #print(e.read())
        warnmsg="Warning: Issue accessing url: %s" % url
        warnmsg+="; "
        warnmsg+=str(e.reason)
        warnmsg+="; "
        warnmsg+="May be handled cleanly by calling instance: otherwise will result in an error."
        warn(warnmsg)
        raise
    if logger:
        logger.debug("Completed url call: %s" % url)
    return url

def patchDataUrllib2(url,payload,timeout=900,logger=None):
    """
    Wrapper method for urllib2 that supports PATCHs to a url.

    Parameters
    ----------
    url : `string`
        Ex: 'https://dqsegdb5.phy.syr.edu/L1/DMT-SCIENCE/1'
    payload : `string`
        JSON formatted string

    """
    socket.setdefaulttimeout(timeout)
    #BEFORE HTTPS: opener = urllib2.build_opener(urllib2.HTTPHandler)
    if urlparse.urlparse(url).scheme == 'https':
        opener=urllib2.build_opener(HTTPSClientAuthHandler)
    else:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
    #print(opener.handle_open.items())
    request = urllib2.Request(url, data=payload)
    request.add_header('Content-Type', 'JSON')
    request.get_method = lambda: 'PATCH'
    if logger:
        logger.debug("Beginning url call: %s" % url)
    try:
        urlreturned = opener.open(request)
    except urllib2.HTTPError as e:
        handleHTTPError("PATCH",url,e)
        ##print(e.read())
        #print("Warning: Issue accessing url: %s" % url)
        #print("Code: ")
        #print(e.code)
        ##print(e.reason)
        ##print(url)
        #print("May be handled cleanly by calling instance: otherwise will result in an error.")
        raise
    except urllib2.URLError as e:
        #print(e.read()
        warnmsg="Warning: Issue accessing url: %s" % url
        warnmsg+="; "
        warnmsg+=str(e.reason)
        warnmsg+="; "
        warnmsg+="May be handled cleanly by calling instance: otherwise will result in an error."
        warn(warnmsg)
        #warn("Warning: Issue accessing url: %s" % url
        #warn(e.reason
        #warn("May be handled cleanly by calling instance: otherwise will result in an error."
        raise
    if logger:
        logger.debug("Completed url call: %s" % url)
    return url

def handleHTTPError(method,url,e):
    if int(e.code)!=404:
        warn("Warning: Issue accessing url: %s" % url)
        warn("Code: %s" % str(e.code))
        warn("Message: %s" % str(e.msg))
        #print(e.reason)
        #print(url)
        warn("May be handled cleanly by calling instance: otherwise will result in an error.")
    else:
        if method == "PUT" or method == "PATCH":
            warn("Info: Flag does not exist in database yet for url: %s" % url)
        elif method == "GET":
            warn("Warning: Issue accessing url: %s" % url)
            #print("yo! FIX!!!")
            warn("Code: %s" % str(e.code))
            warn("Message: %s" % str(e.msg))
            warn("May be handled cleanly by calling instance: otherwise will result in an error.")
        # If method == "QUIET" print nothing:  used for GET checks that don't need to toss info on a 404

###################
#
# Functions copied from glue:
# GLUE is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################

def findCredential():
    """
    Follow the usual path that GSI libraries would
    follow to find a valid proxy credential but
    also allow an end entity certificate to be used
    along with an unencrypted private key if they
    are pointed to by X509_USER_CERT and X509_USER_KEY
    since we expect this will be the output from
    the eventual ligo-login wrapper around
    kinit and then myproxy-login.
    """

    # use X509_USER_PROXY from environment if set
    if os.environ.has_key('X509_USER_PROXY'):
        filePath = os.environ['X509_USER_PROXY']
        if validateProxy(filePath):
            return filePath, filePath

    # use X509_USER_CERT and X509_USER_KEY if set
    if os.environ.has_key('X509_USER_CERT'):
        if os.environ.has_key('X509_USER_KEY'):
            certFile = os.environ['X509_USER_CERT']
            keyFile = os.environ['X509_USER_KEY']
            return certFile, keyFile

    # search for proxy file on disk
    uid = os.getuid()
    path = "/tmp/x509up_u%d" % uid

    if os.access(path, os.R_OK):
        if validateProxy(path):
            return path, path

    # if we get here could not find a credential
    raise RuntimeError("Could not find a valid proxy credential")


def validateProxy(path):
    """Validate a proxy certificate as RFC3820 and not expired

    Parameters
    ----------
    path : `str`
        the path of the proxy certificate file

    Returns
    -------
    True
        if the proxy is validated

    Raises
    ------
    IOError
        if the proxy certificate file cannot be read
    RuntimeError
        if the proxy is found to be a legacy globus cert, or has expired
    """
    # load the proxy from path
    try:
        with open(path, 'rt') as f:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    except IOError as e:
        e.args = ('Failed to load proxy certificate: %s' % str(e),)
        raise

    # try and read proxyCertInfo
    rfc3820 = False
    for i in range(cert.get_extension_count()):
        if cert.get_extension(i).get_short_name() == 'proxyCertInfo':
            rfc3820 = True
            break

    # otherwise test common name
    if not rfc3820:
        subject = cert.get_subject()
        if subject.CN.startswith('proxy'):
            raise RuntimeError('Could not find a valid proxy credential')

    # check time remaining
    expiry = cert.get_notAfter()
    if isinstance(expiry, bytes):
        expiry = expiry.decode('utf-8')
    expiryu = calendar.timegm(time.strptime(expiry, "%Y%m%d%H%M%SZ"))
    if expiryu < time.time():
        raise RuntimeError('Required proxy credential has expired')

    return True
