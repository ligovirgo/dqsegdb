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

import json
import os
import sys
import time
from datetime import datetime, time as time2

from six.moves.urllib.error import HTTPError

try:
    import pyRXPU as pyRXP
except ImportError:
    import pyRXP

from glue import ldbd
from ligo import segments
from glue.ligolw.utils import process

try:
    from lal import UTCToGPS as _UTCToGPS
except ImportError:
    # lal is optional
    from glue import gpstime
    _UTCToGPS = lambda utc: int(gpstime.GpsSecondsFromPyUTC(time.mktime(utc)))

from dqsegdb import urifunctions
from dqsegdb import clientutils
from dqsegdb.jsonhelper import InsertFlagVersion
from dqsegdb.jsonhelper import InsertFlagVersionOld
from dqsegdb.urifunctions import *

__author__ = 'Ryan Fisher <ryan.fisher@ligo.org>'
verbose=False

def dqsegdbCheckVersion(protocol,server,ifo,name,version,warnings=True):
    """
    Checks for existence of a given version of a flag in the db.
    Returns true if version exists

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
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    ### Fix!!! This looks wrong:  seems to check if the flag exists, not whether a version on the server matches what was passed to the function
    queryurl=urifunctions.constructVersionQueryURL(protocol,server,ifo,name)
    try:
        result=urifunctions.getDataUrllib2(queryurl, warnings=warnings)
    except HTTPError as e:
        if e.code==404:
            return False
        else:
            raise
    ult_json=json.loads(result)
    version_list=result_json['version']
    if version in version_list:
        return True
    else:
        return False

    ## Optional method: query the version directly, and look for !404:
    # Pro:
    # No need to actually parse result for this function so just return True
    # Con?

def dqsegdbMaxVersion(protocol,server,ifo,name):
    """
    Checks for existence of a flag in the db, returns maximum
    version if the flag exists exists, 0 if the flag does not exist.

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
    queryurl=urifunctions.constructFlagQueryURL(protocol,server,ifo)
    try:
        result=urifunctions.getDataUrllib2(queryurl,warnings=False)
    except HTTPError as e:
        print("e.code: %s  FIX!" % str(e.code))
        if int(e.code)==404:
            return 0
        else:
            # Print all the messages this time
            result=urifunctions.getDataUrllib2(queryurl,warnings=True)
            raise
    # Now parse result for max version:
    queryurl=urifunctions.constructVersionQueryURL(protocol,server,ifo,name)
    try:
        result=urifunctions.getDataUrllib2(queryurl,warnings=False)
    except HTTPError as e:
        if int(e.code)==404:
            return 0
        else:
            raise

    result_json=json.loads(result)
    version_list=result_json['version']
    return max(version_list)


def dqsegdbFindEndTime(flag_dict):
    """
    Determines max end_time from known times in flag_dict

    Parameters
    _________
    flag_dict: `dictionary`
        Input dictionary, converted from json using json.loads in previous call

    Returns max_end_time: `int`
    """
    if len(flag_dict['known'])!=0:
        maxEndTime=max([i[1] for i in flag_dict['known']])
        return maxEndTime
    else:
        import warnings
        warnings.warn("Function used to find max known_time from a flag was handed a flag with an empty set of known times.  Returning None")
        return None

