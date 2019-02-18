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
from ligo import segments


################################################################################
#
#  This module should contain functions that load in the standard JSON formats
#  returned by the dqsegdb, and parse them into expected python objects.  Thus
#  far, the only anticipated function will be to convert several json flag
#  objects into one xml file.  The other JSON parsing for segment computations
#  is trivial, as shown here:
#
# Example from a file:
#[rpfisher@sugar-dev2 ~]$ cat test_jsonnocomments.json
#{
# "meta": {
#    "query_uri" : "uri",
#    "query_time" : 1056789101,
#    "query_start" : 1056788101,
#    "query_end" : 1056789101
#    },
#  "resource_type" : ["resource_uri_1", "resource_uri_2"]
#}
#python:
#>>> blah=open('test_jsonnocomments.json','r')
#>>> a=json.load(blah)
#
################################################################################

def convertJSONtoXML(json_response):
    """
    Incomplete!!
    Converts a standard JSON response from the dqsegdb server into a
    DQXML format.

    """
    # Assumes JSON input as defined in API doc (dictionary containing keys
    # "meta" and "flags")
    data=json.loads(json_response)
    metadata=data['meta']
    flag_list=data['flags']
    flags=[]
    for flag in flag_list:
        ifo=flag['ifo']
        name=flag['name']
        version=flag['version']
        comment=flag['comment']
        provenance_url=flag['provenance_url']
        deactivated=flag['deactivated']
        active_indicates_ifo_badness=flag['active_indicates_ifo_badness']
        known_segments=convert_json_list_to_segmentlist(flag['known'])
        active_segments=convert_json_list_to_segmentlist(flag['active'])
        flags.append(stuff)  ### Fix!!! : Need to make this a class with elements probably to keep things organized.
        ### Alternatively, I could just keep the dictionary and at least replace the json list segments with segmentlist objects?
        ### What's the use case?  I need to put the information about this flag into the DQXML file:  So, I should look at what the old tools did with the information before writing it out to the file/screen!


    ### Fix!!! Incomplete

################################################################################
#
#  Helper function to build a flag_version dictionary object for JSON output
#
################################################################################

def buildFlagDict(ifo,name,version,known_segments,active_segments):
    """
    Helper function to build a flag_version dictionary for JSON production.

    known_segments and active_segments are assumed to be segmentlist objects
    Note that this currently does not generate a false "query_metadata" block
    """
    flag={}
    flag['ifo']=ifo
    flag['name']=name
    flag['version']=version
    flag['known']=convert_segmentlist_to_json(known_segments)
    flag['active']=convert_segmentlist_to_json(active_segments)
    return flag



class FlagVersion(object):
    """
    Class to set up a flag version object for parsing into JSON
    """
    def __init__(self,ifo,name,version):
        self.known=segments.segmentlist([])
        self.active=segments.segmentlist([])
#        self.metadata={}
        self.flagDict={}
        self.ifo=ifo
        self.name=name
        self.version=version
    def buildURL(self,server=''):
        url=server+'/dq/'+'/'.join([str(self.ifo),str(self.name),str(self.version)])
        return url
    def appendKnown(self,known_segments):
        """ Appends a segmentlist of known segments to the existing known
        segments for the object, and coalesces.
        """
        # known_segments must be a segmentlist object
        self.known=self.known+known_segments
        self.known.coalesce()
    def appendActive(self,active_segments):
        """ Appends a segmentlist of active segments to the existing active
        segments for the object, and coalesces.
        """
        # active_segments must be a segmentlist object
        self.active=self.active+active_segments
        self.active.coalesce()

    def buildFlagDictFromVersion(self):
        self.flagDict=buildFlagDict(self.ifo,self.name,self.version,self.known,self.active)

class PatchFlagVersion(FlagVersion):
    __doc__ = FlagVersion.__doc__ + """
    Class to extend basic flag version class to include insert_history
    """
    def __init__(self,ifo,name,version,hackDec11=False):
        self.known=segments.segmentlist([])
        self.active=segments.segmentlist([])
