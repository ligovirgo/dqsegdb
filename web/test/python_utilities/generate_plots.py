#!/usr/bin/env python
import argparse
from gwpy.segments import DataQualityFlag
import json
import shutil
from ligo import segments

"""
Script used in the on-fly production of segment-comparison plots.

History:
Last update: 29th of November, 2019, by Gary Hemming.
"""

"""
* Auxiliary methods
The following methods all provide auxiliary methods, used by the main or 
conversion methods.
"""

def convert_segmentlist_to_json(segmentlist_input):
    """ 
    Helper function used to convert segmentlist to json list of lists type 
    object.
    * Utility method, ripped from jsonhelper.py in dqsegdb package, until we 
    can use it as a dependency.
    """
    return [[x[0],x[1]] for x in segmentlist_input]

def convert_json_list_to_segmentlist(jsonlist):
    """ 
    Helper function used to convert JSON list of lists-type object to a 
    segmentlist object-
    * Utility method, ripped from jsonhelper.py in dqsegdb package, until we 
    can use it as a dependency.
    """
    return segments.segmentlist([segments.segment(x[0],x[1]) for x in jsonlist])

def parse_command_line():
    """
    Set the args that can be passed by the user at the command line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jsonfile', type=str, help="Json input file.")
    parser.add_argument('-o', '--output', help="Output file path")
    args = parser.parse_args()
    return args

"""
* Main.
"""

if __name__ == "__main__":
    """
    The script starts here, loads the JSON passed by the user, picks out the 
    segment lists, coalesces them, converts them into a GWpy-usable format 
    and then produces the plot.
    """
    # Init.
    dqf = []
    args = parse_command_line()
    # Try to load the JSON payload.
    try:
        json_dict = json.load(open(args.jsonfile))
    except:
        raise Exception('Unable to load JSON file: %s' % (args.jsonfile))
    else:
        # Loop through the Flag-versions passed.
        for v in json_dict:
            # Append the DataQualityFlag to the list.
            dqf.append(DataQualityFlag(v['name'], active=v['active'], known=v['known'], Description=None))
                            

