# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.

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
#!/bin/bash

# Set backup start date.
backup_date=$(date +%Y-%m-%d)

# Set backup import start time.
backup_import_start_time=$(date +'%H:%M:%S')
# Add backup import start date/time.
mysql -u dqsegdb_backup -pdqsegdb_backup_pw -e "UPDATE dqsegdb_regression_tests.tbl_backups SET import_time_start = '${backup_import_start_time}' WHERE backup_date LIKE '${backup_date}%'"

# First, get the appropriate file and copy it over to the /tmp/ directory
mkdir /tmp/mysql_dump
N=$(date +%y-%m-%d).tar.gz
#scp root@dqsegdb5.phy.syr.edu:/backup/primary/$N /backup/segdb/segments/primary
cd /backup/segdb/segments/primary/
#rsync -avP 10.20.5.47::dqsegdb/* .
cd /tmp/mysql_dump 
cp /backup/segdb/segments/primary/$N .
tar -xvzf $N
if [ -e /tmp/mysql_dump/tbl_values.sql ]; then
  echo "Files seem to have unpacked correctly."
else
  echo "Import from backup failed somewhere in scp or tar -x step."
  exit 1
fi

# To import from --tab option

date1=$(date -u +"%s")
# First clean the database out:
mysql -u root -e "DROP DATABASE IF EXISTS segments_backup"
mysql -u root -e "CREATE DATABASE segments_backup"
mysql -u root -e "use segments_backup"
mysql -u root -e "GRANT SELECT, INSERT, UPDATE ON segments_backup.* TO 'dqsegdb_user'@'localhost'"
mysql -u root -e "GRANT ALL PRIVILEGES ON * . * TO 'admin'@'localhost'"

# Next create the structure:
cat /tmp/mysql_dump/tbl_value_groups.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_values.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_dq_flags.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_dq_flag_versions.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_processes.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_process_args.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_segments.sql |mysql -u root segments_backup
cat /tmp/mysql_dump/tbl_segment_summary.sql |mysql -u root segments_backup

# Then import the data
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_value_groups.txt
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_values.txt
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_dq_flags.txt
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_dq_flag_versions.txt
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_processes.txt
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_process_args.txt
mysqlimport -u root --use-threads=4 --local segments_backup /tmp/mysql_dump/tbl_segment*.txt
# Note that doing it this way doubles the import speed by running the two segment tables in parallel
date2=$(date -u +"%s")
diff=$(($date2-$date1))
echo "$(date) : $(($diff / 60)) minutes and $(($diff % 60)) seconds elapsed for import." >> /usr1/ldbd/backup_logging

# Lastly, clean up the /tmp/ directory:
rm -rf /tmp/mysql_dump

# Set backup import end time.
backup_import_stop_time=$(date +'%H:%M:%S')
# Add backup import end date/time.
mysql -u dqsegdb_backup -pdqsegdb_backup_pw -e "UPDATE dqsegdb_regression_tests.tbl_backups SET import_time_stop = '${backup_import_stop_time}' WHERE backup_date LIKE '${backup_date}%'"
