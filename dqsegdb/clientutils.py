from glue import segments
import json
import apicalls
import jsonhelper


def include_exclude_caller(includedList,excludedList,startTime,endTime,protocol, server,include_list_string):
    ## Form the results for included and excluded flags
    includedJSON=[]
    includedURL=[]
    excludedJSON=[]
    excludedURL=[]
    if len(includedList) > 0:
        for entry in includedList:
            ifo=entry[0]
            name=entry[1]
            version=entry[2]
            result,queryurl=apicalls.dqsegdbQueryTimes(protocol,server,ifo,name,version,include_list_string,startTime,endTime)
            includedURL.append(queryurl)
            includedJSON.append(result)
    if len(excludedList) > 0:
        for entry in excludedList:
            ifo=entry[0]
            name=entry[1]
            version=entry[2]
            result,queryurl=apicalls.dqsegdbQueryTimes(protocol,server,ifo,name,include_list_string,startTime,endTime)
            excludedURL.append(queryurl)
            excludedJSON.append(result)

    return includedJSON,includedURL,excludedJSON,excludedURL,ifo

def calculate_combined_result(includedJSON,excludedJSON,startTime,endTime,ifo):
    """ Calculate the result of the union of the active times for the included flag less the intersection of that result with the union of the excluded flags

    Inputs are 2 lists of python dictionaries representing the JSON (already have run json.loads() on the JSON), a start time, and end time, and the ifo name (it doesn't make sense to include/exclude across multiple ifos)
    """
    total_active_list=segments.segmentlist([]) 
    for flag in includedJSON: 
        #result=json.loads(flag) 
        #flagDict=result['flags'][0] 
        active_list=flag['active'] 
        active_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in active_list]) 
        total_active_list=total_active_list+active_segments 
        total_active_list.coalesce()
    for flag in excludedJSON: 
        #result=json.loads(flag) 
        #flagDict=result['flags'][0] 
        active_list=flag['active'] 
        active_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in active_list]) 
        total_active_list=total_active_list-active_segments 
        total_active_list.coalesce()
    # Now, total_active_list contains a segmentlist object with segments spanning the expected result     # includedJSON and excludedJSON contain lists of JSON text blobs (not parsed with json.loads yet) 
 
    ## Note:  About known segments for the result:  We just report the start and end time of the period queried!  If you wanted to report the actual validity of multiple segments, it's somewhat undefined if the excluded ones and/or some of the included flags aren't known about for a time when the included ones are;  Technically since exclusion trumps all inclusions, if an excluded segment is known and active at any given time, the result is known for that time explicitly. 
    result_known_segment_list=segments.segmentlist([segments.segment(startTime,endTime)]) 
 
    ## Now we have to build the JSON for this flag 
    # JSON flag objects looks like this (each is a dictionary!): 
    #  { 
    #    "ifo" : "ifo", 
    #    "name" : "flag", 
    #    "version" : n, 
    #    "comment" : "description",     #    "provenance_url" : "aLog URL", 
    #    "deactivated" : false|true, 
    #    "active_indicates_ifo_badness" : true|false|null, 
    #    // known segments returned for both /active and /known URIs, no segments are returned for the /metadata or /report/flags queries 
    #    // aka S6 summary segments 
    #    "known" : [ [ts,te], [ts,te], ... ] 
    #    // active segments returned only for /active URI: 
    #    "active" : [ [ts,te], [ts,te], ... ] 
    #    // \textcolor{red}{Comment: or "segment" : [ [ts,te,value], [ts,te,value], ...] (where value can be -1,0 or +1)} 
    #    // inactive == (known - active) 
    #    // unknown == (all_time - known) 
    #  }, 
    ## Make the json-ready flag dictionary for the combined result: 
    ifo=ifo # replicating old behavoir from ligolw_segment_query 
    # Note: This just uses the ifo of the last excluded flag! 
    name='RESULT' 
    version=1 
    known_segments=result_known_segment_list 
    active_segments=total_active_list 
    result_flag=jsonhelper.buildFlagDict(ifo,name,version,known_segments,active_segments)
    return result_flag

def calculate_versionless_result(jsonResults,startTime,endTime):
    ## Construct output segments lists from multiple JSON objects    
    ## The jsonResults are expected to be in order of decreasing versions
    debug=False
    active_results={}
    segment_known_results={}
    affected_results={}
    total_active_list=segments.segmentlist([])
    total_query_time=segments.segmentlist([segments.segment(startTime,endTime)])
    total_known_list=segments.segmentlist([])
    for resultin in jsonResults:
        #result=json.loads(resultin)
        result=resultin
        # old : flagDict=result['flags'][0] # Our queries above each return 1 flag
        version = int(result['version'])
        deactivated_state=result['metadata']['deactivated']
        if str(deactivated_state) in ["False","false"]:
            known_list=result['known']
            known_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in known_list]) # make a segment list object to do arithmetic
            known_segments.coalesce()
            segment_known_results[version]=known_segments
            active_list=result['active']
            active_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in active_list]) # make a segment list object to do arithmetic
            active_segments.coalesce()
            active_results[version]=active_segments
            if debug:
                print "Active results for version %d" % version
                print active_results[version]
            # Now I have 2 dictionaries of known and active segments with versions as keys in case I want/need them later...
            # This next step might seem a bit confusing:
            # We need to take the active segments for this version only during times that were not known by higher segment versions
            # Thus we need to take the intersection (& operator) of the unknown segments across all higher versions with the known segments for this version, then take the intersection of that result with the active segments for this version, and then add that to the current list of total active segments... phew:
            total_active_list |= (total_query_time-total_known_list)&known_segments&active_segments
            if debug:
                import pdb
                print "Running pdb to see what is in total_active_list"
                pdb.set_trace()
            total_active_list.coalesce()
            # The S6 clients want to know about the range of times affected by a given version explicitly, so those are calculated here:
            affected_results[version]=(total_query_time-total_known_list)&known_segments
            # Note that the order matters here!  we use the total_known_list from the previous iteration of the loop step to figure out which active segments to use in this iteration of the loop, so the above line must come before the next
            total_known_list |= known_segments
            total_known_list.coalesce()
    
    ifo=result['ifo']
    name='RESULT' # Fix!!! Executive decision to make this clear that this is not a specific IFO:FLAG:VERSION resource, but rather a contrived result
    version=1 # Fix!!! Executive decision to make this match what old clients expect
    # I would prefer that this is more clear that this is not a specific IFO:FLAG:VERSION resource, but rather a contrived result, possibly by making it version 0
    total_active_list.coalesce()
    total_known_list.coalesce()
    result_flag=jsonhelper.buildFlagDict(ifo,name,version,total_known_list,total_active_list)
    return result_flag,affected_results





