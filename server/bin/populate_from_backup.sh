#!/bin/bash

# First, get the appropriate file and copy it over to the /tmp/ directory
mkdir /tmp/mysql_dump
cd /tmp/mysql_dump
N=$(date +%y-%m-%d).tar.gz
scp root@dqsegdb5.phy.syr.edu:/backup/primary/$N /dqsegdb5_backup/primary
cp /dqsegdb5_backup/primary/$N .
tar -xvzf $N 
if [ -e /tmp/mysql_dump/tbl_values.sql ]; then
  echo "Files seem to have unpacked correctly."
else
  echo "Import from backup failed somewhere in scp or tar -x step."
  exit 1
fi

# To import from --tab option

# First clean the database out:
mysql -e "DROP DATABASE IF EXISTS dqsegdb5_backup"
mysql -e "CREATE DATABASE dqsegdb5_backup"
mysql -e "use dqsegdb5_backup"
mysql -e "GRANT SELECT, INSERT, UPDATE ON dqsegdb5_backup.* TO 'dqsegdb_user'@'localhost'"
mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'admin'@'localhost'"

# Next create the structure:
cat /tmp/mysql_dump/tbl_value_groups.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_values.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_dq_flags.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_dq_flag_versions.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_processes.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_process_args.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_segments.sql |mysql dqsegdb5_backup
cat /tmp/mysql_dump/tbl_segment_summary.sql |mysql dqsegdb5_backup

# Then import the data
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_value_groups.txt
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_values.txt
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_dq_flags.txt
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_dq_flag_versions.txt
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_processes.txt
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_process_args.txt
mysqlimport --use-threads=4 --local dqsegdb5_backup /tmp/mysql_dump/tbl_segment*.txt
# Note that doing it this way doubles the import speed by running the two segment tables in parallel

# Lastly, clean up the /tmp/ directory:
rm -rf /tmp/mysql_dump
