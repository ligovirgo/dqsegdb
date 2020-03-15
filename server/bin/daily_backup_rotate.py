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
#!/usr/bin/env python

import datetime
import os
from datetime import date
import shutil

primary_dir='/backup/primary/'
daily_dir='/backup/daily/'

today = date.today()

# Ok, first moving the current backup into the daily directory:
primaryNames=os.listdir(primary_dir)
if len(primaryNames) > 1:
  raise ValueError("There should only be one file in the primary backup directory, something's off!")
elif len(primaryNames)==0:
  raise ValueError("There should be a file in the primary backup directory... check backup script's cron log.")
else:
  os.rename(primary_dir+primaryNames[0],daily_dir+primaryNames[0])

# Now deleting anything older than a week in the daily directory:
weekAgo = today-datetime.timedelta(days = 7)
weekAgo = datetime.datetime.combine(weekAgo, datetime.time())
filenames = os.listdir(daily_dir)

for i in filenames:
  dateString = i.split('.')[0]
  dateTimePy = datetime.datetime.strptime(dateString,"%y-%m-%d")
  if dateTimePy < weekAgo:  # older than a week
    os.remove(daily_dir+i)
