#!/usr/bin/env python

import datetime
import os
from datetime import date
import shutil

primary_dir='/backup/primary/'
monthly_dir='/backup/monthly/'

today = date.today()

# Ok, first copying the current backup into the monthly directory:
primaryNames=os.listdir(primary_dir)
if len(primaryNames) > 1:
  raise ValueError("There should only be one file in the primary backup directory, something's off!")
elif len(primaryNames)==0:
  raise ValueError("There should be a file in the primary backup directory... check backup script's cron log.")
else:
  shutil.copyfile(primary_dir+primaryNames[0],monthly_dir+primaryNames[0])