#        self.metadata={}
        self.flagDict={}
        self.ifo=ifo
        self.name=name
        self.version=version
        self.temp_process_ids={} # Used to hold the data
        #                         # associated with a process_id
        if hackDec11:
            self.insert_history={}
        else:
            self.insert_history=[] # holds the process_metadatas and insertion_metadatas    # Note that this assumes that proper dictionaries are appended to this list
        #self.process_metadata={}
        # self.process_metadata.keys() should be process_start_timestamp(or process_start_time for old server hack for Dec 11),uid,args,pid,fqdn,name
        #self.insertion_metadata={}
        # self.insertion_metadata.keys() should be insert_data_stop,insert_data_start,uri,timestamp,auth_user,insert_data_start
    def buildFlagDictFromPatchVersion(self):
        self.buildFlagDictFromVersion()
        self.flagDict['insert_history']=self.insert_history
    def coalesceInsertHistory(self):
        final_history=[]
        first=True
        debug=False
        if debug:
            print("Printing insert history")
            print(self.insert_history)
            print("length:")
            print(len(self.insert_history))

        for i in self.insert_history:
            if debug:
                print("self.insert_history element:")
                print(i)
            if first:
                final_history.append(i)
                first = False
                if debug:
                    print("first!")
            else:
                process_name=i['process_metadata']['name']
                process_pid=i['process_metadata']['pid']
                process_uid=i['process_metadata']['uid']
                matched=False
                for j in final_history:
                    if debug:
                        print("printing i")
                        print(i)
                        print("printing j for comparison")
                        print(j)
                    if process_name==j['process_metadata']['name'] and process_pid==j['process_metadata']['pid'] and process_uid==j['process_metadata']['uid']:  # FIX!!! Should we sort these by time order and then match end time of file_history element to start_time of insert_history element?
                        j['insertion_metadata']['insert_data_stop']=max(j['insertion_metadata']['insert_data_stop'],i['insertion_metadata']['insert_data_stop'])
                        j['insertion_metadata']['insert_data_start']=min(j['insertion_metadata']['insert_data_start'],i['insertion_metadata']['insert_data_start'])
                        if debug:
                            print("i matched j")
                            matched=True
                    else:
                        if debug:
                            print("i didn't match j")
                if not matched:
                    final_history.append(i)
        if debug:
            print("Printing final history:")
            print(final_history)
            print(len(final_history))
        self.insert_history=final_history


class InsertFlagVersion(PatchFlagVersion):
    __doc__ = PatchFlagVersion.__doc__ + """
    Adds metadata for initial inserts
    """
    def __init__(self,ifo,name,version):
        super(InsertFlagVersion, self).__init__(ifo,name,version)
        self.metadata={}
        self.flag_version_comment=""
        self.flag_description=""
        self.provenance_url=""
        self.deactivated=False
        self.active_indicates_ifo_badness=True
    def buildFlagDictFromInsertVersion(self):
        ### Fix!!! I think I should make this a function that takes the self.x arguments
        ### as inputs and returns a modified flagDict object, so I can use it other
        ### places
        self.buildFlagDictFromPatchVersion()
        self.flagDict['metadata']={}
        self.flagDict['metadata']['flag_description']=self.flag_description
        self.flagDict['metadata']['flag_version_comment']=self.flag_version_comment
        self.flagDict['metadata']['further_info_url']=self.provenance_url
        self.flagDict['metadata']['deactivated']=self.deactivated
        self.flagDict['metadata']['active_indicates_ifo_badness']=self.active_indicates_ifo_badness

class InsertFlagVersionOld(PatchFlagVersion):
    __doc__ = PatchFlagVersion.__doc__ + """
    Adds metadata for initial inserts
    """
    def __init__(self,ifo,name,version):
        super(InsertFlagVersionOld, self).__init__(ifo,name,version)
        self.metadata={}
        self.version_comment=""
        self.flag_comment=""
        self.provenance_url=""
        self.deactivated=False
        self.active_indicates_ifo_badness=True
    def buildFlagDictFromInsertVersion(self):
        ### Fix!!! I think I should make this a function that takes the self.x arguments
        ### as inputs and returns a modified flagDict object, so I can use it other
        ### places
        self.buildFlagDictFromPatchVersion()
        self.flagDict['metadata']={}
        self.flagDict['metadata']['flag_comment']=self.flag_comment
        self.flagDict['metadata']['version_comment']=self.version_comment
        self.flagDict['metadata']['provenance_url']=self.provenance_url
        self.flagDict['metadata']['deactivated']=self.deactivated
        self.flagDict['metadata']['active_indicates_ifo_badness']=self.active_indicates_ifo_badness


################################################################################
#
#  Helper functions to convert segmentlist to json list of lists type object
#  and vice versa
#
################################################################################

def convert_segmentlist_to_json(segmentlist_input):
    """
    Helper function used to convert segmentlist to json list of lists type
    object.
    """
    json_list=[[x[0],x[1]] for x in segmentlist_input]
    return json_list

