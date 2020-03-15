#!/root/miniconda3/bin/python
# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
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
    #all_flags = DataQualityFlag('', active=[], known=[], description=None)
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
            # Build the DQ flag structure.
            dq_flag = DataQualityFlag(('%s:%s:%d') % (v['ifo'], v['name'], v['version']), active=convert_segmentlist_to_json(sa), known=convert_segmentlist_to_json(sk), description=None)
            # Check if the variable for the all-flag bar has been set.
            try:
                all_flags
            except:
                # If it has not been set, initialise as  DQ Flag structure.
                all_flags = dq_flag
            # Append the DQ flag to the list.
            dqfs.append(dq_flag)
            # Add to what will be come the all-flags bar.
            all_flags = (all_flags & dq_flag)
        # Loop through the DQ Flag dictionary.
        for dqf in dqfs:
            try:
                plot
            except:
                # Initialisa the plot.
                plot = dqfs[0].plot(insetlabels=True)
                ax = plot.gca()
            else:
                # Add the DQ Flag structure to the plot.
                ax.plot(dqf)
        # Build the all-flag plot.
        #ax.set_xscale('hours')
        ax.set_epoch(json_dict[0]['query_information']['start'])
        ax.plot(all_flags, label='All')
        plot.save(args.output)
