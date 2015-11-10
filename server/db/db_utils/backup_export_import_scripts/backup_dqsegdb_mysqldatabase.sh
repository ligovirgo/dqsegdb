#!/bin/bash

# Set backup date.
backup_date=$(date +%Y-%m-%d)

# Set backup export start time.
backup_export_start_time=$(date +'%H:%M:%S')
# Insert backup export start date/time.
mysql -h segments-backup.ligo.org -u dqsegdb_backup -pdqsegdb_backup_pw -e "INSERT INTO dqsegdb_regression_tests.tbl_backups (backup_date, export_time_start) VALUES ('${backup_date}', '${backup_export_start_time}')"

mkdir /tmp/mysql_dump
chmod a+rwx /tmp/mysql_dump
time mysqldump --single-transaction -u root dqsegdb --tab=/tmp/mysql_dump
cd /tmp/mysql_dump
tar -zcvf "/backup/segdb/segments/primary/$(date +%y-%m-%d).tar.gz" *
if [ -z "/backup/segdb/segments/primary/$(date +%y-%m-%d).tar.gz" ]; then
  echo "Didn't find my tar'd file: raise error!" 1>&2
  exit 1
else
  # Found the tarball, so we can remove the mysql_dump temp directory
  cd ${HOME}
  rm -rf /tmp/mysql_dump
  # rsync to backup/segdb/segments!
  #rsync /backup/segdb/segments/primary/* 10.14.0.105::dqsegdb
fi

# Set backup export end time.
backup_export_stop_time=$(date +'%H:%M:%S')
# Add backup export end date/time.
mysql -h segments-backup.ligo.org -u dqsegdb_backup -pdqsegdb_backup_pw -e "UPDATE dqsegdb_regression_tests.tbl_backups SET export_time_stop = '${backup_export_stop_time}' WHERE backup_date LIKE '${backup_date}%'"
