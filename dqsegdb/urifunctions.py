# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher, Gary Hemming, and Duncan Brown. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
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
import socket
import calendar
import time
import os
from OpenSSL import crypto

from six.moves.urllib.parse import urlparse
from six.moves import http_client
from six.moves.urllib.request import Request as Request
from six.moves.urllib import (request as urllib_request,
                              error as urllib_error)


#
# =============================================================================
#
#                Library for DQSEGDB API Providing URL Functions
#
# =============================================================================
#

def findSciToken(aud,scope):
    """Look for a scitoken that can be used to talk to a DQSegDB server

    Parameters
    ----------
    aud : `str`
        audience for the token (the hostname of the DQSegDB server)

    scope : `str`
        check that token contains this scope

    Returns
    -------
    token : `str`
        text string containing the serialized SciToken
    """
    token_data = None
    tok = None

    try:
        import scitokens
    except ImportError:
        return token_data

    authz, path = scope.split(':')

    # look for a condor-created scitoken for the target url
    if os.environ.get('_CONDOR_CREDS'):
        for f in os.listdir(os.environ['_CONDOR_CREDS']):
            if f.endswith(".use"):
                try:
                    with open(os.path.join(
                              os.environ['_CONDOR_CREDS'],f)) as t:
                        token_data = t.read().strip()
                        tok = scitokens.SciToken.deserialize(token_data,
                                                             audience=aud)
                        break
                except InvalidTokenFormat, InvalidAudienceError:
                    # ignore files that do not contain tokens
                    # or that are for a different audience
                    pass

    # use the token in the specified file
    if os.environ.get('SCITOKENS_FILE'):
        with open(os.environ.get('SCITOKENS_FILE')) as t:
            token_data = t.read().strip()
            tok = scitokens.SciToken.deserialize(token_data,
                                                 audience=aud)

    # use a serialized token in an environment variable
    if os.environ.get('SCITOKEN'):
        token_data = os.environ['SCITOKEN'].strip()
        tok = scitokens.SciToken.deserialize(token_data,
                                             audience=aud)

    # check that this token has dqsegdb read permissions
    if token_data:
        token_enforcer = scitokens.Enforcer(tok['iss'], audience=aud)
        if token_enforcer.test(token, authz, path) is False:
            raise ValueError('SciToken does not have read:/DQSegDB scope')

    return token_data


def getDataUrllib2(url, timeout=900, logger=None, warnings=True,
                   **urlopen_kw):
    """Return response from server

    Parameters
    ----------
    url : `str`
        remote URL to request (HTTP or HTTPS)

    timeout : `float`
        time (seconds) to wait for reponse

    logger : `logging.Logger`
        logger to print to

    **urlopen_kw
        other keywords are passed to :func:`urllib.request.urlopen`

    Returns
    -------
    response : `str`
        the text reponse from the server
    """
    if logger:
        logger.debug("Beginning url call: %s" % url)
    if urlparse(url).scheme == 'https' and 'context' not in urlopen_kw:
        from ssl import create_default_context
        urlopen_kw['context'] = context = create_default_context()
        req = Request(url)

        # if we have a token, use it, otherwise look for x590 cert
        token_data = findSciToken(urlparse(url).hostname, "read:/DQSegSB")
        if token_data:
            req.add_header("Authorization", "Bearer " + token_data)
        else:
            from gwdatafind.utils import find_credential
            context.load_cert_chain(*find_credential())

    else:
        req = Request(url)

    output = urllib_request.urlopen(req, timeout=timeout, **urlopen_kw)

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

def putDataUrllib2(url,payload,timeout=900,logger=None,
                   **urlopen_kw):
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
    if urlparse(url).scheme == 'https' and 'context' not in urlopen_kw:
        from ssl import create_default_context
        urlopen_kw['context'] = context = create_default_context()
    #BEFORE HTTPS: opener = urllib2.build_opener(urllib2.HTTPHandler)
    #if urlparse(url).scheme == 'https':
    #    opener=urllib_request.build_opener(HTTPSClientAuthHandler)
    #else:
    #    opener = urllib_request.build_opener(urllib_request.HTTPHandler)
    request = urllib_request.Request(url, data=payload)

    # if we have a token, use it, otherwise look for x590 cert
    token_data = findSciToken(urlparse(url).hostname, "write:/DQSegSB")
    if token_data:
        request.add_header("Authorization", "Bearer " + token_data)
    else:
        from gwdatafind.utils import find_credential
        context.load_cert_chain(*find_credential())

    request.add_header('Content-Type', 'JSON')
    request.get_method = lambda: 'PUT'
    if logger:
        logger.debug("Beginning url call: %s" % url)
    try:
        urlreturned = urllib_request.urlopen(request, timeout=timeout, **urlopen_kw)
    except urllib_error.HTTPError as e:
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
    except urllib_error.URLError as e:
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

def patchDataUrllib2(url,payload,timeout=900,logger=None,
                   **urlopen_kw):
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
    if urlparse(url).scheme == 'https' and 'context' not in urlopen_kw:
        from ssl import create_default_context
        urlopen_kw['context'] = context = create_default_context()
    #if urlparse(url).scheme == 'https':
    #    opener=urllib_request.build_opener(HTTPSClientAuthHandler)
    #else:
    #    opener = urllib_request.build_opener(urllib_request.HTTPHandler)
    #print(opener.handle_open.items())
    request = urllib_request.Request(url, data=payload)

    # if we have a token, use it, otherwise look for x590 cert
    token_data = findSciToken(urlparse(url).hostname, "write:/DQSegSB")
    if token_data:
        request.add_header("Authorization", "Bearer " + token_data)
    else:
        from gwdatafind.utils import find_credential
        context.load_cert_chain(*find_credential())

    request.add_header('Content-Type', 'JSON')
    request.get_method = lambda: 'PATCH'
    if logger:
        logger.debug("Beginning url call: %s" % url)
    try:
        #urlreturned = opener.open(request)
        urlreturned = urllib_request.urlopen(request, timeout=timeout, **urlopen_kw)
    except urllib_error.HTTPError as e:
        handleHTTPError("PATCH",url,e)
        ##print(e.read())
        #print("Warning: Issue accessing url: %s" % url)
        #print("Code: ")
        #print(e.code)
        ##print(e.reason)
        ##print(url)
        #print("May be handled cleanly by calling instance: otherwise will result in an error.")
        raise
    except urllib_error.URLError as e:
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
