#!/usr/bin/env python
import argparse
import json
from glue import segments

########### ########### ########### ###########
#
# Extract json file to string
#
########### ########### ########### ###########

def open_json_file(json_filepath):
    return json.load(open(json_filepath))

################################################################################
#
#  Conversions from JSON to user requested formats
#
################################################################################

def generated_vdb_ascii(json_dict,filepath):
    #res_dict=json.loads(json_str)
    res_dict=json_dict
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

def generated_ascii(json_dict,filepath):
    #res_dict=json.loads(json_str)    
    res_dict=json_dict
    active_list=res_dict['active']
    active_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in active_list])    
    active_segments_string='\n'.join([str(i[0])+","+str(i[1]) for i in active_segments])
    output_fileh=open(filepath,'w+')    
    output_fileh.writelines(active_segments_string)
    output_fileh.close()
    return filepath

#####
#
#  Set up parser for command line execution
#
######

def parse_command_line():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jsonfile', type=str, help="Json input file.")
    parser.add_argument('-o', '--output', help="Output file path")
    parser.add_argument('-t', '--type', default='vdb', help='Type of file to ouput, default: %(default)s')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_command_line()
    if args.type != 'vdb' and args.type != 'ascii':
        raise InputError('Please provide type of vdb or ascii')
    json_string=open_json_file(args.jsonfile)
    if args.type == 'vdb':
        res_file=generated_vdb_ascii(json_string,args.output)
    elif args.type == 'ascii':
        res_file=generated_ascii(json_string,args.output)
    print "Output file %s created" % res_file

    

