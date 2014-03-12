import httplib
import urlparse
import urllib2
import socket

#
# =============================================================================
#
#                Library for DQSEGDB API Providing URL Functions 
#
# =============================================================================
#

def getDataHttplib(url):
    """
    Optional fall back in case of failure in getDataUrllib2
    Takes a url such as:
    url="http://segdb-test-internal/dq/H1/DMT-SCIENCE/1/active?s=10&e=20"
    Returns JSON response from server
    """
    urlsplit=urlparse.urlparse(url)
    conn=httplib.HTTPConnection(urlsplit.netloc)
    conn.request("GET",'?'.join([urlsplit.path,urlsplit.query]))
    r1=conn.getresponse()
    if r1.status!=200:
        print "Return status code: %s, %s" % r1.status,r1.reason
        raise(urllib2.URLError)
    data1=r1.read()
    return data1

def getDataUrllib2(url,timeout=30):
    socket.setdefaulttimeout(timeout)
    """
    Takes a url such as:
    url="http://segdb-test-internal/dq/dq/H1/DMT-SCIENCE/1/active?s=10&e=20"
    Returns JSON response from server
    """
    try:
        r1=urllib2.urlopen(url)
    except urllib2.URLError,e:
        print e.code
        print e.read()
        raise
    return r1.read()

def constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime):
    """
    Simple url construction method for dqsegdb server flag:version queries 
    including restrictions on time ranges.
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
    """
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo,name,version])
    url3=url2+'?'+'include='+include_list_string
    return url3

def constructVersionQueryURL(protocol,server,ifo,name):
    """
    Simple url construction method for dqsegdb server version queries. 
    """
    ## Simple url construction method:
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo,name])
    return url2

def constructFlagQueryURL(protocol,server,ifo):
    """
    Simple url construction method for dqsegdb server flag queries. 
    """
    ## Simple url construction method:
    url1=protocol+"://"+server+"/dq"
    url2='/'.join([url1,ifo])
    return url2

def putDataUrllib2(url,payload,timeout=30):
    """
    Wrapper method for urllib2 that supports PUTs to a url.
    """
    socket.setdefaulttimeout(timeout)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=payload)
    request.add_header('Content-Type', 'JSON')
    request.get_method = lambda: 'PUT'
    try:
        url = opener.open(request)
    except urllib2.URLError,e:
        print e.code
        print e.read()
        raise
    return url

def patchDataUrllib2(url,payload,timeout=30):
    """
    Wrapper method for urllib2 that supports PATCHs to a url.
    """
    socket.setdefaulttimeout(timeout)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=payload)
    request.add_header('Content-Type', 'JSON')
    request.get_method = lambda: 'PATCH'
    try:
        url = opener.open(request)
    except urllib2.URLError,e:
        print e.code
        print e.read()
        raise
    return url


