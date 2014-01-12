import sys
import dqsegdbURIFunctions
import dqsegdbClientUtils
import json
import jsonHelper
import glue
from jsonHelper import InsertFlagVersion
from urllib2 import HTTPError
import time
import json
from glue import gpstime
from glue import ldbd
from glue import segments
from glue import git_version
from glue.segmentdb import segmentdb_utils
from glue.ligolw import table
from glue.ligolw import lsctables
from glue.ligolw import ligolw
from glue.ligolw.utils import process
from glue.ligolw import types as ligolwtypes
import os
import pyRXP
import time
from dqsegdbURIFunctions import *
try:
    from lal import UTCToGPS as _UTCToGPS
except ImportError:
    # lal is optional
    # FIXME:  make it not optional
    from glue import gpstime
    _UTCToGPS = lambda utc: int(gpstime.GpsSecondsFromPyUTC(time.mktime(utc)))

programversion='0.1'
author = "Ryan Fisher"
verbose=False

def dqsegdbQueryTimes(protocol,server,ifo,name,version,include_list_string,startTime,endTime):
    """ 
    Issue query to server for ifo:name:version with start and end time
    Returns the python loaded JSON response!
    """
    queryurl=dqsegdbURIFunctions.constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime)
    result=dqsegdbURIFunctions.getDataUrllib2(queryurl)
    result_json=json.loads(result)
    return result_json,queryurl

def reportFlags(protocol,server,verbose):
    ## Construct url and issue query
    queryurl=protocol+"://"+server+"/report/flags"
    if verbose:
        print queryurl
    result=dqsegdbURIFunctions.getDataUrllib2(queryurl)
    return result

def dqsegdbCascadedQuery(protocol, server, ifo, name, include_list_string, startTime, endTime):
    """ 
    Queries server for needed flag_versions to generate the result of a
    cascaded query (was called a versionless query in S6).  

    Returns a python dictionary representing the calculated result "versionless"
    flag and also the python dictionaries (in a list) for the flag_versions
    necessary to construct the result.
    """

    #verbose=True

    ## Construct url and issue query to determine highest version from list 
    ## of versions
    versionQueryURL=dqsegdbURIFunctions.constructVersionQueryURL(protocol,server,ifo,name)
    if verbose:
        print versionQueryURL
    versionResult=dqsegdbURIFunctions.getDataUrllib2(versionQueryURL)

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
        queryurl=dqsegdbURIFunctions.constructSegmentQueryURLTimeWindow(protocol,server,ifo,name,version,include_list_string,startTime,endTime)
        if verbose:
            print queryurl
        result=dqsegdbURIFunctions.getDataUrllib2(queryurl)
        result_parsed=json.loads(result)
        jsonResults.append(result_parsed)
        # Fix!!! Executive Decision:  Should we force these intermediate results to hit disk?  
        # For now, I say yes:
        # Fix!!! Choose a better location for files to go automatically, so this can be run from other directories
        filename=queryurl.replace('/','_').split(':')[-1]+'.json'
        try:
            tmpfile=open(filename,'w')
            json.dump(result_parsed,tmpfile)
            tmpfile.close()
        except:
            print "Couldn't save partial results to disk.... continuing anyway."

    ## Construct output segments lists from multiple JSON objects
    # The jsonResults are in order of decreasing versions, 
    # thanks to the sorting above
    # This generates a results_flag object for dumping to JSON with the 
    # total_known_list across all versions, cascaded
    # and we have the total active list across all versions, cascaded
    # so we're done the math! : 
    result_flag,affected_results=dqsegdbClientUtils.calculate_versionless_result(jsonResults,startTime,endTime)
    if verbose:
        print "active segments:", result_flag['active']
        print "known segments:", result_flag['known']

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
    if uri in ['http://www.ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt',
        'http://ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt']:
        # if the XML file contains a http pointer to the ligolw DTD at CIT then
        # return a local copy to avoid any network problems
        return 'file://localhost' + os.path.join( os.environ["GLUE_PREFIX"],
          'etc/ligolw_dtd.txt' )
    else:
        # otherwise just use the uri in the file
        return uri
    

