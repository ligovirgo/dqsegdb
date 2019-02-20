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

import sys
import math
import os
import operator
import tempfile

from six.moves import reduce

from ligo import segments

from glue.ligolw import table
from glue.ligolw import lsctables
from glue.ligolw import types as ligolwtypes

from glue.segmentdb import segmentdb_utils

from glue.ligolw.utils import ligolw_sqlite
from glue.ligolw import dbtables

from dqsegdb import jsonhelper


def include_exclude_caller(includedList,excludedList,startTime,endTime,protocol, server,include_list_string):
    """
    Function to query the dqsegdb for lists of included and excluded flags.
    Returns lists of JSON for the included and excluded flags and lists of
    URLs used to query the database.

    Parameters
    ----------
    includedList : `list`
        List of ifo,name,version tuples
    excludedList : `list`
        List of ifo,name,version tuples
    protocol : `string`
        Ex: 'https'
    server : `string`
        Ex: 'dqsegdb5.phy.syr.edu'
    include_list_string : `string`
        Ex: "metadata,known,active"
    startTime : `int`
        Ex: 999999999
    endTime : `int`
        Ex: 999999999

    """
    from dqsegdb import apicalls
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
    """
    Calculate the result of the union of the active times for the included flag less the intersection of that result with the union of the excluded flags
    Inputs are 2 lists of python dictionaries representing the JSON (already have run json.loads() on the JSON), a start time, and end time, and the ifo name (it does not make sense to include/exclude across multiple ifos)

    Parameters
    ----------
    startTime : `int`
        Ex: 999999999
    endTime : `int`
        Ex: 999999999
    ifo : `string`
        Ex: 'L1'

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

def calculate_versionless_result(jsonResults,startTime,endTime,ifo_input=None):
    """
    Construct output segments lists from multiple JSON objects.
    The jsonResults input is a list of json ojbects and
    are expected to be in order of decreasing versions.
    """
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
                print("Active results for version %d" % version)
                print(active_results[version])
            # Now I have 2 dictionaries of known and active segments with versions as keys in case I want/need them later...
            # This next step might seem a bit confusing:
            # We need to take the active segments for this version only during times that were not known by higher segment versions
            # Thus we need to take the intersection (& operator) of the unknown segments across all higher versions with the known segments for this version, then take the intersection of that result with the active segments for this version, and then add that to the current list of total active segments... phew:
            total_active_list |= (total_query_time-total_known_list)&known_segments&active_segments
            if debug:
                import pdb
                print("Running pdb to see what is in total_active_list")
                pdb.set_trace()
            total_active_list.coalesce()
            # The S6 clients want to know about the range of times affected by a given version explicitly, so those are calculated here:
            affected_results[version]=(total_query_time-total_known_list)&known_segments
            # Note that the order matters here!  we use the total_known_list from the previous iteration of the loop step to figure out which active segments to use in this iteration of the loop, so the above line must come before the next
            total_known_list |= known_segments
            total_known_list.coalesce()
    if ifo_input==None:
        if len(jsonResults)==0:
            import exceptions
            exceptions.RuntimeError("No versions for flag in versionless query")
        else:
            ifo=result['ifo']
    else:  #Only use ifo_input if we can't extract the ifo from the json result (usually because json result is empty)
        try:
            ifo=result['ifo']
        except:
            ifo=ifo_input
    name='RESULT' # Fix!!! Executive decision to make this clear that this is not a specific IFO:FLAG:VERSION resource, but rather a contrived result
    version=1 # Fix!!! Executive decision to make this match what old clients expect
    # I would prefer that this is more clear that this is not a specific IFO:FLAG:VERSION resource, but rather a contrived result, possibly by making it version 0
    total_active_list.coalesce()
    total_known_list.coalesce()
    result_flag=jsonhelper.buildFlagDict(ifo,name,version,total_known_list,total_active_list)
    return result_flag,affected_results

################################
#
#  S6 Client Utilities
#
################################

def seg_spec_to_sql(spec):
    """Given a string of the form ifo:name:version, ifo:name:* or ifo:name
    constructs a SQL caluse to restrict a search to that segment definer"""

    parts = spec.split(':')
    sql   = "(segment_definer.ifos = '%s'" % parts[0]

    if len(parts) > 1 and parts[1] != '*':
        sql += " AND segment_definer.name = '%s'" % parts[1]
        if len(parts) > 2 and parts[2] != '*':
            sql += " AND segment_definer.version = %s" % parts[2]

    sql += ')'

    return sql



#
# The results of show-types is a join against segment_definer and segment
# summary, and so does not fit into an existing table type.  So here we
# define a new type so that the ligolw routines can generate the XML
#
class ShowTypesResultTable(table.Table):
    tableName = "show_types_result:table"

    validcolumns = {
        "ifos": "lstring",
        "name": "lstring",
        "version": "int_4s",
        "segment_definer_comment": "lstring",
        "segment_summary_start_time": "int_4s",
        "segment_summary_end_time": "int_4s",
        "segment_summary_comment": "lstring"
        }



class ShowTypesResult(object):
    __slots__ = ShowTypesResultTable.validcolumns.keys()

    def get_pyvalue(self):
        if self.value is None:
            return None
        return ligolwtypes.ToPyType[self.type or "lstring"](self.value)


ShowTypesResultTable.RowType = ShowTypesResult



#
# =============================================================================
#
#                          Methods that implement major modes
#
# =============================================================================
#
def run_show_types(doc, connection, engine, gps_start_time, gps_end_time, included_segments_string, excluded_segments_string):
    resulttable = lsctables.New(ShowTypesResultTable)
    doc.childNodes[0].appendChild(resulttable)

    sql = """SELECT segment_definer.ifos, segment_definer.name, segment_definer.version,
                 (CASE WHEN segment_definer.comment IS NULL THEN '-' WHEN segment_definer.comment IS NOT NULL THEN segment_definer.comment END),
                 segment_summary.start_time, segment_summary.end_time,
                 (CASE WHEN segment_summary.comment IS NULL THEN '-' WHEN segment_summary.comment IS NOT NULL THEN segment_summary.comment END)
          FROM  segment_definer, segment_summary
          WHERE segment_definer.segment_def_id = segment_summary.segment_def_id
          AND   NOT (segment_summary.start_time > %d OR %d > segment_summary.end_time)
          """ % (gps_end_time, gps_start_time)

    rows = engine.query(sql)

    seg_dict = {}

    for row in rows:
        ifos, name, version, segment_definer_comment, segment_summary_start_time, segment_summary_end_time, segment_summary_comment = row
        key = (ifos, name, version, segment_definer_comment, segment_summary_comment)
        if key not in seg_dict:
            seg_dict[key] = []

        seg_dict[key].append(segments.segment(segment_summary_start_time, segment_summary_end_time))

    for key, value in seg_dict.iteritems():
        segmentlist = segments.segmentlist(value)
        segmentlist.coalesce()

        for segment in segmentlist:
            result = ShowTypesResult()
            result.ifos, result.name, result.version, result.segment_definer_comment, result.segment_summary_comment = key
            result.segment_summary_start_time, result.segment_summary_end_time = segment
            result.ifos = result.ifos.strip()

            resulttable.append(result)

    engine.close()


def run_query_types(doc, proc_id, connection, engine, gps_start_time, gps_end_time, included_segments):
    query_segment = segments.segmentlist([segments.segment(gps_start_time, gps_end_time)])

    sql = """SELECT segment_definer.ifos, segment_definer.name,segment_definer.version,
           (CASE WHEN segment_definer.comment IS NULL THEN '-' WHEN segment_definer.comment IS NOT NULL THEN segment_definer.comment END),
           segment_summary.start_time, segment_summary.end_time,
           (CASE WHEN segment_summary.comment IS NULL THEN '-' WHEN segment_summary.comment IS NOT NULL THEN segment_summary.comment END)
    FROM segment_definer, segment_summary
    WHERE segment_definer.segment_def_id = segment_summary.segment_def_id
    AND NOT(%d > segment_summary.end_time OR segment_summary.start_time > %d)
    """ % (gps_start_time, gps_end_time)

    type_clauses = map(seg_spec_to_sql, included_segments.split(','))

    if type_clauses != []:
        sql += " AND (" + "OR ".join(type_clauses) + ")"


    segment_types = {}

    for row in engine.query(sql):
        sd_ifo, sd_name, sd_vers, sd_comment, ss_start, ss_end, ss_comment = row
        key = (sd_ifo, sd_name, sd_vers, sd_comment, ss_comment)
        if key not in segment_types:
            segment_types[key] = segments.segmentlist([])
        segment_types[key] |= segments.segmentlist([segments.segment(ss_start, ss_end)])

    engine.close()

    # Create segment definer and segment_summary tables
    seg_def_table = lsctables.New(lsctables.SegmentDefTable, columns = ["process_id", "segment_def_id", "ifos", "name", "version", "comment"])
    doc.childNodes[0].appendChild(seg_def_table)

    seg_sum_table = lsctables.New(lsctables.SegmentSumTable, columns = ["process_id", "segment_sum_id", "start_time", "start_time_ns", "end_time", "end_time_ns", "comment", "segment_def_id"])

    doc.childNodes[0].appendChild(seg_sum_table)

    for key in segment_types:
        # Make sure the intervals fall within the query window and coalesce
        segment_types[key].coalesce()
        segment_types[key] &= query_segment

        seg_def_id                     = seg_def_table.get_next_id()
        segment_definer                = lsctables.SegmentDef()
        segment_definer.process_id     = proc_id
        segment_definer.segment_def_id = seg_def_id
        segment_definer.ifos           = key[0]
        segment_definer.name           = key[1]
        segment_definer.version        = key[2]
        segment_definer.comment        = key[3]

        seg_def_table.append(segment_definer)

        # add each segment summary to the segment_summary_table

        for seg in segment_types[key]:
            segment_sum            = lsctables.SegmentSum()
            segment_sum.comment    = key[4]
            segment_sum.process_id = proc_id
            segment_sum.segment_def_id = seg_def_id
            segment_sum.segment_sum_id = seg_sum_table.get_next_id()
            segment_sum.start_time = seg[0]
            segment_sum.start_time_ns = 0
            segment_sum.end_time   = seg[1]
            segment_sum.end_time_ns = 0

            seg_sum_table.append(segment_sum)

def run_query_segments(doc, process_id, engine, gps_start_time, gps_end_time, include_segments, exclude_segments, result_name):
    segdefs = []

    for included in include_segments.split(','):
        spec = included.split(':')

        if len(spec) < 2 or len(spec) > 3:
            print("Included segements must be of the form ifo:name:version or ifo:name:*", file=sys.stderr)
            sys.exit(1)

        ifo     = spec[0]
        name    = spec[1]
        if len(spec) is 3 and spec[2] is not '*':
            version = int(spec[2])
            if version < 1:
                print("Segment version numbers must be greater than zero", file=sys.stderr)
                sys.exit(1)
        else:
            version = '*'

        segdefs += segmentdb_utils.expand_version_number(engine, (ifo, name, version, gps_start_time, gps_end_time, 0, 0) )

    found_segments = segmentdb_utils.query_segments(engine, 'segment', segdefs)
    found_segments = reduce(operator.or_, found_segments).coalesce()

    # We could also do:
    segment_summaries = segmentdb_utils.query_segments(engine, 'segment_summary', segdefs)

    # And we could write out everything we found
    segmentdb_utils.add_segment_info(doc, process_id, segdefs, None, segment_summaries)


    # Do the same for excluded
    if exclude_segments:
        ex_segdefs = []

        for excluded in exclude_segments.split(','):
            spec = excluded.split(':')

            if len(spec) < 2:
                print("Excluded segements must be of the form ifo:name:version or ifo:name:*", file=sys.stderr)
                sys.exit(1)

            ifo     = spec[0]
            name    = spec[1]
            version = len(spec) > 2 and spec[2] or '*'

            ex_segdefs += segmentdb_utils.expand_version_number(engine, (ifo, name, version, gps_start_time, gps_end_time, 0, 0) )


        excluded_segments = segmentdb_utils.query_segments(engine, 'segment', ex_segdefs)
        excluded_segments = reduce(operator.or_, excluded_segments).coalesce()

        found_segments.coalesce()
        found_segments -= excluded_segments



    # Add the result type to the segment definer table
    seg_name   = result_name
    seg_def_id = segmentdb_utils.add_to_segment_definer(doc, process_id, ifo, seg_name, 1)

    # and segment summary
    segmentdb_utils.add_to_segment_summary(doc, process_id, seg_def_id, [[gps_start_time, gps_end_time]])

    # and store the segments
    segmentdb_utils.add_to_segment(doc, process_id, seg_def_id, found_segments)
    print("Made it to the end of the query code")
    print(doc)
           

#
# =============================================================================
#
#                                 XML/File routines
#
# =============================================================================
#


def setup_files(dir_name, gps_start_time, gps_end_time):
    # Filter out the ones that are outside our time range
    xml_files = segmentdb_utils.get_all_files_in_range(dir_name, gps_start_time, gps_end_time)

    handle, temp_db  = tempfile.mkstemp(suffix='.sqlite')
    os.close(handle)

    target     = dbtables.get_connection_filename(temp_db, None, True, False)
    connection = ligolw_sqlite.setup(target)

    ligolw_sqlite.insert_from_urls(connection, xml_files) # [temp_xml])

    segmentdb_utils.ensure_segment_table(connection)

    return temp_db, connection

def add_to_segment_ns(xmldoc, proc_id, seg_def_id, sgmtlist):
    try:
        segtable = table.get_table(xmldoc, lsctables.SegmentTable.tableName)
    except:
        segtable = lsctables.New(lsctables.SegmentTable, columns = ["process_id", "segment_def_id", "segment_id", "start_time", "start_time_ns", "end_time", "end_time_ns"])
        xmldoc.childNodes[0].appendChild(segtable)

    for seg in sgmtlist:
        segment                = lsctables.Segment()
        segment.process_id     = proc_id
        segment.segment_def_id = seg_def_id
        segment.segment_id     = segtable.get_next_id()
        seconds,nanoseconds=output_microseconds(seg[0])
        segment.start_time     = seconds
        segment.start_time_ns  = nanoseconds
        seconds,nanoseconds=output_microseconds(seg[1])
        segment.end_time       = seconds
        segment.end_time_ns    = nanoseconds

        segtable.append(segment)

def add_to_segment_summary_ns(xmldoc, proc_id, seg_def_id, sgmtlist, comment=''):
    try:
        seg_sum_table = table.get_table(xmldoc, lsctables.SegmentSumTable.tableName)
    except:
        seg_sum_table = lsctables.New(lsctables.SegmentSumTable, columns = ["process_id", "segment_def_id", "segment_sum_id", "start_time", "start_time_ns", "end_time", "end_time_ns", "comment"])
        xmldoc.childNodes[0].appendChild(seg_sum_table)

    for seg in sgmtlist:
        segment_sum                = lsctables.SegmentSum()
        segment_sum.process_id     = proc_id
        segment_sum.segment_def_id = seg_def_id
        segment_sum.segment_sum_id = seg_sum_table.get_next_id()
        seconds,nanoseconds=output_microseconds(seg[0])
        segment_sum.start_time     = seconds
        segment_sum.start_time_ns  = nanoseconds
        seconds,nanoseconds=output_microseconds(seg[1])
        segment_sum.end_time       = seconds
        segment_sum.end_time_ns    = nanoseconds
        #segment_sum.start_time     = seg[0]
        #segment_sum.start_time_ns  = 0
        #segment_sum.end_time       = seg[1]
        #segment_sum.end_time_ns    = 0
        segment_sum.comment        = comment

        seg_sum_table.append(segment_sum)

def add_segment_info_ns(doc, proc_id, segdefs, segments, segment_summaries):

    for i in range(len(segdefs)):
        ifo, name, version, start_time, end_time, start_pad, end_pad = segdefs[i]

        seg_def_id = segmentdb_utils.add_to_segment_definer(doc, proc_id, ifo, name, version)

        add_to_segment_summary_ns(doc, proc_id, seg_def_id, segment_summaries[i])

        if segments:
            add_to_segment_ns(doc, proc_id, seg_def_id, segments[i])


def output_microseconds(input_time):
    # Says it outputs nanoseconds, but really is only good to microsecond precision!!!
    if isinstance(input_time, float):
        ns, seconds = math.modf(input_time)
        seconds = int(input_time)
        nanoseconds = ns * 1e9
        nanoseconds=round((nanoseconds/1e+3))*1e3
    else:
        seconds=int(input_time)
        nanoseconds=0
    return seconds, nanoseconds
