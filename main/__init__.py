from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_mail import Mail, Message
from flask_googlemaps import GoogleMaps, Map
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
#from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource


import dateutil.parser
import requests, json
import pytemperature
import string
from random import *
import random

app = Flask(__name__, instance_relative_config=True, template_folder='templates')

app.config.from_object('config')
app.config.from_pyfile('config.py')

app.app_context().push()

mail = Mail(app)


from .blueprints.auth_routes import auth_bp
from .blueprints.general_routes import app_bp
from .blueprints.center_routes import center_bp
from .blueprints.evac_routes import evac_bp
from .blueprints.goods_routes import goods_bp
from .blueprints.profile_routes import profile_bp
from .blueprints.search_routes import search_bp
from .blueprints.user_routes import user_bp
	
app.register_blueprint(app_bp, url_prefix='')
app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(center_bp, url_prefix='/center')
app.register_blueprint(evac_bp, url_prefix='/evacuees')
app.register_blueprint(goods_bp, url_prefix='/goods')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(user_bp, url_prefix='/user')

#Functions: These define the functions within the views.
def api_login(autho, username, last_name, first_name, role):
	session['user'] = username
	session['token'] = autho
	session['first_name'] = first_name 
	session['last_name'] = last_name
	session['role'] = role
	g.token = session['token'] 
	g.user = session['user']
	return session['token']

def generate_password():
	characters = string.ascii_letters + string.punctuation + string.digits
	password = "".join(choice(characters) for x in range(randint(8, 16)))
	return password

@app.before_request
def before_request():
    g.user = None
    g.token = None
    if 'user' in session and 'token' in session:
        g.user = session['user']
        g.token = session['token']
