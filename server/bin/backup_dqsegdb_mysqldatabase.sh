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