def InsertSingleDQXMLFile(filename,server='http://slwebtest.virgo.infn.it',hackDec11=True,debug=True):
    """ 
    Inserts a single dqxml file's worth of data into the DQSEGDB.
    - filename is a string filename for a DQXML file.
    - hackDec11 is used to turn off good features that the server doesn't
    yet support.
    returns True if it completes sucessfully
    """
    xmlparser = pyRXP.Parser()
    lwtparser = ldbd.LIGOLwParser()
    segment_md = ldbd.LIGOMetadata(xmlparser,lwtparser)

    if debug:
        print "Inserting file %s." % filename
    
    fh=open(filename,'r')
    
    xmltext = fh.read()
    fh.close()
    segment_md.parse(xmltext)
    #segment_md.table
    segment_md.table.keys()
    
    flag_versions_numbered = {}
    
    for j in range(len(segment_md.table['segment_definer']['stream'])):
        flag_versions_numbered[j] = {}
        for i,entry in enumerate(segment_md.table['segment_definer']['orderedcol']):
          #print j,entry,segment_md.table['segment_definer']['stream'][j][i]
          flag_versions_numbered[j][entry] = segment_md.table['segment_definer']['stream'][j][i]
    
    
    # parse process table and make a dict that corresponds with each process, where
    # the keys for the dict are like "process:process_id:1" so that we can match
    # these to the flag_versions from the segment definer in the next section
    
    # Note:  Wherever temp_ preceeds a name, it is generally an identifier field
    # from the dqxml, that is only good for the single dqxml file being parsed
    
    
    process_dict = {}
    # Going to assign process table streams to process_dict with a key matching process_id (process:process_id:0 for example)
    for j in range(len(segment_md.table['process']['stream'])):
        process_id_index = segment_md.table['process']['orderedcol'].index('process_id')
        temp_process_id = segment_md.table['process']['stream'][j][process_id_index]
        # Now we're going to assign elements to process_dict[process_id]
        process_dict[temp_process_id] = {}
        for i,entry in enumerate(segment_md.table['process']['orderedcol']):
            #print j,entry,segment_md.table['process']['stream'][j][i]
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
        else:
            process_dict[temp_process_id]['process_metadata']['process_start_timestamp'] = process_dict[temp_process_id]['start_time']
        process_dict[temp_process_id]['process_metadata']['uid'] = process_dict[temp_process_id]['username']
        process_dict[temp_process_id]['process_metadata']['args'] = [] ### Fix!!! dqxml has no args???
        process_dict[temp_process_id]['process_metadata']['pid'] = process_dict[temp_process_id]['unix_procid']
        process_dict[temp_process_id]['process_metadata']['name'] = process_dict[temp_process_id]['program']
        process_dict[temp_process_id]['process_metadata']['fqdn'] = process_dict[temp_process_id]['node'] ### Fix!!! 
        #   not really fqdn, just the node name
    
    # So now I have process_dict[temp_process_id]['process_metadata'] for each
    # process_id, and can add it to a flag version when it uses it;  really I
    # should group it with the segment summary info because that has the
    # insertion_metadata start and stop time
    
    ### Fix!!! Get the args from the *other* process table... yikes
    
    
    flag_versions = {}
    temp_id_to_flag_version = {}
    for i in flag_versions_numbered.keys():
        ifo = flag_versions_numbered[i]['ifos']
        name = flag_versions_numbered[i]['name']
        version = flag_versions_numbered[i]['version']
        flag_versions[(ifo,name,version)] = InsertFlagVersion(ifo,name,version)
        flag_versions[(ifo,name,version)].temporary_definer_id = flag_versions_numbered[i]['segment_def_id']
        # if hasattr(flag_versions[(ifo,name,version)],'temporary_process_id') and
        #      flag_versions[(ifo,name,version)].temporary_process_id != 
        #      flag_versions_numbered[i]['process_id']:
        #    print "Multiple processes for the same flag-version;  Haven't handled
        #    this case yet!"
        #    raise ValueError
        flag_versions[(ifo,name,version)].temporary_process_id = flag_versions_numbered[i]['process_id']
        flag_versions[(ifo,name,version)].flag_comment=str(flag_versions_numbered[i]['comment'])
        flag_versions[(ifo,name,version)].version_comment=str(flag_versions_numbered[i]['comment'])
    
        #flag_versions[(ifo,name,version)]['metadata'][]
        temp_id_to_flag_version[flag_versions[(ifo,name,version)].temporary_definer_id] = (ifo,name,version)
    
    
    # ways to solve the metadata problem:
    # Associate each insertion_metadata block with a process, then group them and
    # take the min insert_data_start and max insert_data_stop
    
    
    # parse segment_summary table and associate known segments with flag_versions
    # above:
    
    for j in range(len(segment_md.table['segment_summary']['stream'])):
        #flag_versions_numbered[j] = {}
        seg_def_index = segment_md.table['segment_summary']['orderedcol'].index('segment_def_id')
        #print "associated seg_def_id is: "+ segment_md.table['segment_summary']['stream'][j][seg_def_index]
        (ifo,name,version) = temp_id_to_flag_version[segment_md.table['segment_summary']['stream'][j][seg_def_index]]
        seg_sum_index = segment_md.table['segment_summary']['orderedcol'].index('segment_sum_id')
        # Unneeded:
        #flag_versions[(ifo,name,version)].temporary_segment_sum_id = segment_md.table['segment_summary']['stream'][j][seg_sum_index]
        start_time_index = segment_md.table['segment_summary']['orderedcol'].index('start_time')
        end_time_index = segment_md.table['segment_summary']['orderedcol'].index('end_time')
        start_time = segment_md.table['segment_summary']['stream'][j][start_time_index]
        end_time = segment_md.table['segment_summary']['stream'][j][end_time_index]
        new_seg_summary = segments.segmentlist([segments.segment(start_time,end_time)])
        flag_versions[(ifo,name,version)].appendKnown(new_seg_summary)
        # Now I need to build up the insertion_metadata dictionary for this summary:
        # Now I need to associate the right process with the known segments here,
        #  and put the start and end time into the insertion_metadata part of the
        #  insert_history dict
        # Plan for processes and affected data:
        # Loop through segment summaries
        # If we haven't seen the associated process before, create it:
        # First, append the temp_process_id to temp_process_ids
        # Then, each temp_process_ids entry is a dictionary, where the one
        # element is start_affected time, and the other is end_affected time, and
        # later we will combine this with the correct process_metadata dictionary
        process_id_index = segment_md.table['segment_summary']['orderedcol'].index('process_id')
        temp_process_id = segment_md.table['segment_summary']['stream'][j][process_id_index]
        if temp_process_id in flag_versions[(ifo,name,version)].temp_process_ids.keys():
            # We don't need to append this process metadata, as it already exists
            # We do need to extend the affected data start and stop to match
            if start_time < flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start']:
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start'] = start_time
            if end_time > flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop']:
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop'] = end_time
        else:
            # Need to make the dictionary entry for this process_id
            flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id] = {}
            flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start'] = start_time
            flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop'] = end_time
    
    
    # Now, I need to append an insert_history element to the flag_versions for this
    # ifo,name, version, as I have the correct insertion_metadata and the correct
    # process_metadata (from the process_dict earlier
    if debug:
        t1=time.time()
    for i in flag_versions.keys():
        for pid in flag_versions[i].temp_process_ids.keys():
            start = flag_versions[i].temp_process_ids[pid]['insert_data_start']
            stop = flag_versions[i].temp_process_ids[pid]['insert_data_stop']
            insert_history_dict = {}
            insert_history_dict['process_metadata'] = process_dict[pid]['process_metadata']
            insert_history_dict['insertion_metadata'] = {}
            insert_history_dict['insertion_metadata']['insert_data_stop'] = stop
            insert_history_dict['insertion_metadata']['insert_data_start'] = start
            ifo = flag_versions[i].ifo
            version = flag_versions[i].version
            name = flag_versions[i].name
            insert_history_dict['insertion_metadata']['uri'] = '/dq/'+'/'.join([str(ifo),str(name),str(version)])
            #print ifo,name,version
            insert_history_dict['insertion_metadata']['timestamp'] = _UTCToGPS(time.gmtime())
            insert_history_dict['insertion_metadata']['auth_user']=process.get_username()
            if hackDec11:
                # note that this only uses one insert_history...despite all that hard work to get the list right...
                # so this might break something...
                flag_versions[i].insert_history=insert_history_dict
            else:
                flag_versions[i].insert_history.append(insert_history_dict)
    
    # parse segment table and associate known segments with flag_versions above:
    
    for j in range(len(segment_md.table['segment']['stream'])):
        #flag_versions_numbered[j] = {}
        seg_def_index = segment_md.table['segment']['orderedcol'].index('segment_def_id')
        #print "associated seg_def_id is: "+ 
        #    segment_md.table['segment']['stream'][j][seg_def_index]
        (ifo,name,version) = temp_id_to_flag_version[segment_md.table['segment']['stream'][j][seg_def_index]]
        #seg_sum_index = segment_md.table['segment']['orderedcol'].index('segment_sum_id')
        start_time_index = segment_md.table['segment']['orderedcol'].index('start_time')
        end_time_index = segment_md.table['segment']['orderedcol'].index('end_time')
        start_time = segment_md.table['segment']['stream'][j][start_time_index]
        end_time = segment_md.table['segment']['stream'][j][end_time_index]
        new_seg = segments.segmentlist([segments.segment(start_time,end_time)])
        flag_versions[(ifo,name,version)].appendActive(new_seg)
    
    for i in flag_versions.values():
        i.buildFlagDictFromInsertVersion()
        #i.flagDict
        url=i.buildURL(server)
        print url
        #if hackDec11:
        #    if len(i.active)==0:
        #        print "No segments for this url"
        #        continue
        patchWithFailCases(i,url)
    print "If we made it this far, no errors were encountered in the inserts."
    ### Fix!!! Should be more careful about error handling here.
    if debug:
        t2=time.time()
        print "Time elapsed for file %s = %d." % (filename,t2-t1)
    return True

