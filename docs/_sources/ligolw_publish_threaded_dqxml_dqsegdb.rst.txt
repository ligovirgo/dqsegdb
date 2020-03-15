#####################################
ligolw_publish_threaded_dqxml_dqsegdb
#####################################

Overview
========
Publishing client used to publish DQMXML (usually produced by DMT) from a set
of directories to the DQSEGDB server.  This publisher supports grouping 
multiple input files together, and then pushing data to the database either
one flag:version at a time or pushing data in a threaded manner.

Also supports a start time and end time argument to restrict the range of input data accepted.

Please see Python help documentation for all input arguments.

Example call to function:
    
ligolw_publish_threaded_dqxml_dqsegdb --segment-url http://slwebtest.virgo.infn.it --state-file=/home/rfisher/DQSEGDB/DQSEGDBClient/var/spool/L-DQ_Segments_long_test.xml --pid-file=/home/rfisher/DQSEGDB/DQSEGDBClient/var/run/L-DQ_Segments.pid --log-file=/home/rfisher/DQSEGDB/DQSEGDBClient/var/log/L-DQ_Segments.log --input-directory=/archive/frames/dmt/ER4/DQ/L1 --log-level DEBUG -m 60 -c 20 -e 105819443

Help message
============

.. command-output:: ligolw_publish_threaded_dqxml_dqsegdb --help