def dqsegdbQueryTimes(protocol,server,ifo,name,version,include_list_string,startTime,endTime,warnings=True):
    """
    Issue query to server for ifo:name:version with start and end time
    Returns the python loaded JSON response!

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
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    queryurl=urifunctions.constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime)
    result=urifunctions.getDataUrllib2(queryurl,warnings=warnings)
    result_json=json.loads(result)
    return result_json,queryurl


#dqsegdbQueryTimesCompatible
def dqsegdbQueryTimesCompatible(protocol,server,ifo,name,version,include_list_string,startTime,endTime,warnings=True):
    """
    Issue query to server for ifo:name:version with start and end time
    This is the version that reproduces S6 style query results when the query is empty
    Returns the python loaded JSON response!

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
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`

    """
    queryurl=urifunctions.constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime)
    try:
        result=urifunctions.getDataUrllib2(queryurl, warnings=warnings)
        result_json=json.loads(result)
    except HTTPError as e:
        if e.code==404:
            # For S6 executable compatibility, we need to return something anyway to make ligolw_segments_from_cats and segment_query work properly, in this case, we'll return a faked up dictionary with empty lists for keys 'known' and 'active', which the calling functions will correctly interperet (because it's the equivalent of asking for a flag outside known time for the S6 calls)
            result_json={"known":[],"active":[]}
        else:
            raise

    return result_json,queryurl


def dqsegdbQueryTimeless(protocol,server,ifo,name,version,include_list_string,warnings=True):
    """
    Issue query to server for ifo:name:version without start and end time
    Returns the python loaded JSON response converted into a dictionary and queryurl!
    Returns
    ----------
    [dictionary,string(url)]

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
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    queryurl=urifunctions.constructSegmentQueryURL(protocol,server,ifo,name,version,include_list_string)
    result=urifunctions.getDataUrllib2(queryurl, warnings=warnings)
    result_json=json.loads(result)
    return result_json,queryurl

def coalesceResultDictionary(result_dict):
    """
    Takes a dictionary as returned by QueryTimes or QueryTimeless and converts the lists of tuples into actual segment lists (and coalesces them).

    Parameters
    ----------
    result_dict : `dict`
        This is the input result dictionary from the other api calls
    out_result_dict : `dict`
        This is the output result dictionary with actual segment lists (and coalesced results).

    """
    import copy
    out_result_dict=copy.deepcopy(result_dict)
    active_seg_python_list=[segments.segment(i[0],i[1]) for i in result_dict['active']]
    active_seg_list=segments.segmentlist(active_seg_python_list)
    active_seg_list.coalesce()
    out_result_dict['active']=active_seg_list
    known_seg_python_list=[segments.segment(i[0],i[1]) for i in result_dict['known']]
    known_seg_list=segments.segmentlist(known_seg_python_list)
    known_seg_list.coalesce()
    out_result_dict['known']=known_seg_list
    return out_result_dict

def queryAPIVersion(protocol,server,verbose,warnings=True):
    """
    Construct url and issue query to get the reported list of all IFOs
    provided by dqsegd and the API version of the server.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    queryurl=protocol+"://"+server+"/dq"
    if verbose:
        print(queryurl)
    result=urifunctions.getDataUrllib2(queryurl, warnings=warnings)
    dictResult=json.loads(result)
    apiVersion=str(dictResult['query_information']['api_version'])
    return apiVersion


def reportFlags(protocol,server,verbose,warnings=True):
    """
    Construct url and issue query to get the reported list of all flags
    provided by dqsegdb.
    From the API Doc:
    Get a JSON formatted string resource describing all the flags in the database. This provides an optimization by returning all flag names and all associated versions in a single call.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    queryurl=protocol+"://"+server+"/report/flags"
    if verbose:
        print(queryurl)
    result=urifunctions.getDataUrllib2(queryurl,warnings=warnings)
    return result

def reportActive(protocol,server,includeSegments,verbose,gps_start_time,gps_end_time,warnings=True):
    """
    Construct url and issue query to get the reported list of all active segments for all flags in the time window provided.
    From the API Doc:
    Get a JSON string resource containing the active segments for all flags between t1 and t2. Note that this returns exactly what /dq/IFO/FLAG/VERSION does, except for ALL flags over the query period instead of one flag. The clients must assume that they may get empty active lists for flags that are unactive between times t1 and t2.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    includeSegments : `boolean`
        Ex: True
    verbose : `boolean`
        Ex: True
    gps_start_time: `int`
        Ex: 999999999
    gps_end_time: `int`
        Ex: 999999999
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`

    """
    if includeSegments:
        includeText=""
        timeText="?s=%d&e=%d"%(gps_start_time,gps_end_time)
    else:
        includeText="?include=metadata"
        timeText="&s=%d&e=%d"%(gps_start_time,gps_end_time)
    queryurl=protocol+"://"+server+"/report/active"+includeText+timeText
    if verbose:
        print(queryurl)
    result=urifunctions.getDataUrllib2(queryurl,timeout=1200,warnings=warnings)
    return result,queryurl

def reportKnown(protocol,server,includeSegments,verbose,gps_start_time,gps_end_time,warnings=True):
    """
    Construct url and issue query to get the reported list of all known segments for all flags in the time window provided.
    From the API Doc:
    Get a JSON string resource containing the known segments for all flags between t1 and t2. Note that this returns exactly what /dq/IFO/FLAG/VERSION/known does, except for ALL flags over the query period instead of one flag. The clients must assume that they may get empty known lists for flags that are unknown between times t1 and t2.

    Parameters
    ----------
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    includeSegments : `boolean`
        Ex: True
    verbose : `boolean`
        Ex: True
    gps_start_time: `int`
        Ex: 999999999
    gps_end_time: `int`
        Ex: 999999999
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    if includeSegments:
        includeText=""
        timeText="?s=%d&e=%d"%(gps_start_time,gps_end_time)
    else:
        includeText="?include=metadata"
        timeText="&s=%d&e=%d"%(gps_start_time,gps_end_time)
    queryurl=protocol+"://"+server+"/report/known"+includeText+timeText
    if verbose:
        print(queryurl)
    result=urifunctions.getDataUrllib2(queryurl,timeout=1200,warnings=warnings)
    return result,queryurl