def patchWithFailCases(i,url,debug=True):
        try:
            #patch to the flag/version
            if debug:
                print "Trying to patch alone for url: %s" % url 
            patchDataUrllib2(url,json.dumps(i.flagDict))
            if debug:
                print "Patch alone succeeded for %s" % url
        except HTTPError as e:
            if e.code!=404:
                raise e
            try: 
                #put to version
                if debug:
                    print "Trying to put alone for %s" % url
                putDataUrllib2(url,json.dumps(i.flagDict))
                if debug:
                    print "Put alone succeeded for %s" % url
            except HTTPError as ee:
                if ee.code!=404:
                    raise ee
                #put to flag
                suburl='/'.join(url.split('/')[:-1])
                if debug:
                    print "Trying to PUT flag and version to: "+suburl
                putDataUrllib2(suburl,json.dumps(i.flagDict))
                #put to version
                putDataUrllib2(url,json.dumps(i.flagDict))
                if debug:
                    print "Had to PUT flag and version"


def threadedPatchWithFailCases(q,server,debug):
    """ Used by threaded implementation of InsertSingleDQXMLFileThreaded """
    while True:
        i=q.get()
        url=i.buildURL(server)
        try:
            patchWithFailCases(i,url,debug)
        except KeyboardInterrupt:
            print "interrupted by user!"
            sys.exit(1)
        q.task_done()

