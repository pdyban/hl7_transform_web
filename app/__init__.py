import os
from flask import Flask
app = Flask(__name__)

from app import routes

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