def parseKnown(jsonResult):
    """
    Accepts jsonResult from reportKnown call and parses into expected format
    for ligolw_segment_query client to generate xml.
    """
    rows=[]
    resultDictionary=json.loads(jsonResult)
    #ifos, name, version, segment_definer_comment, segment_summary_start_time, segment_summary_end_time, segment_summary_comment = row
    # json looks like this:
    #{
    #    "query_information": {
    #        "api_version": 1,
    #        "end": "1076401264",
    #        "include": [],
    #        "server": "dqsegdb5.phy.syr.edu",
    #        # Jul 28: api_version replaced server_code_version
    #        "server_code_version": "v1r5",
    #        "server_elapsed_query_time": 2.3630100000000001,
    #        "server_timestamp": 1079895401,
    #        "start": "1076400544",
    #        "uri": "/report/known?s=1076400544&e=1076401264"
    #    },
    #    "results": [
    #        {
    #            "ifo": "L1",
    #            "known": [
    #                [
    #                    1076400480,
    #                    1076400848
    #                ],
    #                [
    #                    1076400848,
    #                    1076401200
    #                ],
    #                [
    #                    1076401200,
    #                    1076401568
    #                ]
    #            ],
    #            "metadata": {
    #                "active_indicates_ifo_badness": false,
    #                "comment": "L1 interferometer Up from h(t) DQ flags",
    #                "deactivated": false,
    #                "provenance_url": "This is where the url should go"
    #            },
    #            "name": "DMT-UP",
    #            "version": 1
    #        },
    #        {
    #            "ifo": "L1",
    #            "known": [
    #                [
    #                    1076400848,
    #                    1076401200
    #                ],
    #                [
    #                    1076401200,
    #                    1076401568
    #                ],
    #                [
    #                    1076400480,
    #                    1076400848
    #                ]
    #            ],
    #            "metadata": {
    #                "active_indicates_ifo_badness": false,
    #                "comment": "L1 interferometer Up from h(t) DQ flags",
    #                "deactivated": false,
    #                "provenance_url": "This is where the url should go"
    #            },
    #            "name": "DMT-SCIENCE",
    #            "version": 1
    #        },
    for i in resultDictionary['results']:
        # Ex: >>> resultDict['results'][0]
        #{u'known': [[1076400480, 1076400848], [1076400848, 1076401200], [1076401200, 1076401568]], u'ifo': u'L1', u'name': u'DMT-UP', u'version': 1, u'metadata': {u'comment': u'L1 interferometer Up from h(t) DQ flags', u'provenance_url': u'This is where the url should go', u'active_indicates_ifo_badness': False, u'deactivated': False}}
        #old: row = ('H1          ', 'ODC-PSL_FSS_RFPD_LT_TH', 1, 'RPFD check, when above threshold the segment will be off', 1072880640, 1072880656, '-')
        ifo=i['ifo']
        flag=i['name']
        version=i['version']
        comment=i['metadata']['comment']
        summary_comment='-'
        for j in i['known']:
            start=j[0]
            stop=j[1]
            row=(str(ifo),str(flag),int(version),str(comment),float(start),float(stop),str(summary_comment))
            rows.append(row)


    return rows

