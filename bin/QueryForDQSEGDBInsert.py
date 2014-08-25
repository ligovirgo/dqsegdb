#!/usr/bin/env python

from optparse import OptionParser

def parse_command_line():
    """
    Parse the command line, return an options object
    """

    parser = OptionParser(
 	version = "First" ,
        usage       = "%prog [ --version ] [ --segment-url ] options ",
        description = "Performs a number of queries against either a set of DMT files or a segment database")

    parser.add_option("-t", "--segment-url",    metavar = "segment_url", help = "Segment URL to publish results to. Users have to specify either 'https://' for a secure connection or 'http://' for an insecure connection in the segment database url. For example, '--segment-url=https://segdb.ligo.caltech.edu'. No need to specify port number. ")
    parser.add_option("-i","--ifo", metavar="ifo", help="Ifo like L1")
    parser.add_option("-n","--name", metavar="name", help="Name like DMT-SCIENCE")
    parser.add_option("-v","--segversion", metavar="segversion", help="segment version like 3")

    options, others = parser.parse_args()
    for arg in [options.segment_url,options.ifo,options.name,options.segversion]:
        if not arg:
            raise ValueError("Must supply segment-url, ifo, name and segversion")

    return options

def append_process_gpssane(xmldoc, program = None, version = None, cvs_repository = None, cvs_entry_time = None, comment = None, is_online = False, jobid = 0, domain = None, ifos = None):
    """
    Add an entry to the process table in xmldoc.  program, version,
    cvs_repository, comment, and domain should all be strings or
    unicodes.  cvs_entry_time should be a 9 or 10 digit GPS time
    is_online should be a boolean, jobid
    an integer.  ifos should be an iterable (set, tuple, etc.) of
    instrument names.

    See also register_to_xmldoc().
    """
    try:
            proctable = lsctables.ProcessTable.get_table(xmldoc)
    except ValueError:
            proctable = lsctables.New(lsctables.ProcessTable)
            xmldoc.childNodes[0].appendChild(proctable)

    proctable.sync_next_id()

    process = proctable.RowType()
    process.program = program
    process.version = version
    process.cvs_repository = cvs_repository
    ## FIXME:  remove the "" case when the git versioning business is
    ## sorted out
    #if cvs_entry_time is not None and cvs_entry_time != "":
    #        try:
    #                # try the git_version format first
    #                process.cvs_entry_time = _UTCToGPS(time.strptime(cvs_entry_time, "%Y-%m-%d %H:%M:%S +0000"))
    #        except ValueError:
    #                # fall back to the old cvs format
    #                process.cvs_entry_time = _UTCToGPS(time.strptime(cvs_entry_time, "%Y/%m/%d %H:%M:%S"))
    #else:
    #        process.cvs_entry_time = None
    ## Instead of all of that above, just require the input time to be a GPS
    process.cvs_entry_time=cvs_entry_time
    process.comment = comment
    process.is_online = int(is_online)
    process.node = socket.gethostname()
    try:
            process.username = get_username()
    except KeyError:
            process.username = None
    process.unix_procid = os.getpid()
    process.start_time = _UTCToGPS(time.gmtime())
    process.end_time = None
    process.jobid = jobid
    process.domain = domain
    process.set_ifos(ifos)
    process.process_id = proctable.get_next_id()
    proctable.append(process)
    return process



