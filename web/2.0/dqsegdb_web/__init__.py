from flask import Flask
app = Flask(__name__)

import dqsegdb_web.views
import os

# Generate a secret key for the app session.
app.secret_key = os.urandom(16)