def dqsegdbCascadedQuery(protocol, server, ifo, name, include_list_string, startTime, endTime, debug=False, warnings=True):
    """
    Queries server for needed flag_versions to generate the result of a
    cascaded query (was called a versionless query in S6).

    Returns a python dictionary representing the calculated result "versionless"
    flag and also the python dictionaries (in a list) for the flag_versions
    necessary to construct the result.

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
    debug : `bool`
        Ex: False
    warnings : `bool`
        show warnings for `HTTPError` (as well as raising exception),
        default: `True`
    """
    if debug==True:
        verbose=True
    else:
        verbose=False

    ## Construct url and issue query to determine highest version from list
    ## of versions
    versionQueryURL=urifunctions.constructVersionQueryURL(protocol,server,ifo,name)
    if verbose:
        print(versionQueryURL)
    try:
        versionResult=urifunctions.getDataUrllib2(versionQueryURL,
                                                  warnings=warnings)
    except HTTPError as e:
        if e.code==404:
            import warnings
            warnings.warn("Provided IFO:FLAG: %s:%s not found in database, returning empty result" % (ifo,name))
            jsonResults=[]
    else:
        # Parse the result
        # Results should be a JSON object like this:
        #{
        # "meta": {
        #    query_uri" : "uri",   // contains the URI specified with the GET HTTP method
        #    "query_time" : gpstime,    // when the query was issued
        #    // optional query parameters
        #    "query_start" : t1,
        #    "query_end" : t2
        #    },
        #  "resource_type" : ["resource_uri_1", "resource_uri_2"]
        #}
        versionData=json.loads(versionResult)  #JSON is nice... :)

        ## Construct urls and issue queries for the multiple versions and dump the results to disk locally for careful provenance
        jsonResults=[]
        #urlList=versionData['resource_type']
        version_list=versionData['version']
        urlList=[versionQueryURL+'/'+str(version) for version in version_list]

        # sort list by decreasing version number and call each URL:
        sortedurlList=sorted(urlList, key=lambda url: url.split('/')[-1], reverse=True)
        for versioned_url in sortedurlList:
            # I am assuming I need to pull off the versions from the urls to use my existing library function.
            # Alternatively, we could make a new library function that starts from the end of the version and takes the include_list_string and start and end times as inputs
            version=versioned_url.split('/')[-1]
            queryurl=urifunctions.constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime)
            if verbose:
                print(queryurl)
            result=urifunctions.getDataUrllib2(queryurl, warnings=warnings)
            result_parsed=json.loads(result)
            jsonResults.append(result_parsed)
            # Fix!!! Improvement: Executive Decision:  Should we force these intermediate results to hit disk?
            # For now, I say yes:
            # Fix!!! Improvement: Choose a better location for files to go automatically, so this can be run from other directories
            filename=queryurl.replace('/','_').split(':')[-1]+'.json'
            if debug:
                try:
                    tmpfile=open(filename,'w')
                    json.dump(result_parsed,tmpfile)
                    tmpfile.close()
                    print("Stored partial result for individual version to disk as %s" % filename)
                except:
                    print("Couldn't save partial results to disk.... continuing anyway.")

    ## Construct output segments lists from multiple JSON objects
    # The jsonResults are in order of decreasing versions,
    # thanks to the sorting above
    # This generates a results_flag object for dumping to JSON with the
    # total_known_list across all versions, cascaded
    # and we have the total active list across all versions, cascaded
    # so we're done the math! :
    result_flag,affected_results=clientutils.calculate_versionless_result(jsonResults,startTime,endTime,ifo_input=ifo)
    if verbose:
        print("active segments:", result_flag['active'])
        print("known segments:", result_flag['known'])

    ### Old before JSON spec change:
    ### Need to build the client_meta part of the JSON results
    #meta={}
    #meta['program_name']=os.path.basename(__file__)
    #meta['options']=options
    #meta['start_time']=startTime
    #meta['end_time']=endTime
    #meta['query_uris_called']=sortedurlList
    ## Note: Using ligolw/utils/process.py method of determining time:
    #meta['query_time']=query_start
    #meta['query_start']=query_start
    #meta['query_end']=_UTCToGPS(time.gmtime())

    ### Now that we have the meta and the flags, which include the result, we need to build up the larger JSON
    #json_result={}
    #json_result['client_meta']=meta
    #json_result['flags']=[]
    #for flag in jsonResults:
    #    json_result['flags'].append(flag)
    #json_result['flags'].append(result_flag)

    # Now we need to return the reduced results and the intermediate JSON
    # responses from the versioned queries
    # Note: The result_flag will not have query_metadata
    return result_flag,jsonResults,affected_results

def dtd_uri_callback(uri):
    """
    S6 helper function for XML file writing and parsing using a dtd.
    """
    if uri in ['http://www.ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt',
        'http://ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt']:
        # if the XML file contains a http pointer to the ligolw DTD at CIT then
        # return a local copy to avoid any network problems
        return 'file://localhost' + os.path.join( os.environ["GLUE_PREFIX"],
          'etc/ligolw_dtd.txt' )
    else:
        # otherwise just use the uri in the file
        return uri



def waitTill(runTime,timeout=2400):
    """
    runTime is time in HH:MM (string) format, action is call to a function to
    be exceuted at specified time.
    Function source: http://stackoverflow.com/a/6579355/2769157
    """
    startTime = time2(*(map(int, runTime.split(':'))))
    waitTime=0 # Timeout set to 20 minutes
    while startTime > datetime.today().time() and waitTime < 1200:
        time.sleep(1)
        waitTime+=1
    return