if __name__ == "__main__":
    # Flag we want:
    
    #ifo="L1"
    #name="DMT-SCIENCE"
    #version=2
    
    options=parse_command_line()
    ifo=options.ifo
    name=options.name
    version=int(options.segversion)
    segment_url=options.segment_url
    
    # DB2 connection
    
    import DB2
    conn=DB2.connect(dsn='seg_cit',uid='',pwd='')
    curs=conn.cursor()
    
    # Grab the process information
    
    
    curs.execute("select segment_definer.ifos, segment_definer.name, segment_definer.version, process.start_time, process.end_time,process.program,process.creator_db,process.version,process.cvs_repository,process.cvs_entry_time,process.comment,process.is_online,process.node,process.username,process.unix_procid,process.jobid,process.domain,process.param_set,process.ifos,process.insertion_time, segment_definer.comment from segment_definer, process where process.process_id = segment_definer.process_id AND (segment_definer.ifos = '%s' AND segment_definer.name = '%s' AND segment_definer.version = %d)" %(ifo,name,version))
    procresult=curs.fetchall()
    
    ifo=procresult[0][0].strip()
    proc_start_time=procresult[0][3]
    proc_end_time=procresult[0][4]
    
    proc_program=procresult[0][5]
    
    proc_creator_db=procresult[0][6]
    
    proc_version =procresult[0][7]
    proc_cvs_repository=procresult[0][8]
    proc_cvs_entry_time=procresult[0][9]  # Fix!!! Need to fix formatting below
    proc_comment=procresult[0][10]
    proc_is_online=procresult[0][11]
    
    proc_node=procresult[0][12]
    proc_username=procresult[0][13]
    proc_unix_procid=procresult[0][14]
    
    proc_jobid=procresult[0][15]
    proc_domain=procresult[0][16]
    
    proc_param_set=procresult[0][17]
    
    proc_ifos=(procresult[0][18])  # Might not work, but process.append_process expects a tuple here;  in practice, we give it a None!
    
    proc_insertion_time=procresult[0][19]
    
    segdef_comment=procresult[0][20]
    
    # Create a ligolw document to start adding information to:
    
    from glue.ligolw import ligolw
    doc = ligolw.Document()
    doc.appendChild(ligolw.LIGO_LW())
    
    from glue.ligolw import types as ligolwtypes
    ligolwtypes.FromPyType[type(True)] = ligolwtypes.FromPyType[type(0)]
    
    # Format and add the process information:
    
    from glue.ligolw.utils import process
    
    #from pylal.xlal.datatypes.ligotimegps import LIGOTimeGPS
    #formated_cvs_gps = LIGOTimeGPS(proc_cvs_entry_time)
    #from pylal.date import XLALGPSToUTC
    #cvs_time_tuple=XLALGPSToUTC(formated_cvs_gps)
    
    #proc_cvs_entry_time="%d-%d-%d %d:%d:%d +0000" %(cvs_time_tuple[0],cvs_time_tuple[1],cvs_time_tuple[2],cvs_time_tuple[3],cvs_time_tuple[4],cvs_time_tuple[5])
    
    #append_process_gpssane
    #proc_out=process.append_process(doc,program=proc_program,version=proc_version,cvs_repository=proc_cvs_repository,cvs_entry_time=proc_cvs_entry_time,comment=proc_comment,is_online=proc_is_online,jobid=proc_jobid,domain=proc_domain,ifos=proc_ifos)
    proc_out=append_process_gpssane(doc,program=proc_program,version=proc_version,cvs_repository=proc_cvs_repository,cvs_entry_time=proc_cvs_entry_time,comment=proc_comment,is_online=proc_is_online,jobid=proc_jobid,domain=proc_domain,ifos=proc_ifos)
    
    params=process.process_params_from_dict({"start_time": proc_start_time, "end_time": proc_end_time, "creator_db":proc_creator_db, "node":proc_node,"username":proc_username,"unix_procid":proc_unix_procid,"param_set":proc_param_set, "insertion_time":proc_insertion_time})
    
    process_doc_out=process.append_process_params(doc,proc_out,params)
    
    # Now add segment definer to doc 
    # Fix!!! Why didn't I just call segmentdb_utils.add_to_segment_definer?  This is that code duplicated:
    
    from glue.ligolw import lsctables
    
    seg_def_table = lsctables.New(lsctables.SegmentDefTable,columns = ['segment_def_id', 'process_id','ifos','name', 'version','comment'])
    # adds this table to the doc:
    doc.childNodes[0].appendChild(seg_def_table)
    
    # creates (local) table data container to be appended to table we just made
    segment_definer = lsctables.SegmentDef()
    
    seg_def_id = seg_def_table.get_next_id()
    segment_definer.segment_def_id = seg_def_id
    segment_definer.process_id = proc_out.process_id
    segment_definer.ifos = ifo
    segment_definer.name = name
    segment_definer.version = int(version)
    segment_definer.comment = segdef_comment
    # Appends local table to document table that we made above
    seg_def_table.append(segment_definer)
    
    
    # Now add segment summaries to doc
    curs.execute("SELECT segment_summary.start_time, segment_summary.end_time  FROM segment_definer, segment_summary  WHERE segment_summary.segment_def_id = segment_definer.segment_def_id AND (segment_definer.ifos = '%s' AND segment_definer.name = '%s' AND segment_definer.version = %d)" %(ifo,name,version))
    
    sumresult=curs.fetchall()
    
    from glue import segments
    
    sum_result_segments=[segments.segment(i) for i in sumresult]
    
    sum_result_segments_list=segments.segmentlist(sum_result_segments)
    
    sum_result_segments_list.coalesce()
    
    #using seg_def_id from above
    from glue.segmentdb import segmentdb_utils
    segmentdb_utils.add_to_segment_summary(doc, proc_out.process_id, seg_def_id, sum_result_segments_list)
    
    # Now add  segments to doc
    curs.execute("SELECT segment.start_time, segment.end_time  FROM segment_definer, segment  WHERE segment.segment_def_id = segment_definer.segment_def_id AND (segment_definer.ifos = '%s' AND segment_definer.name = '%s' AND segment_definer.version = %d)" %(ifo,name,version))
    
    segresult=curs.fetchall()
    
    from glue import segments
    
    seg_result_segments=[segments.segment(i) for i in segresult]
    
    seg_result_segments_list=segments.segmentlist(seg_result_segments)
    
    seg_result_segments_list.coalesce()
    
    segmentdb_utils.add_to_segment(doc, proc_out.process_id, seg_def_id, seg_result_segments_list)
    
    # Now publish the doc after writing it to disk temporarily
    
    import logging
    import logging.handlers
    
    def callInsertMultipleDQXMLThreaded(filepath,segment_url):
        logger = logging.getLogger('ligolw_publish_dqxml_dqsegdb')
        log_file=filepath.split('.xml')[0]+'.log'
        handler = logging.handlers.RotatingFileHandler(log_file, 'a', 1024**3, 3)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(eval("logging." + "DEBUG"))
        infiles=[filepath]
        result=apicalls.InsertMultipleDQXMLFileThreaded(infiles,logger,segment_url,hackDec11=False,debug=False,threads=1)
        return result
    
    import StringIO
    
    fake_file = StringIO.StringIO()
    doc.write(fake_file)
    import time
    filepath='/tmp/ligolw_segment_insert_'+str(time.time())+'.xml'
    #atexit.register(del_file,filepath) # 
    fp = open(filepath,'w')
    fp.write(fake_file.getvalue())
    fp.close()
    #segment_url="http://dqsegdb6.phy.syr.edu"
    filepath # for checking output
    
    
    from dqsegdb import apicalls
    
    result=callInsertMultipleDQXMLThreaded(filepath,segment_url)