def convert_json_list_to_segmentlist(jsonlist):
     """
     Helper function used to convert json list of lists type object to a
     segmentlist object
     """
     segment_list=segments.segmentlist([segments.segment(x[0],x[1]) for x in jsonlist])
     return segment_list

################################################################################
#
#  Conversions from JSON to user requested formats
#
################################################################################

def generated_vdb_ascii(json_str,filepath):
    res_dict=json.loads(json_str)
    active_list=res_dict['active']
    active_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in active_list])
    known_list=res_dict['known']
    known_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in known_list])
    query_start=res_dict['query_information']['start']
    query_stop=res_dict['query_information']['end']
    if query_start!=0 and query_stop!=0:
        requested_span=segments.segmentlist([segments.segment(query_start,query_stop)])
    else:
        requested_span=segments.segmentlist([segments.segment(0,9999999999)])
    active_segments_string=',1 \n'.join([str(i[0])+","+str(i[1]) for i in active_segments])+",1 \n"
    unknown_segments=requested_span-known_segments
    unknown_segments_string=',-1 \n'.join([str(i[0])+","+str(i[1]) for i in unknown_segments])+",-1 \n"
    known_not_active_segments=known_segments-active_segments
    known_not_active_segments_string=',0 \n'.join([str(i[0])+","+str(i[1]) for i in known_not_active_segments])+",0 \n"
    output_fileh=open(filepath,'w+')
    query_info_string=json.dumps(res_dict['query_information'], indent=1)
    output_fileh.writelines(query_info_string)
    output_fileh.write('\n')
    output_fileh.writelines(active_segments_string)
    output_fileh.writelines(unknown_segments_string)
    output_fileh.writelines(known_not_active_segments_string)
    output_fileh.close()
    return filepath

def generated_ascii(json_str,filepath):
    res_dict=json.loads(json_str)
    active_list=res_dict['active']
    active_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in active_list])
    active_segments_string='\n'.join([str(i[0])+","+str(i[1]) for i in active_segments])
    output_fileh=open(filepath,'w+')
    output_fileh.writelines(active_segments_string)
    output_fileh.close()
    return filepath


################################################################################
#
#  Parse basic list results json objects:
#  Example from API Document:
#  {
#   "meta": {
#      "query_uri" : "uri",
#      "query_time" : 1056789101,
#      "query_start" : 1056788101,
#      "query_end" : 1056789101
#      },
#    "resource_type" : ["resource_uri_1", "resource_uri_2"]
#  }
#
#  Fix!!! NOTE: I just realized that the above format isn't very programmatic:  you
#  can't look for a key that will tell you what you are looking at, e.g. the
#  resource_type gets replaced by "version", but there is no key with a value
#  of "version".  Having that last part would make for cleaner parsing of
#  results.
#
################################################################################

################################################################################
#
# Basic Insert Example:
# {
#   "insert_process" : {
#     "insert_uri" : "uri",   // contains the URI specified with the PUT HTTP method
#     "process_id": pid, // process id number
#     "process_full_name": "process name",
#     "process_fqdn": "fully qualified domain name",
#     "process_args": ["arg1","arg2"],
#     "process_user" : "user" // user who ran the insert process on the client
#     "inserted_data_start": gpstime, // First gpstime of data this insertion describes
#     "inserted_data_end": gpstime, // Last gpstime of data this insertion describes
#     "process_start_timestamp": gpstime, // When the insert process was started, use to determine run time of inserts
#     // NOT to be added by client code -- these are server-side annotations, prior to insertion into the DB
#     "auth_user" : "user identification" // from the auth infrastructure used to talk to the server
#     "insert_timestamp" : gpstime,    // when the insert was committed to the DB
#    },
#    "flag" : {
#         "ifo" : "ifo",
#         "name" : "flag",
#         "comment" : "description",
#         "URL" : "aLog URL",
#         "deactivated" : false|true,
#         "active_indicates_ifo_badness" : true|false|null,
#         // all of the above will be needed for /dq/IFO/FLAG inserts
#         "version" : n,
#         // all of the above will be needed for /dq/IFO/FLAG/VERSION inserts
#         // all of the below are required for /dq/IFO/FLAG/VERSION/active inserts
#         "known" : [ [ts,te], [ts,te], ... ]
#         // Note that active segments do not actually have to be included, if the flag was known to be inactive:
#         "active" : [ [ts,te], [ts,te], ... ]
#         // \textcolor{red}{Comment: or "segment" : [ [ts,te,value], [ts,te,value], ...] (where value can be -1,0 or +1)}
#         // inactive == (known - active)
#         // unknown == (all_time - known)
#    }
# }
#
################################################################################