def patchWithFailCases(i,url,debug=True,inlogger=None,testing_options={}):
    """
    Attempts to patch data to a url where the data is in a dictionary format
    that can be directly dumped to json that the dqsegdb server expects.
    Correctly fails to making a new version or flag in the database as needed.
    """
    try:
        #patch to the flag/version
        if debug:
            inlogger.debug("Trying to patch alone for url: %s" % url)
            #print("Trying to patch alone for url: %s" % url)
        if 'synchronize' in testing_options:
            startTime=testing_options['synchronize']
            inlogger.debug("Trying to patch synchronously at time %s" % startTime)
            waitTill(startTime)
        patchDataUrllib2(url,json.dumps(i.flagDict),logger=inlogger)
        if debug:
            inlogger.debug("Patch alone succeeded for %s" % url)
            #print("Patch alone succeeded for %s" % url)
    except HTTPError as e:
        if e.code!=404:
            raise e
        try:
            #put to version
            if debug:
                inlogger.debug("Trying to put alone for url: %s" % url)
                #print("Trying to put alone for %s" % url)
            putDataUrllib2(url,json.dumps(i.flagDict),logger=inlogger)
            if debug:
                inlogger.debug("Put alone succeeded for %s" % url)
                #print("Put alone succeeded for %s" % url)
        except HTTPError as ee:
            if ee.code!=404:
                raise ee
            #put to flag
            suburl='/'.join(url.split('/')[:-1])
            if debug:
                inlogger.debug("Trying to PUT flag and version to: %s" % suburl)
                #print("Trying to PUT flag and version to: "+suburl)
            putDataUrllib2(suburl,json.dumps(i.flagDict),logger=inlogger)
            #put to version
            putDataUrllib2(url,json.dumps(i.flagDict),logger=inlogger)
            if debug:
                inlogger.debug("Had to PUT flag and version")
                #print("Had to PUT flag and version")


def threadedPatchWithFailCases(q,server,debug,inputlogger=None):
    """
    Used by InsertMultipleDQXMLFileThreaded
    to patch data to server. (Deprecated/Incomplete error handling)
    """
    while True:
        i=q.get()
        url=i.buildURL(server)
        try:
            patchWithFailCases(i,url,debug,inlogger=inputlogger)
        except KeyboardInterrupt:
            print("interrupted by user!")
            sys.exit(1)
        q.task_done()

def setupSegment_md(filename,xmlparser,lwtparser,debug):
    """
    Helper function used to setup ligolw parser (S6 xml generation tool).
    """
    segment_md = ldbd.LIGOMetadata(xmlparser,lwtparser)

    #if debug:
    #    print("Inserting file %s." % filename)
    fh=open(filename,'r')
    xmltext = fh.read()
    fh.close()
    segment_md.parse(xmltext)
    if debug:
        #segment_md.table
        segment_md.table.keys()
    return segment_md

