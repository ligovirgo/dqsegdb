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
    dqfs = []
    all_flags = DataQualityFlag('', active=[], known=[], description=None)
    args = parse_command_line()
    # Try to load the JSON payload.
    try:
        json_dict = json.load(open(args.jsonfile))
    except:
        raise Exception('Unable to load JSON file: %s' % (args.jsonfile))
    else:
        # Loop through the Flag-versions passed.
        for v in json_dict:
            # Convert JSON segments to LIGO Segment structure and coalesce.
            sa = convert_json_list_to_segmentlist(v['active'])
            sa.coalesce()
            sk = convert_json_list_to_segmentlist(v['known'])
            sk.coalesce()
            # Set the DataQualityFlag.
            dq_flag = DataQualityFlag(v['name'], active=convert_segmentlist_to_json(sa), known=convert_segmentlist_to_json(sk), description=None)
            # Append the DataQualityFlag to the list.
            dqfs.append(dq_flag)
            # Build the all flags bar.
            all_flags = all_flags + dq_flag
        # Instantiate plot with first flag.
        plot = dqfs[0].plot()
        ax = plot.gca()
        # Loop through the DataQualityFlag dictionary.
        for dqf in dqfs:
            # Build the plot for the flag.
            ax.plot(dqf)
        # Build the all-flag plot.
        ax.plot(all_flags, label='All')
        plot.save(args.output)

