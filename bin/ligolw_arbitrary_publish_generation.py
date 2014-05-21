#!/usr/bin/env python
import errno
import sys,os,stat
from glue import pipeline
import time

# Put this in a config file eventually:
# [V]
#interferometer="V" # H,L,V
#run_dir="/home/rfisher/DQSEGDB/DQSEGDBClient/"+time.strftime("%M%H%d%m%Y")
#dqsegdb_code_DIR="/home/rfisher/DQSEGDB_Mar12/dqsegdb"
#template_state_file="/home/rfisher/DQSEGDB/DQSEGDBClient/var/spool/"+interferometer+"-DQ_Segments_S6_template.xml"
#publish_executable=dqsegdb_code_DIR+"/bin/ligolw_publish_threaded_dqxml_dqsegdb_hacked"
##dqxml_dir="/archive/frames/online/DQ/V1" # /archive/frames/dmt/L${inf}O/triggers/DQ_Segments
#offset=2000000000 # time offset to publish segmetns
#mode="vanilla" # single?, local
#start_time=928787010# ignored if not > 928787010
#end_time=975287010# ignored if not < 975287010
##log_file = run_dir+"/var/log/"+
#site='CIT' # used to determine DQXML file path
#executable_name=run_dir+"/van_V1_offset_test.sh"
#user_name="rfisher" # used so cluster jobs will write to /usr1/ directory for logging
#gps_stride_per_job=500000
#log_file_dir=run_dir+"/var/log"
#gap_publish=False
#debug=True
#server="http://dqsegdb3.phy.syr.edu"
#files_per_publish=5000
#threading=1

# [L]
interferometer="L" # H,L,V
user_name=str(sys.argv[1]) # used so cluster jobs will write to /usr1/ directory for logging
run_dir=os.getcwd()+"/"+time.strftime("%M%H%d%m%Y")
dqsegdb_code_DIR="<path>/dqsegdb"
template_state_file="/home/rfisher/DQSEGDB/DQSEGDBClient/var/spool/"+interferometer+"-DQ_Segments_S6_template.xml"
publish_executable=dqsegdb_code_DIR+"/bin/ligolw_publish_threaded_dqxml_dqsegdb_hacked"
#dqxml_dir="/archive/frames/online/DQ/V1" # /archive/frames/dmt/L${inf}O/triggers/DQ_Segments
offset=3000000000 # time offset to publish segmetns
mode="vanilla" # single?, local
start_time=968654528# ignored if not > 928787010
end_time=968656112# ignored if not < 975287010
#log_file = run_dir+"/var/log/"+
site='CIT' # used to determine DQXML file path
executable_name=run_dir+"/van_"+interferometer+"1_offset_test.sh"
gps_stride_per_job=500
log_file_dir=run_dir+"/var/log"
gap_publish=False
debug=True
server="http://dqsegdb3.phy.syr.edu"
files_per_publish=100
threading=1

interferometer="L" # H,L,V
user_name=str(sys.argv[1]) # used so cluster jobs will write to /usr1/ directory for logging
run_dir=os.getcwd()+"/"+time.strftime("%M%H%d%m%Y")
dqsegdb_code_DIR="/home/rfisher/DQSEGDB_Mar12/dqsegdb"
template_state_file="/home/rfisher/DQSEGDB/DQSEGDBClient/var/spool/"+interferometer+"-DQ_Segments_S6_template.xml"
publish_executable=dqsegdb_code_DIR+"/bin/ligolw_publish_threaded_dqxml_dqsegdb_hacked"
#dqxml_dir="/archive/frames/online/DQ/V1" # /archive/frames/dmt/L${inf}O/triggers/DQ_Segments
offset=71 # time offset to publish segmetns
mode="local" # single?, local
start_time=968654528# ignored if not > 928787010
end_time = 969454528 # 16(s)*5000(files) # ignored if not < 975287010
#log_file = run_dir+"/var/log/"+
site='CIT' # used to determine DQXML file path
executable_name=run_dir+"/loc_"+interferometer+"1_offset_test.sh"
gps_stride_per_job=80000 # 10 jobs for whole range, 5000 files each
log_file_dir=run_dir+"/var/log"
gap_publish=False
debug=True
server="http://dqsegdb3.phy.syr.edu"
files_per_publish=5000
threading=1
synch="14:30"


if debug:
    log_level="DEBUG"
else:
    log_level="INFO"

if gap_publish:
    comment_cp="#"
else:
    comment_cp=""

if synch:
    synch_command="-x "+synch
else:
    synch_commmand=""

gps_range_L1=(937035615,972535615)
gps_range_H1=(944535616,973035616)
gps_range_V1=(928787010,975287010)

gps_range=[start_time,end_time]
if interferometer=="V":
    gps_range[0]=max(start_time,gps_range_V1[0])
    gps_range[1]=min(end_time,gps_range_V1[1])
elif interferometer=="H":
    gps_range[0]=max(start_time,gps_range_H1[0])
    gps_range[1]=min(end_time,gps_range_H1[1])
elif  interferometer=="L":
    gps_range[0]=max(start_time,gps_range_L1[0])
    gps_range[1]=min(end_time,gps_range_L1[1])
try:
    os.makedirs(run_dir)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(run_dir):
        pass
    else:
        raise
try:
    os.makedirs(run_dir+"/var/spool")
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(run_dir):
        pass
    else:
        raise
try:
    os.makedirs(run_dir+"/var/log")
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(run_dir):
        pass
    else:
        raise