def InsertMultipleDQXMLFileThreaded(filenames,logger,server='http://slwebtest.virgo.infn.it',hackDec11=False,debug=True,threads=1,testing_options={}):
    """
    Inserts multiple dqxml files of data into the DQSEGDB.

    Input:
    - filenames is a list of string filenames for  DQXML files.
    - hackDec11 is deprecated (always should be false): This was used to differentiate function against different server APIs before we used numbering an responses to make decisions.
    - testing_options is a dictionary including (optionally):offset(int),synchronize(time in 'HH:MM' format (string))

    Output:
    returns True if it completes sucessfully
    """
    logger.info("Beginning call to InsertMultipleDQXMLFileThreaded.  This message last updated April 14 2015, Ciao da Italia!")
    from threading import Thread
    from Queue import Queue
    import sys

    # Make a call to server+'/dq':
    protocol=server.split(':')[0]
    serverfqdn=server.split('/')[-1]
    apiResult=queryAPIVersion(protocol,serverfqdn,False)
    # If the API change results in a backwards incompatibility, handle it here with a flag that affects behavior below
    if apiResult >= "2.1.0":
        # S6 style comments are needed
        new_comments=True
    else:
        # Older server, so don't want to supply extra comments...
        new_comments=False
    if apiResult >= "2.1.15":
        # Alteration to insertion_metadata from uri to comment to accomodate s6 data conversion
        use_new_insertion_metadata=True
    else:
        use_new_insertion_metadata=False


    if 'offset' in testing_options:
        offset=int(testing_options['offset'])
    else:
        offset=0
    if 'synchronize' in testing_options:
        synchronize=testing_options['synchronize']

    xmlparser = pyRXP.Parser()
    lwtparser = ldbd.LIGOLwParser()

    flag_versions = {}

    # flag_versions, filename, server, hackDec11, debug are current variables

    # This next bunch of code is specific to a given file:
    if len(filenames)<1:
        print("Empty file list sent to InsertMultipleDQXMLFileThreaded")
        raise ValueError
    for filename in filenames:

        segment_md = setupSegment_md(filename,xmlparser,lwtparser,debug)

        # segment_md, flag_versions, filename, server, hackDec11, debug are current variables

        flag_versions_numbered = {}

        for j in range(len(segment_md.table['segment_definer']['stream'])):
            flag_versions_numbered[j] = {}
            for i,entry in enumerate(segment_md.table['segment_definer']['orderedcol']):
              #print(j,entry,segment_md.table['segment_definer']['stream'][j][i])
              flag_versions_numbered[j][entry] = segment_md.table['segment_definer']['stream'][j][i]


        # parse process table and make a dict that corresponds with each
        # process, where the keys for the dict are like "process:process_id:1"
        # so that we can match
        # these to the flag_versions from the segment definer in the next
        # section

        # Note:  Wherever temp_ preceeds a name, it is generally an identifier
        # field from the dqxml, that is only good for the single dqxml file
        # being parsed


        process_dict = {}
        # Going to assign process table streams to process_dict with a key
        # matching process_id (process:process_id:0 for example)
        for j in range(len(segment_md.table['process']['stream'])):
            process_id_index = segment_md.table['process']['orderedcol'].index('process_id')
            temp_process_id = segment_md.table['process']['stream'][j][process_id_index]
            # Now we're going to assign elements to process_dict[process_id]
            process_dict[temp_process_id] = {}
            for i,entry in enumerate(segment_md.table['process']['orderedcol']):
                #print(j,entry,segment_md.table['process']['stream'][j][i])
                process_dict[temp_process_id][entry] = segment_md.table['process']['stream'][j][i]
                # Note that the segment_md.table['process']['stream'][0] looks like this:
                #0 program SegGener
                #0 version 6831
                #0 cvs_repository https://redoubt.ligo-wa.caltech.edu/
                #0                svn/gds/trunk/Monitors/SegGener/SegGener.cc
                #0 cvs_entry_time 1055611021
                #0 comment Segment generation from an OSC condition
                #0 node l1gds2
                #0 username john.zweizig@LIGO.ORG
                #0 unix_procid 24286
                #0 start_time 1065916603
                #0 end_time 1070395521
                #0 process_id process:process_id:0
                #0 ifos L0L1
                # So now I have all of that info stored by the process_id keys
                # Eventually I have to map these elements to the process_metadata
                # style.. maybe I can do that now:
            process_dict[temp_process_id]['process_metadata'] = {}
            if hackDec11:
                process_dict[temp_process_id]['process_metadata']['process_start_time'] = process_dict[temp_process_id]['start_time']
            else: # This is for the newer server APIs:  (April 24 2015 we checked it (it probably changed before ER6 finally))
                process_dict[temp_process_id]['process_metadata']['process_start_timestamp'] = process_dict[temp_process_id]['start_time']
            if new_comments:
                process_dict[temp_process_id]['process_comment']=process_dict[temp_process_id]['comment']
            process_dict[temp_process_id]['process_metadata']['uid'] = process_dict[temp_process_id]['username']
            process_dict[temp_process_id]['process_metadata']['args'] = [] ### Fix!!! dqxml has no args???
            process_dict[temp_process_id]['process_metadata']['pid'] = process_dict[temp_process_id]['unix_procid']
            process_dict[temp_process_id]['process_metadata']['name'] = process_dict[temp_process_id]['program']
            process_dict[temp_process_id]['process_metadata']['fqdn'] = process_dict[temp_process_id]['node'] ### Fix!!! Improvement: not really fqdn, just the node name

        # So now I have process_dict[temp_process_id]['process_metadata'] for each
        # process_id, and can add it to a flag version when it uses it;  really I
        # should group it with the segment summary info because that has the
        # insertion_metadata start and stop time

        ### Fix!!! Get the args from the *other* process table... yikes
        ### Double check what is done below works!
        # First pass:
        #if debug:
        #    import pdb
        #    pdb.set_trace()

        temp_process_params_process_id=None
        try:
            len(segment_md.table['process_params']['stream'])
        except:
            logger.info("No process_params table for file: %s" % filename)
        else:
            for j in range(len(segment_md.table['process_params']['stream'])):
                process_id_index = segment_md.table['process_params']['orderedcol'].index('process_id')
                temp_process_params_process_id=segment_md.table['process_params']['stream'][j][process_id_index]
                #  This next bit looks a bit strange, but the goal is to pull off only the param and value from each row of the process_params table, and then put them into the process_metadata
                #  Thus we loop through the columns in each row and toss out everything but the param and value entries, and then outside the for loop, append them to the args list
                for i, entry in enumerate(segment_md.table['process_params']['orderedcol']):
                    if entry=="param":
                        temp_param=str(segment_md.table['process_params']['stream'][j][i])
                    if entry=="value":
                        temp_value=str(segment_md.table['process_params']['stream'][j][i])
                process_dict[temp_process_params_process_id]['process_metadata']['args'].append(str(temp_param))
                process_dict[temp_process_params_process_id]['process_metadata']['args'].append(str(temp_value))

        #if debug:
        #    import pdb
        #    pdb.set_trace()

        temp_id_to_flag_version = {}

        for i in flag_versions_numbered.keys():
            ifo = flag_versions_numbered[i]['ifos']
            name = flag_versions_numbered[i]['name']
            version = flag_versions_numbered[i]['version']
            if (ifo,name,version) not in flag_versions.keys():
                if new_comments==True:
                    flag_versions[(ifo,name,version)] = InsertFlagVersion(ifo,name,version)
                else:
                    flag_versions[(ifo,name,version)] = InsertFlagVersionOld(ifo,name,version)
                if new_comments:
                    flag_versions[(ifo,name,version)].flag_description=str(flag_versions_numbered[i]['comment']) # old segment_definer comment = new flag_description
                    # OUTDATED PLACEHOLDER: flag_versions[(ifo,name,version)].version_comment=str(flag_versions_numbered[i]['comment'])
                else:
                    flag_versions[(ifo,name,version)].flag_comment=str(flag_versions_numbered[i]['comment'])
                    flag_versions[(ifo,name,version)].version_comment=str(flag_versions_numbered[i]['comment'])
            flag_versions[(ifo,name,version)].temporary_definer_id = flag_versions_numbered[i]['segment_def_id']
            flag_versions[(ifo,name,version)].temporary_process_id = flag_versions_numbered[i]['process_id']
            # Populate reverse lookup dictionary:
            temp_id_to_flag_version[flag_versions[(ifo,name,version)].temporary_definer_id] = (ifo,name,version)


        # ways to solve the metadata problem:
        # Associate each insertion_metadata block with a process, then group
        # them and take the min insert_data_start and max insert_data_stop


        # parse segment_summary table and associate known segments with
        # flag_versions above:
        ## Note this next line is needed for looping over multiple files
        for i in flag_versions.keys():
            flag_versions[i].temp_process_ids={}
        for j in range(len(segment_md.table['segment_summary']['stream'])):
            #flag_versions_numbered[j] = {}
            seg_def_index = segment_md.table['segment_summary']['orderedcol'].index('segment_def_id')
            #print("associated seg_def_id is: "+ segment_md.table['segment_summary']['stream'][j][seg_def_index])
            (ifo,name,version) = temp_id_to_flag_version[segment_md.table['segment_summary']['stream'][j][seg_def_index]]
            seg_sum_index = segment_md.table['segment_summary']['orderedcol'].index('segment_sum_id')
            # Unneeded:
            #flag_versions[(ifo,name,version)].temporary_segment_sum_id = segment_md.table['segment_summary']['stream'][j][seg_sum_index]
            start_time_index = segment_md.table['segment_summary']['orderedcol'].index('start_time')
            end_time_index = segment_md.table['segment_summary']['orderedcol'].index('end_time')
            start_time = segment_md.table['segment_summary']['stream'][j][start_time_index]+offset
            end_time = segment_md.table['segment_summary']['stream'][j][end_time_index]+offset
            comment_index = segment_md.table['segment_summary']['orderedcol'].index('comment')
            seg_sum_comment=segment_md.table['segment_summary']['stream'][j][comment_index]
            new_seg_summary = segments.segmentlist([segments.segment(start_time,end_time)])
            flag_versions[(ifo,name,version)].appendKnown(new_seg_summary)
            # Now I need to build up the insertion_metadata dictionary for this
            # summary:
            # Now I need to associate the right process with the known
            # segments here, and put the start and end time into the
            # insertion_metadata part of the
            #  insert_history dict
            # Plan for processes and affected data:
            # Loop through segment summaries
            # If we haven't seen the associated process before, create it:
            # First, append the temp_process_id to temp_process_ids
            # Then, each temp_process_ids entry is a dictionary, where the one
            # element is start_affected time, and the other is end_affected
            # time, and later we will combine this with the correct
            # process_metadata dictionary
            process_id_index = segment_md.table['segment_summary']['orderedcol'].index('process_id')
            temp_process_id = segment_md.table['segment_summary']['stream'][j][process_id_index]
            if temp_process_id in flag_versions[(ifo,name,version)].temp_process_ids.keys():
                # We don't need to append this process metadata, as it already
                # exists We do need to extend the affected data start and stop
                # to match
                if start_time < flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start']:
                    flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start'] = start_time
                if end_time > flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop']:
                    flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop'] = end_time
            else:
                # Need to make the dictionary entry for this process_id
                if seg_sum_comment!=None:
                    flag_versions[(ifo,name,version)].provenance_url=seg_sum_comment
                else:
                    flag_versions[(ifo,name,version)].provenance_url=''
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id] = {}
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start'] = start_time
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop'] = end_time


        # Now, I need to append an insert_history element to the flag_versions
        # for this ifo,name, version, as I have the correct insertion_metadata
        # and the correct
        # process_metadata (from the process_dict earlier
        if debug:
            t1=time.time()
        for i in flag_versions.keys():
            for pid in flag_versions[i].temp_process_ids.keys():
                start = flag_versions[i].temp_process_ids[pid]['insert_data_start']
                stop = flag_versions[i].temp_process_ids[pid]['insert_data_stop']
                if new_comments:
                    flag_versions[i].flag_version_comment=process_dict[pid]['process_comment']
                insert_history_dict = {}
                try:
                    insert_history_dict['process_metadata'] = process_dict[pid]['process_metadata']
                except:
                    raise
                #    import pdb
                #    pdb.set_trace()
                insert_history_dict['insertion_metadata'] = {}
                insert_history_dict['insertion_metadata']['insert_data_stop'] = stop
                insert_history_dict['insertion_metadata']['insert_data_start'] = start
                ifo = flag_versions[i].ifo
                version = flag_versions[i].version
                name = flag_versions[i].name
                if use_new_insertion_metadata==True:
                    insert_history_dict['insertion_metadata']['comment'] = '/dq/'+'/'.join([str(ifo),str(name),str(version)])  # FIX make dq a constant string in case we ever change it
                else:
                    insert_history_dict['insertion_metadata']['uri'] = '/dq/'+'/'.join([str(ifo),str(name),str(version)])  # FIX make dq a constant string in case we ever change it
                #print(ifo,name,version)
                insert_history_dict['insertion_metadata']['timestamp'] = _UTCToGPS(time.gmtime())
                insert_history_dict['insertion_metadata']['auth_user']=process.get_username()
                #if hackDec11:
                #    # note that this only uses one insert_history...despite
                #    all that hard work to get the list right...
                #    # so this might break something...
                #    flag_versions[i].insert_history=insert_history_dict
                #else:
                #    flag_versions[i].insert_history.append(insert_history_dict)
                flag_versions[i].insert_history.append(insert_history_dict)
        
        # parse segment table and associate known segments with flag_versions
        # above:
        try:
            for j in range(len(segment_md.table['segment']['stream'])):
                #flag_versions_numbered[j] = {}
                seg_def_index = segment_md.table['segment']['orderedcol'].index('segment_def_id')
                #print("associated seg_def_id is: "+
                #    segment_md.table['segment']['stream'][j][seg_def_index])
                (ifo,name,version) = temp_id_to_flag_version[segment_md.table['segment']['stream'][j][seg_def_index]]
                #seg_sum_index = segment_md.table['segment']['orderedcol'].index('segment_sum_id')
                start_time_index = segment_md.table['segment']['orderedcol'].index('start_time')
                end_time_index = segment_md.table['segment']['orderedcol'].index('end_time')
                start_time = segment_md.table['segment']['stream'][j][start_time_index]+offset
                end_time = segment_md.table['segment']['stream'][j][end_time_index]+offset
                new_seg = segments.segmentlist([segments.segment(start_time,end_time)])
                flag_versions[(ifo,name,version)].appendActive(new_seg)
        except KeyError:
            logger.info("No segment table for this file: %s" % filename)
            if debug:
                print("No segment table for this file: %s" % filename)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    for i in flag_versions.keys():
        flag_versions[i].coalesceInsertHistory()

    if threads>1:
        # Call this after the loop over files, and we should be good to go
        concurrent=min(threads,len(i)) # Fix!!! why did I do len(i) ???
        q=Queue(concurrent*2) # Fix!!! Improvement: remove hardcoded concurrency
        for i in range(concurrent):
            t=Thread(target=threadedPatchWithFailCases, args=[q,server,debug,logger])
            t.daemon=True
            t.start()
        for i in flag_versions.values():
            i.buildFlagDictFromInsertVersion()
            #i.flagDict
            url=i.buildURL(server)
            if debug:
                print(url)
                logger.debug("json.dumps(i.flagDict):")
                logger.debug("%s"%json.dumps(i.flagDict))
            #if hackDec11:
            #    if len(i.active)==0:
            #        print("No segments for this url")
            #        continue
            q.put(i)
        q.join()
    else:
        for i in flag_versions.values():
            i.buildFlagDictFromInsertVersion()
            #i.flagDict
            url=i.buildURL(server)
            if debug:
                logger.debug("Url for the following data: %s" % url)
                #print(url)
                logger.debug("json.dumps(i.flagDict):")
                logger.debug("%s"%json.dumps(i.flagDict))
            #if hackDec11:
            #    if len(i.active)==0:
            #        print("No segments for this url")
            #        continue
            patchWithFailCases(i,url,debug,logger,testing_options)

    if debug:
        logger.debug("If we made it this far, no errors were encountered in the inserts.")
        #print("If we made it this far, no errors were encountered in the inserts.")
    ### Fix!!! Improvement: Should be more careful about error handling here.
    if debug:
        t2=time.time()
        logger.debug("Time elapsed for file %s = %d." % (filename,t2-t1))
        #print("Time elapsed for file %s = %d." % (filename,t2-t1))
    return True
