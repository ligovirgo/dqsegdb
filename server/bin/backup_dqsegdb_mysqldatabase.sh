#!/bin/bash
mkdir /tmp/mysql_dump
chmod a+rwx /tmp/mysql_dump
time mysqldump -u root dqsegdb --tab=/tmp/mysql_dump
cd /tmp/mysql_dump
tar -zcvf "/backup/primary/$(date +%y-%m-%d).tar.gz" *
if [ -z "/backup/primary/$(date +%y-%m-%d).tar.gz" ]; then
  echo "Didn't find my tar'd file: raise error!" 1>&2
  exit 1
else
  # Found the tarball, so we can remove the mysql_dump temp directory
  cd /root/
  rm -rf /tmp/mysql_dump
fi
