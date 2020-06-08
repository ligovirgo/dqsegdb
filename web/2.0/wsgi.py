#!/usr/bin/env python

import sys
import site

site.addsitedir('/var/www/flask_apps/DQSEGDB_WEB/lib/python3.6/site-packages')

sys.path.insert(0, '/var/www/flask_apps/DQSEGDB_WEB/dqsegdb_web')

from dqsegdb_web import app as application

