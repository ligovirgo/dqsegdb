############################
ligolw_segment_query_dqsegdb
############################

Overview
========
This provides the means to answer several questions posed against either the
segment database or a collection of DMT XML files.  Output should match 
exactly the format returned by S6 style segment database tools.

  * (Not yet operational): What DQ flags exist in the database? ligolw_segment_query --show-types
      * (Not yet operational): When was a given DQ flag defined? ligolw_segment_query --query-types 
          * When was a given flag active? ligolw_segment_query --query-segments
                * Example: ligolw_segment_query_dqsegdb --segment-url=http://slwebtest.virgo.infn.it --query-segments --gps-start-time 1070612448 --gps-end-time 1070613448 --include-segments="H1:ODC-PSL_SUMMARY:1" -o example.xml

Help message
============

.. command-output:: ligolw_segment_query_dqsegdb --help
