#!/usr/bin/env python
# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.\n
# This program is free software: you can redistribute it and/or modify\n
# it under the terms of the GNU Affero General Public License as\n
# published by the Free Software Foundation, either version 3 of the\n
# License, or (at your option) any later version.\n
#\n
# This program is distributed in the hope that it will be useful,\n
# but WITHOUT ANY WARRANTY; without even the implied warranty of\n
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n
# GNU Affero General Public License for more details.\n
#\n
# You should have received a copy of the GNU Affero General Public License\n
# along with this program.  If not, see <http://www.gnu.org/licenses/>.\n

from __future__ import print_function
import argparse
import json
import shutil
from ligo import segments

########### ########### ########### ###########
#
# Extract json file to string
#
########### ########### ########### ###########

def open_json_file(json_filepath):
    try:
        return [json.load(open(json_filepath))]
    except ValueError:
        start_json_block_index=0
        result_array=[]
        data=open(json_filepath,'r').readlines()
        count=0
        index=0
        clean_data=data[0].strip()
        for i in clean_data:
            if i=="{":
                count=count+1
            elif i=="}":
                count=count-1
            if count==0:
                #print "Made it through first payload at index: %d" % index
                #print clean_data[start_json_block_index:index+1]
                result_array.append(json.loads(clean_data[start_json_block_index:index+1]))
                start_json_block_index=index+1
            index+=1
        return result_array

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
    active_segments.coalesce()
    known_list=res_dict['known']
    known_segments=segments.segmentlist([segments.segment(x[0],x[1]) for x in known_list])
    known_segments.coalesce()
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
    output_fileh=open(filepath,'a')
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
    active_segments.coalesce()
    output_fileh=open(filepath,'a')    
    output_fileh.writelines(active_segments_string)
    output_fileh.close()
    return filepath

def generated_json(json_dict,filepath):
    res_dict=json_dict
    active_list=res_dict['active']
    active_segments=convert_json_list_to_segmentlist(active_list)
    active_segments.coalesce()
    active_json=convert_segmentlist_to_json(active_segments)
    res_dict['active']=active_json

    known_list=res_dict['known']
    known_segments=convert_json_list_to_segmentlist(known_list)
    known_segments.coalesce()
    known_json=convert_json_list_to_segmentlist(known_segments)
    res_dict['known']=known_json
    #print filepath
    ### Document why we need the next line!:
    ### It is because the file name would be <number>.coalesced_json and we want it to be <number>.coalesced.json instead.  This breaks with normal file names given to command line though
    #filepath=".".join(["_".join(filepath.split("_")[0:-1]),filepath.split("_")[-1:][0]])
    #filepath='.'.join(filepath.split('_')[)
    #print filepath
    output_fileh=open(filepath,'a') 
    #output_fileh.writelines(active_segments_string) 
    json_output_string=json.dumps(res_dict)
    #print "Coalesced json string type"
    #print type(json_output_string)
    output_fileh.writelines(json_output_string)
    output_fileh.close()
    return filepath



##### 
#
# Ripped from jsonhelper.py in dqsegdb package until we can use it as a dependency
#
#####

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
    #print args.output
    if args.type != 'vdb' and args.type != 'ascii' and args.type != 'coalesced_json':
        raise InputError('Please provide type of vdb or ascii or coalesced_json')
    json_dict_array=open_json_file(args.jsonfile)
    if args.type == 'vdb':
        if len(json_dict_array)==1:
            json_dict=json_dict_array[0]
            res_file=generated_vdb_ascii(json_dict,args.output)
        else:
            for json_dict in json_dict_array:
                version=json_dict['version']
                fileh=open(args.output,'a')
                if fileh.tell()==0:
                    fileh.writelines('Multiple Versions Requested, Version = %d Results: \n' % int(version))
                else:
                    fileh.writelines('\nMultiple Versions Requested, Version = %d Results: \n' % int(version))
                fileh.close()
                res_file=generated_vdb_ascii(json_dict,args.output)
    elif args.type == 'ascii':
        #res_file=generated_ascii(json_dict,args.output)
        if len(json_dict_array)==1:
            json_dict=json_dict_array[0]
            res_file=generated_ascii(json_dict,args.output)
        else:
            for json_dict in json_dict_array:
                version=json_dict['version']
                fileh=open(args.output,'a')
                if fileh.tell()==0:
                    fileh.writelines('Multiple Versions Requested, Version = %d Results: \n' % int(version))
                else:
                    fileh.writelines('\nMultiple Versions Requested, Version = %d Results: \n' % int(version))
                fileh.close()
                res_file=generated_ascii(json_dict,args.output)

    elif args.type == 'coalesced_json':
        #res_file=generated_json(json_dict,args.output)
        if len(json_dict_array)==1:
            json_dict=json_dict_array[0]
            res_file=generated_json(json_dict,args.output)
        else:
            for number,json_dict in enumerate(json_dict_array):
                version=json_dict['version']
                fileh=open(args.output,'a')
                if fileh.tell()==0:
                    fileh.writelines('Multiple Versions Requested, Version = %d Results: \n' % int(version))
                else:
                    fileh.writelines('\nMultiple Versions Requested, Version = %d Results: \n' % int(version))
                fileh.close()
                #res_file=generated_json(json_dict,args.output)
                if number==0:
                    res_file=generated_json(json_dict,args.output)
                else:
                    res_file=generated_json(json_dict,res_file)
        filepath=args.output
        final_filepath=".".join(["_".join(filepath.split("_")[0:-1]),filepath.split("_")[-1:][0]])
        shutil.copy(res_file, final_filepath)

    print("Output file %s created" % res_file)
