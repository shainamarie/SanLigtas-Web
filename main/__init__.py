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
g.mail = mail

from .blueprints.account_routes import account_bp
from .blueprints.announcement_routes import announce_bp
from .blueprints.auth_routes import auth_bp
from .blueprints.barangay_routes import barangay_bp
from .blueprints.general_routes import app_bp
from .blueprints.center_routes import center_bp
from .blueprints.family_routes import family_bp
from .blueprints.evac_routes import evac_bp
from .blueprints.goods_routes import goods_bp
from .blueprints.profile_routes import profile_bp
from .blueprints.role_routes import role_bp
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
app.register_blueprint(account_bp, url_prefix='/account')
app.register_blueprint(announce_bp, url_prefix='/announcement')
app.register_blueprint(barangay_bp, url_prefix='/barangay')
app.register_blueprint(family_bp, url_prefix='/family')
app.register_blueprint(role_bp, url_prefix='/role')

@app.before_request
def before_request():
    g.user = None
    g.token = None
    if 'user' in session and 'token' in session:
        g.user = session['user']
        g.token = session['token']
