#!/usr/bin/env python

import datetime
import os
from datetime import date
import shutil

primary_dir='/backup/primary/'
weekly_dir='/backup/weekly/'

today = date.today()

# Ok, first copying the current backup into the weekly directory:
primaryNames=os.listdir(primary_dir)
if len(primaryNames) > 1:
  raise ValueError("There should only be one file in the primary backup directory, something's off!")
elif len(primaryNames)==0:
  raise ValueError("There should be a file in the primary backup directory... check backup script's cron log.")
else:
  shutil.copyfile(primary_dir+primaryNames[0],weekly_dir+primaryNames[0])

# Now deleting anything older than a week in the weekly directory:
weeksAgo = today-datetime.timedelta(weeks = 4)
weeksAgo = datetime.datetime.combine(weeksAgo, datetime.time())
filenames = os.listdir(weekly_dir)

for i in filenames:
  dateString = i.split('.')[0]
  dateTimePy = datetime.datetime.strptime(dateString,"%y-%m-%d")
  if dateTimePy < weeksAgo:  # older than 5 weeks
    os.remove(weekly_dir+i)
