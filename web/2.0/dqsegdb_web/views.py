from flask import jsonify, render_template, request, session
import time
import datetime

from dqsegdb_web import app
from dqsegdb_web.core import Constants, DAO

'''
This file contains all of the main Views for the DQSEGDB website. 
It is the file that is launched at 'flask run' time.
'''

@app.route('/')
def index():
    '''
    The home-page view.
    '''
    dao = DAO.DAO()
    return render_template('homepage.html')