def setupSegment_md(filename,xmlparser,lwtparser,debug):
    segment_md = ldbd.LIGOMetadata(xmlparser,lwtparser)

    if debug:
        print "Inserting file %s." % filename
    fh=open(filename,'r')
    xmltext = fh.read()
    fh.close()
    segment_md.parse(xmltext)
    if debug:
        #segment_md.table
        segment_md.table.keys()
    return segment_md

def InsertMultipleDQXMLFileThreaded(filenames,logger,server='http://slwebtest.virgo.infn.it',hackDec11=True,debug=True,threads=20):
    """ 
    Inserts multiple dqxml files of data into the DQSEGDB.
    - filename is a list of string filenames for  DQXML files.
    - hackDec11 is used to turn off good features that the server doesn't
    yet support.
    returns True if it completes sucessfully
    """
    from threading import Thread
    from Queue import Queue
    import sys

    xmlparser = pyRXP.Parser()
    lwtparser = ldbd.LIGOLwParser()
    
    flag_versions = {}
    
    # flag_versions, filename, server, hackDec11, debug are current variables

    # This next bunch of code is specific to a given file:
    if len(filenames)<1:
        print "Empty file list sent to InsertMultipleDQXMLFileThreaded"
        raise ValueError
    for filename in filenames:
    
        segment_md = setupSegment_md(filename,xmlparser,lwtparser,debug)

        # segment_md, flag_versions, filename, server, hackDec11, debug are current variables
        
        flag_versions_numbered = {}
        
        for j in range(len(segment_md.table['segment_definer']['stream'])):
            flag_versions_numbered[j] = {}
            for i,entry in enumerate(segment_md.table['segment_definer']['orderedcol']):
              #print j,entry,segment_md.table['segment_definer']['stream'][j][i]
              flag_versions_numbered[j][entry] = segment_md.table['segment_definer']['stream'][j][i]
        
        
        # parse process table and make a dict that corresponds with each process, where
        # the keys for the dict are like "process:process_id:1" so that we can match
        # these to the flag_versions from the segment definer in the next section
        
        # Note:  Wherever temp_ preceeds a name, it is generally an identifier field
        # from the dqxml, that is only good for the single dqxml file being parsed
        
        
        process_dict = {}
        # Going to assign process table streams to process_dict with a key matching process_id (process:process_id:0 for example)
        for j in range(len(segment_md.table['process']['stream'])):
            process_id_index = segment_md.table['process']['orderedcol'].index('process_id')
            temp_process_id = segment_md.table['process']['stream'][j][process_id_index]
            # Now we're going to assign elements to process_dict[process_id]
            process_dict[temp_process_id] = {}
            for i,entry in enumerate(segment_md.table['process']['orderedcol']):
                #print j,entry,segment_md.table['process']['stream'][j][i]
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
            else:
                process_dict[temp_process_id]['process_metadata']['process_start_timestamp'] = process_dict[temp_process_id]['start_time']
            process_dict[temp_process_id]['process_metadata']['uid'] = process_dict[temp_process_id]['username']
            process_dict[temp_process_id]['process_metadata']['args'] = [] ### Fix!!! dqxml has no args???
            process_dict[temp_process_id]['process_metadata']['pid'] = process_dict[temp_process_id]['unix_procid']
            process_dict[temp_process_id]['process_metadata']['name'] = process_dict[temp_process_id]['program']
            process_dict[temp_process_id]['process_metadata']['fqdn'] = process_dict[temp_process_id]['node'] ### Fix!!! 
            #   not really fqdn, just the node name
        
        # So now I have process_dict[temp_process_id]['process_metadata'] for each
        # process_id, and can add it to a flag version when it uses it;  really I
        # should group it with the segment summary info because that has the
        # insertion_metadata start and stop time
        
        ### Fix!!! Get the args from the *other* process table... yikes
        
        temp_id_to_flag_version = {}
        
        for i in flag_versions_numbered.keys():
            ifo = flag_versions_numbered[i]['ifos']
            name = flag_versions_numbered[i]['name']
            version = flag_versions_numbered[i]['version']
            if (ifo,name,version) not in flag_versions.keys():
                flag_versions[(ifo,name,version)] = InsertFlagVersion(ifo,name,version)
                flag_versions[(ifo,name,version)].flag_comment=str(flag_versions_numbered[i]['comment'])
                flag_versions[(ifo,name,version)].version_comment=str(flag_versions_numbered[i]['comment'])
            flag_versions[(ifo,name,version)].temporary_definer_id = flag_versions_numbered[i]['segment_def_id']
            flag_versions[(ifo,name,version)].temporary_process_id = flag_versions_numbered[i]['process_id']
            # Populate reverse lookup dictionary:
            temp_id_to_flag_version[flag_versions[(ifo,name,version)].temporary_definer_id] = (ifo,name,version)
        
        
        # ways to solve the metadata problem:
        # Associate each insertion_metadata block with a process, then group them and
        # take the min insert_data_start and max insert_data_stop
        
        
        # parse segment_summary table and associate known segments with flag_versions
        # above:
        ## Note this next line is needed for looping over multiple files
        for i in flag_versions.keys():
            flag_versions[i].temp_process_ids={}
        for j in range(len(segment_md.table['segment_summary']['stream'])):
            #flag_versions_numbered[j] = {}
            seg_def_index = segment_md.table['segment_summary']['orderedcol'].index('segment_def_id')
            #print "associated seg_def_id is: "+ segment_md.table['segment_summary']['stream'][j][seg_def_index]
            (ifo,name,version) = temp_id_to_flag_version[segment_md.table['segment_summary']['stream'][j][seg_def_index]]
            seg_sum_index = segment_md.table['segment_summary']['orderedcol'].index('segment_sum_id')
            # Unneeded:
            #flag_versions[(ifo,name,version)].temporary_segment_sum_id = segment_md.table['segment_summary']['stream'][j][seg_sum_index]
            start_time_index = segment_md.table['segment_summary']['orderedcol'].index('start_time')
            end_time_index = segment_md.table['segment_summary']['orderedcol'].index('end_time')
            start_time = segment_md.table['segment_summary']['stream'][j][start_time_index]
            end_time = segment_md.table['segment_summary']['stream'][j][end_time_index]
            new_seg_summary = segments.segmentlist([segments.segment(start_time,end_time)])
            flag_versions[(ifo,name,version)].appendKnown(new_seg_summary)
            # Now I need to build up the insertion_metadata dictionary for this summary:
            # Now I need to associate the right process with the known segments here,
            #  and put the start and end time into the insertion_metadata part of the
            #  insert_history dict
            # Plan for processes and affected data:
            # Loop through segment summaries
            # If we haven't seen the associated process before, create it:
            # First, append the temp_process_id to temp_process_ids
            # Then, each temp_process_ids entry is a dictionary, where the one
            # element is start_affected time, and the other is end_affected time, and
            # later we will combine this with the correct process_metadata dictionary
            process_id_index = segment_md.table['segment_summary']['orderedcol'].index('process_id')
            temp_process_id = segment_md.table['segment_summary']['stream'][j][process_id_index]
            if temp_process_id in flag_versions[(ifo,name,version)].temp_process_ids.keys():
                # We don't need to append this process metadata, as it already exists
                # We do need to extend the affected data start and stop to match
                if start_time < flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start']:
                    flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start'] = start_time
                if end_time > flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop']:
                    flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop'] = end_time
            else:
                # Need to make the dictionary entry for this process_id
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id] = {}
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_start'] = start_time
                flag_versions[(ifo,name,version)].temp_process_ids[temp_process_id]['insert_data_stop'] = end_time
        
        
        # Now, I need to append an insert_history element to the flag_versions for this
        # ifo,name, version, as I have the correct insertion_metadata and the correct
        # process_metadata (from the process_dict earlier
        if debug:
            t1=time.time()
        for i in flag_versions.keys():
            for pid in flag_versions[i].temp_process_ids.keys():
                start = flag_versions[i].temp_process_ids[pid]['insert_data_start']
                stop = flag_versions[i].temp_process_ids[pid]['insert_data_stop']
                insert_history_dict = {}
                try:
                    insert_history_dict['process_metadata'] = process_dict[pid]['process_metadata']
                except:
                    import pdb
                    pdb.set_trace()
                insert_history_dict['insertion_metadata'] = {}
                insert_history_dict['insertion_metadata']['insert_data_stop'] = stop
                insert_history_dict['insertion_metadata']['insert_data_start'] = start
                ifo = flag_versions[i].ifo
                version = flag_versions[i].version
                name = flag_versions[i].name
                insert_history_dict['insertion_metadata']['uri'] = '/dq/'+'/'.join([str(ifo),str(name),str(version)])
                #print ifo,name,version
                insert_history_dict['insertion_metadata']['timestamp'] = _UTCToGPS(time.gmtime())
                insert_history_dict['insertion_metadata']['auth_user']=process.get_username()
                #if hackDec11:
                #    # note that this only uses one insert_history...despite all that hard work to get the list right...
                #    # so this might break something...
                #    flag_versions[i].insert_history=insert_history_dict
                #else:
                #    flag_versions[i].insert_history.append(insert_history_dict)
                flag_versions[i].insert_history.append(insert_history_dict)
        
        # parse segment table and associate known segments with flag_versions above:
        try:
            for j in range(len(segment_md.table['segment']['stream'])):
                #flag_versions_numbered[j] = {}
                seg_def_index = segment_md.table['segment']['orderedcol'].index('segment_def_id')
                #print "associated seg_def_id is: "+ 
                #    segment_md.table['segment']['stream'][j][seg_def_index]
                (ifo,name,version) = temp_id_to_flag_version[segment_md.table['segment']['stream'][j][seg_def_index]]
                #seg_sum_index = segment_md.table['segment']['orderedcol'].index('segment_sum_id')
                start_time_index = segment_md.table['segment']['orderedcol'].index('start_time')
                end_time_index = segment_md.table['segment']['orderedcol'].index('end_time')
                start_time = segment_md.table['segment']['stream'][j][start_time_index]
                end_time = segment_md.table['segment']['stream'][j][end_time_index]
                new_seg = segments.segmentlist([segments.segment(start_time,end_time)])
                flag_versions[(ifo,name,version)].appendActive(new_seg)
        except KeyError:
            logger.info("No segment table for this file: %s" % filename)
            if debug:
                print "No segment table for this file: %s" % filename
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    if threads>1:
        # Call this after the loop over files, and we should be good to go
        concurrent=min(threads,len(i))
        q=Queue(concurrent*2) # Fix!!! hardcoded concurrency
        for i in range(concurrent):
            t=Thread(target=threadedPatchWithFailCases, args=[q,server,debug])
            t.daemon=True
            t.start()
        for i in flag_versions.values():
            i.buildFlagDictFromInsertVersion()
            #i.flagDict
            url=i.buildURL(server)
            if debug:
                print url
            #if hackDec11:
            #    if len(i.active)==0:
            #        print "No segments for this url"
            #        continue
            q.put(i)
        q.join()
    else:
        for i in flag_versions.values():
            i.buildFlagDictFromInsertVersion()
            #i.flagDict
            url=i.buildURL(server)
            if debug:
                print url
            #if hackDec11:
            #    if len(i.active)==0:
            #        print "No segments for this url"
            #        continue
            patchWithFailCases(i,url,debug)

    if debug:
        print "If we made it this far, no errors were encountered in the inserts."
    ### Fix!!! Should be more careful about error handling here.
    if debug:
        t2=time.time()
        print "Time elapsed for file %s = %d." % (filename,t2-t1)
    return True
