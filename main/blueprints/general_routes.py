from flask import Blueprint, render_template, session, g
from flask import current_app as app
app_bp = Blueprint('apple', __name__)
api_url = app.config['API_URL']





#Statistics
@app_bp.route('/plot')
#app.route(/statistics)
def plot():
	return render_template('chart.html')

@app_bp.route('/statistics-frequency')
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
@app_bp.route('/dashboard')
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

@app_bp.route('/maps')
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

@app_bp.route('/home')
def home():
	return render_template('home.html')


