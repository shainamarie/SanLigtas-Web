from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_mail import Mail, Message
from flask_googlemaps import GoogleMaps, Map
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
#from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource

from .blueprints.auth_routes import auth_bp
from .blueprints.center_routes import center_bp
from .blueprints.evac_routes import evac_bp
from .blueprints.goods_routes import goods_bp
from .blueprints.profile_routes import profile_bp
from .blueprints.search_routes import search_bp
from .blueprints.user_routes import user_bp

import dateutil.parser
import requests, json
import pytemperature
import string
from random import *
import random

app = Flask(__name__, template_folder="templates")
api_url = 'http://127.0.0.1:5000'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'zxcvbnm'

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'    #content type sa mail dapat html type
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '3c42180c5ffb31'
app.config['MAIL_PASSWORD'] = '2f695055c2fd0f'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

app.register_blueprint(home, url_prefix='')
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(signup, url_prefix='/signup')

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

#Statistics
@app.route('/plot')
#app.route(/statistics)
def plot():
	return render_template('chart.html')

@app.route('/statistics-frequency')
#app.route(/statistics/age)
def stat():
	headers = {
			'Authorization' : '{}'.format(session['token'])
		}
	urls = api_url+'/evacuees/all_age_female'
	responses = requests.request('GET', urls, headers=headers)
	female_age = responses.json()
	print(female_age)
	print(female_age[0]["adult"])

	urls2 = api_url+'/evacuees/all_age_female'
	responses = requests.request('GET', urls2, headers=headers)
	male_age = responses.json()
	print(male_age)
	print(male_age[0]["adult"])
	return render_template('stat-freq.html', male_age=male_age, female_age=female_age)

#Homepage
@app.route('/dashboard')
#@app.route('/home')
def mainadminhome():
	if g.user:
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=8f46c985e7b5f885798e9a5a68d9c036&q=Iligan'
		json_data = requests.get(api_address).json()
		city = json_data['name']
		formatted_data = json_data['weather'][0]['description']
		weather_icon = json_data['weather'][0]['icon']
		temp = json_data['main']['temp']
		final_temp = pytemperature.k2c(temp)
		celcius = round(final_temp, 2)

		url = api_url+'/distcenter/'
		
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()

		return render_template('dashboard.html', json_data=json_data, username=session['user'], first_name=session['first_name'], last_name=session['last_name'],  weather=formatted_data, weather_icon=weather_icon, celcius=celcius, city=city )
	else:
		return redirect('unauthorized')

@app.route('/maps')
def maps():
	if g.user:
		url = api_url+'/distcenter/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)

		return render_template('maps.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/home')
def home():
	return render_template('home.html')