try:
    os.makedirs(run_dir+"/var/run")
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(run_dir):
        pass
    else:
        raise

# options = { 'log_file': '/home/rfisher/DQSEGDB/DQSEGDBClient/var/log/L-DQ_Segments.log', 'log_level': 'DEBUG', 'dry_run': None, 'segment_url': 'http://slwebtest.virgo.infn.it', 'thread_count': '20', 'start_time': '999999999', 'state_file': '/home/rfisher/DQSEGDB/DQSEGDBClient/var/spool/L-DQ_Segments_long_test.xml', 'end_time': '105819443', 'offset': '10', 'pid_file': '/home/rfisher/DQSEGDB/DQSEGDBClient/var/run/L-DQ_Segments.pid', 'segments_file': None, 'input_directory': '/archive/frames/dmt/ER4/DQ/L1', 'multiple_files': '60'}

#locals() now contains a dictionary of all the keys I need to fill in in the scripts below!

#I need to make this a script that can take 3 inputs still!!! I shouldn't be settin the inf or start or end in the text below! I should just be setting the directory structure up!
if site=='CIT':
    if interferometer=="V":
        input_directory="/archive/frames/online/DQ/V1"
    elif interferometer=="H" or interferometer=="L":
        input_directory="/archive/frames/dmt/L${inf}O/triggers/DQ_Segments"
if site=='SYR':
    if interferometer=="V":
        input_directory="/frames/dmt/V1"
    elif interferometer=="H" or interferometer=="L":
        input_directory="/frames/dmt/L${inf}O/triggers/DQ_Segments"



## Generate bash script file for submit file to call with parameters

script_text="""#!/bin/bash

# Assumes lib directory is one down from this script:
#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR=%(dqsegdb_code_DIR)s

#echo "Setting PYTHONPATH to point to $DIR/lib"
export PYTHONPATH=$PYTHONPATH:$DIR/dqsegdb
export PATH=$PATH:$DIR/bin/

inf=$1
start=$2
end=$3

echo "Run directory="
echo "%(run_dir)s"

#mkdir -p %(run_dir)s/var/spool
#mkdir -p %(run_dir)s/var/log
#mkdir -p %(run_dir)s/var/run

%(comment_cp)scp %(template_state_file)s %(run_dir)s/var/spool/${inf}-DQ_Segments_S6_${start}_${end}.xml

rm -f /usr1/%(user_name)s/${inf}-DQ_Segments_S6_${start}_${end}.log

/usr/bin/env python -W ignore::DeprecationWarning %(publish_executable)s --segment-url %(server)s --state-file=%(run_dir)s/var/spool/${inf}-DQ_Segments_S6_${start}_${end}.xml --pid-file=%(run_dir)s/var/run/${inf}-DQ_Segments_S6_${start}_${end}.pid --log-file=/usr1/%(user_name)s/${inf}-DQ_Segments_S6_${start}_${end}.log --input-directory=%(input_directory)s --log-level %(log_level)s -m %(files_per_publish)s -c %(threading)s -b ${start} -e ${end} -o %(offset)s %(synch_command)s

cp /usr1/%(user_name)s/${inf}-DQ_Segments_S6_${start}_${end}.log %(log_file_dir)s/${inf}-DQ_Segments_S6_${start}_${end}.log 

rm -f /usr1/%(user_name)s/${inf}-DQ_Segments_S6_${start}_${end}.log
""" % locals()

script_fh=open(executable_name,'w')
perms=stat.S_IXGRP |stat.S_IRGRP|stat.S_IROTH|stat.S_IXOTH |stat.S_IRWXU
os.chmod(executable_name,perms)
script_fh.write(script_text)
script_fh.close()

if mode=="single":
    print "Run the following command:"
    print " ".join([executable_name,interferometer,str(start_time),str(end_time)])
    sys.exit()

## Generate sub file and dag file


run_dir=run_dir+"/"
# Initialize dag
dag = pipeline.CondorDAG('s6publish.log', dax=False)
dag.set_dag_file(run_dir+'s6publish')


subFile = pipeline.CondorDAGJob(mode, executable_name)
subFile.set_stdout_file(run_dir+'s6publish-$(cluster)-$(process).out')
subFile.set_stderr_file(run_dir+'s6publish-$(cluster)-$(process).err')
subFile.set_sub_file(run_dir+'s6publish.sub')
#print "Subfile:"
#print subFile.get_sub_file()

#blah2=open('v1_run_commands.txt','r')
#cmds=blah2.readlines()
#cmds
#cmds=[i.strip() for i in cmds]
times=[]
#print "Computing times:"
#print gps_range
#print gps_stride_per_job
for i in range(gps_range[0],gps_range[1],gps_stride_per_job):
    times.append((i,i+gps_stride_per_job))
#print times
# now times contains the start and end for each job in the dag

for i in times: #cmds:
    #time1 = i.split(' ')[-2]
    time1=i[0]
    #time2 = i.split(' ')[-1]
    time2=i[1]
    ifo = interferometer
    #node = subFile.create_node()
    node = pipeline.CondorDAGNode(subFile)
    node.add_var_arg(ifo)
    node.add_var_arg(str(time1))
    node.add_var_arg(str(time2))
    dag.add_node(node)

print "Writing dag file:"
print dag.get_dag_file()
dag.write_dag()
#print "Writing sub file:"
#print dag.get_sub_file()
#print dag.get_jobs()
dag.write_sub_files()

print "Executable and DAG created, please run dag by submitting:"
print "condor_submit_dag "+run_dir+'s6publish.dag'
