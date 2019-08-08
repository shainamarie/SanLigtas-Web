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


#Authorization and Index page views
@app.route('/', methods=['POST', 'GET'])
def index():
	return render_template('login.html')

@app.route('/unauthorized')
def unauthorized():
	return render_template('unauthorized.html')

@app.route('/login', methods=['POST', 'GET'])
def loginprocess():
	if request.method == 'POST':
		session.pop('user', None)
		email = request.form['email']
		password = request.form['password']
		url = api_url+'/authadmin/login'
		files = {
			'email' : (None, email),
			'password' : (None, password),
		}
		response = requests.request('POST', url, files=files)
		login_dict = json.loads(response.text)
		message = login_dict["message"]
		print(message)
		if message == "Login failed. Check email or password.":
			return render_template('login.html')
		else:
			role = login_dict["role"]
			autho = login_dict["Authorization"]
			first_name = login_dict["first_name"]
			last_name = login_dict["last_name"]
			username = login_dict["username"]
			token = api_login(autho, username, last_name, first_name, role)
		return redirect(url_for('mainadminhome', username=username, last_name=last_name, first_name=first_name))
	else:
		return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
	if g.user:
		print(session['token'])
		url = api_url+'/authadmin/logout'
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response = requests.request('POST', url, headers=headers)
		print(response.text)
		return redirect(url_for('index'))
	else:
		return redirect('unauthorized')


#Profile views
@app.route('/own/profile')
def ownprofile():
	if g.user:
		url1 = api_url+'/user/admin/search/'+session['user']
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		url = api_url+'/user/admin/'+json_data1["data"][0]["public_id"]
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data= response.json()
		return render_template('profile-page.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/profile-page/admin/<public_id>')
def viewprofile_admin(public_id):
	if g.user:
		url = api_url+'/user/admin/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		return render_template('profile-admin.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/profile-page/admin2/<public_id>')
def viewprofile_admin2(public_id):
	if g.user:
		url = api_url+'/user/admin/search/'+username
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		return render_template('profile-admin2.html', json_data=json_data)
	else:
		return redirect('unauthorized')


@app.route('/profile-page/mobile/<public_id>')
def viewprofile_mobile(public_id):
	if g.user:
		url = api_url+'/user/mobile/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(username)
		print(json_data)
		return render_template('profile-mobile.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/profile-page/evacuees/<public_id>')
def viewprofile_evacuee(public_id):
	if g.user:
		url = api_url+'/evacuees/'+public_id 	        
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()

		return render_template('profile-evacuee.html', json_data=json_data)
	else:
		return redirect('unauthorized')


#Statistics
@app.route('/plot')
def plot():
	return render_template('chart.html')

@app.route('/statistics-frequency')
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
@app.route('/main-admin/home/')
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


#Search
@app.route('/search/center', methods=['POST'])
def search_center():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/distcenter/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)

			if json_data == {'data': []}:
				return render_template('no-center-result.html')
			else:
				return render_template('center-result.html', json_data=json_data)
	else:
		return redirect('unauthorized')	

@app.route('/search/user', methods=['POST'])
def search_user():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/user/admin/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)
			if json_data == {'data': []}:
				return render_template('no-user-result.html')
			else:
				return render_template('user-result.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/search/evacuee/<name>/<public_id>', methods=['POST'])
def search_evacuee(name, public_id):
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/evacuees/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)
			if json_data == {'data': []}:
				return render_template('no-user-result.html')
			else:
				return render_template('evacuee-result.html', json_data=json_data, name=name, public_id=public_id)
	else:
		return redirect('unauthorized')

@app.route('/search/admin/<name>/<public_id>', methods=['POST'])
def search_admin(name, public_id):
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/user/admin/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)
			if json_data == {'data': []}:
				return render_template('no-user-result.html')
			else:
				return render_template('admin-result.html', json_data=json_data, name=name, public_id=public_id)
	else:
		return redirect('unauthorized')


#User Admin
@app.route('/view/admin')
def viewuser():
	if g.user:
		url = api_url+'/user/admin/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		if json_data == {'data': []}:
			return render_template('no-user-result.html')
		else:
			return render_template('view-user.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/add/user/admin', methods=['POST', 'GET'])
def add_user():	
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin':
				email = request.form.get('email', '')
				first_name = request.form.get('first_name', '')
				last_name = request.form.get('last_name', '')
				role = request.form.get('role', '')
				username = request.form.get('username', '')
				gender = request.form.get('gender', '')
				password_generator = generate_password()
				password = password_generator
				url = api_url+'/user/admin/'
				files = {
					'email' : (None, email),
					'username' : (None, username),
					'password' : (None, password),
					'role' : (None, role),
					'first_name' : (None, first_name),
					'last_name' : (None, last_name),
					'gender' : (None, gender)
				}
				response = requests.request('POST', url, files=files)
				login_dict = json.loads(response.text)
				message = login_dict["message"]
				if message == "Email already used.":
					return redirect(url_for('add_user'))
				else:
					mat = password
					msg = Message(body="You have been registered on SanLigtas.\n Username:"+username+"\n Password: "+mat+"\n Welcome to the team!",
						sender="noreply@sanligtas.com",
						recipients=[email],
						subject="Welcome to San Ligtas")
					mail.send(msg)
				return redirect(url_for('viewuser'))
			else:
				return redirect(url_for('unauthorized'))
		else:
			return render_template('add-user.html')
	else:
		return redirect(url_for('unauthorized'))

@app.route('/update/admin/<public_id>', methods=['POST', 'GET'])
def update_admin(public_id):
	if g.user:
		url1 = api_url+'/user/admin/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				username = request.form.get('username', '')
				email = request.form.get('email', '')
				first_name = request.form.get('first_name', '')
				last_name = request.form.get('last_name', '')
				role = request.form.get('role', '')
				gender = request.form.get('gender', '')
				public_id = public_id

				url = api_url+'/user/admin/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
						
					'username' : (None, username),
					'email' : (None, email),
					'first_name' : (None, first_name),
					'last_name' : (None, last_name),
					'password' : 'admin',
					'role' : (None, role),
					'gender' : (None, gender)
				}
				response = requests.request('PUT', url, headers=headers, data=payload)
				del_dict = json.loads(response.text)

				return redirect(url_for('viewuser'))
			else:
				return redirect('unauthorized')
		else:

			return render_template('edit-admin.html', username=json_data1['username'], email=json_data1['email'], public_id=json_data1['public_id'], first_name=json_data1['first_name'], last_name=json_data1['last_name'], role=json_data1['role'], gender=json_data1['gender'] )	
	else:
		return redirect('unauthorized')

@app.route('/delete/admin/<public_id>')
def delete_admin(public_id):
	if g.user:
		print(session['token'])
		headers = { 'Authorization' : '{}'.format(session['token']) }
		public_id = public_id
		print(public_id)
		url = api_url+'/user/admin/'+public_id
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')



#User Mobile
@app.route('/view/mobile')
def viewmobile():
	if g.user:
		url = api_url+'/user/mobile/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		# print(json_data['data'][0]['registered_on'])
		print(json_data)
		if json_data == {'data': []}:
			return render_template('no-user-result.html')
		else:
			return render_template('view-mobile.html', json_data=json_data)
	else:
		return redirect(url_for('unauthorized'))

@app.route('/delete/mobile/<public_id>')
def delete_mobile(public_id):
	if g.user:
		if session['role'] == 'Main Admin':
			print(session['token'])
			headers = { 'Authorization' : '{}'.format(session['token']) }
			public_id = public_id
			print(public_id)
			url = api_url+'/user/mobile/'+public_id
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('viewmobile'))
		else:
			return redirect(url_for('unauthorized'))
	else: 
		return render_template('unauthorized')

@app.route('/update/mobile/<public_id>', methods=['POST', 'GET'])
def update_mobile(public_id):
	if g.user:
		url1 = api_url+'/user/mobile/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
	
		if request.method == 'POST':
			if session['role'] == 'Main Admin':

				username = request.form.get('username', '')
				email = request.form.get('email', '')
				first_name = request.form.get('first_name', '')
				last_name = request.form.get('last_name', '')
				birth_date = request.form.get('birth_date', '')
				address = request.form.get('address', '')
				gender = request.form.get('gender', '')
				contact_number = request.form.get('contact_number', '')
				public_id = public_id

				url = api_url+'/user/mobile/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
						
					'username' : (None, username),
					'email' : (None, email),
					'first_name' : (None, first_name),
					'last_name' : (None, last_name),
					'birth_date' : (None, birth_date),
					'address' : (None, address),
					'contact_number' : (None, contact_number),
					'gender' : (None, gender)
				}
				response = requests.request('PUT', url, headers=headers, data=payload)		
				del_dict = json.loads(response.text)


				return redirect(url_for('viewmobile'))
			else:
				return redirect('unauthorized')
		else:

			return render_template('edit-mobile.html', address=json_data1['address'], username=json_data1['username'], birth_date=json_data1['birth_date'], email=json_data1['email'], public_id=json_data1['public_id'], first_name=json_data1['first_name'], last_name=json_data1['last_name'], contact_number=json_data1['contact_number'], gender=json_data1['gender'] )	
	else:
		return redirect('unauthorized')


#Household
#Evacuee	
@app.route('/view/evacuees')
def viewevacuees():
	if g.user:
		url = api_url+'/evacuees/'
		url2 = api_url+'/house/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		response2 = requests.request('GET', url2, headers=headers)
		json_data = response.json()
		json_data2 = response2.json()
		return render_template('view-evacuees.html', json_data=json_data, json_data2=json_data2)
	else:
		return redirect(url_for('unauthorized'))

@app.route('/add/evacuee',methods=['POST', 'GET'])
def add_evacuee():
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				n = 4
				name = request.form.get('name', '')
				home_id = ''.join(["%s" % randint(0, 9) for num in range(0, n)])
				address = request.form.get('address', '')
				gender = request.form.get('gender', '')
				age = request.form.get('age', '')
				religion = request.form.get('religion', '')
				civil_status = request.form.get('civil_status', '')
				educ_attainment = request.form.get('educ_attainment', '')
				occupation = request.form.get('occupation', '')

				url = api_url+'/evacuees/'
				files = {
					'name' : (None, name),
					'home_id' : (None, home_id),
					'address' : (None, address),
					'gender' : (None, gender),
					'age' : (None, age),
					'religion' : (None, religion),
					'civil_status' : (None, civil_status),
					'educ_attainment' : (None, educ_attainment),
					'occupation' : (None, occupation)
				}
				headers = { 'Authorization' : '{}'.format(session['token']) }
				response = requests.request('POST', url, files=files, headers=headers)
				json_data = response.json()

				return redirect(url_for('viewevacuees'))
			else:
				return redirect(url_for('unauthorized'))
		else:
			return render_template('add-evacuee.html')
	else:
		return redirect(url_for('unauthorized'))

@app.route('/update/evacuee/<public_id>', methods=['POST', 'GET'])
def update_evacuee(public_id):
	if g.user:
		url1 = api_url+'/evacuees/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin':

				name = request.form.get('name', '')
				gender = request.form.get('gender', '')
				age = request.form.get('age', '')
				religion = request.form.get('religion', '')
				civil_status = request.form.get('civil_status', '')
				educ_attainment = request.form.get('educ_attainment', '')
				occupation = request.form.get('occupation', '')

				url = api_url+'/evacuees/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {	
					'name' : (None, name),
					'gender' : (None, gender),
					'age' : (None, age),
					'religion' : (None, religion),
					'civil_status' : (None, civil_status),
					'educ_attainment' : (None, educ_attainment),
					'occupation' : (None, occupation)
				}

				response = requests.request('PUT', url, headers=headers, data=payload)
				del_dict = json.loads(response.text)
				
				return redirect(url_for('viewevacuees'))
			else:
				return redirect('unauthorized')
		else:
			return render_template('edit-evacuee.html',	 name=json_data1['name'], religion=json_data1['religion'], age=json_data1['age'], public_id=json_data1['public_id'], civil_status=json_data1['civil_status'], educ_attainment=json_data1['educ_attainment'], occupation=json_data1['occupation'] )	
	else:
		return redirect('unauthorized')

@app.route('/delete/evacuee/<public_id>')
def delete_evacuee(public_id):
	if g.user:
		print (session['role'])
		if session['role'] == 'Social Worker Admin' or session['role'] == 'Main Admin':
			print(session['token'])
			headers = { 'Authorization' : '{}'.format(session['token']) }
			
			url = api_url+'/evacuees/'+public_id
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('viewevacuees'))
		else:
			return redirect(url_for('unauthorized'))
	else: 
		return render_template('unauthorized')



#Change password user
@app.route('/change/password/<public_id>', methods=['POST', 'GET'])
def change_pass(public_id):
	if g.user:
		public_id = public_id
		if request.method == 'POST':
			old_pass = request.form.get('old_pass', '')		
			new_pass = request.form.get('new_pass', '')	

			url = api_url+'/user/admin/'+public_id
			headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)

			# data_old_pass = json_data['password']
			# print(data_old_pass)
			username = json_data['username']
			print(username)
			print(session['user'])

			if new_pass == old_pass and session['user'] == username:
				url2 = api_url+'/user/admin/password/'+public_id
				files = {
						'new_pass' : (None, new_pass)
					}
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				response2 = requests.request('PUT', url2, files=files, headers=headers)
				json_data2 = response2.json()
				# print(json_data2)
				message = json_data2['message']
				print(message)

				if message == "Password successfully updated.":
					return redirect('/')
				else:
					return render_template('change-password.html', public_id=public_id)
			else:
				return "unauthorized ka gurl"
		else:
			return render_template('change-password.html', public_id=public_id)

	else:
		return redirect('unauthorized')


#Evacuation/Distribution Center
@app.route('/view/center')
def view_center():
	if g.user:
		url = api_url+'/distcenter/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)

		if json_data == {'data': []}:
			return render_template('no-center-result.html')
		else:
			return render_template('view-evac.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@app.route('/assign/admin/center/<name>/<public_id>', methods=['POST', 'GET'])
def assign_admin(public_id, name):
	if g.user:
		url1 = api_url+'/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		latitude = json_data1["latitude"]
		longitude = json_data1["longitude"]


		if request.method == 'POST':
			center_public_id = public_id
			center_admin = request.form.get('center_admin', '')

			url2 = api_url+'/user/admin/search/'+center_admin
			response2 = requests.request('GET', url2, headers=headers)
			json_data2 = response2.json()
			print(json_data2)

			role = json_data2["data"][0]["role"]

			if role == "Social Worker Admin" or role == "Main Admin":
				files = {					
					'center_public_id': (None, center_public_id),
					'center_admin': (None, center_admin)
				}
				headers = {
					'Authorization': '{}'.format(session['token'])
				}
				url = api_url+'/distcenter/assign/admin/'+public_id
				response = requests.request('POST', url, files=files, headers=headers)
				json_data = response.json()
				print(json_data)
				message = json_data["message"]

				if message == "admin assigned successfully":
					return redirect(url_for('view_spec_center', public_id=public_id, name=name ))
				else:
					return "Dili pwede dzaii"
			else:
				return "Dili pwede kay dili Social Worker"
		else:
			return render_template('assign_admin.html', name=name, public_id=public_id, latitude=latitude, longitude=longitude)
	else:
		return redirect(url_for('unauthorized'))

@app.route('/assign/searched/admin/<name>/<public_id>/<username>')
def assign_searched_admin(name, public_id, username):
	if g.user:
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		files = {	
			'center_public_id': (None, public_id),
			'center_admin': (None, username)
		}
		url = api_url+'/distcenter/assign/admin/'+public_id
		response = requests.request('POST', url, headers=headers, files=files,  )
		json_data1 = response.json()
		print(public_id)
		print(username)
		print(json_data1)

		message = json_data1["message"]

		if message == "admin assigned successfully":
			return redirect(url_for('view_spec_center', public_id=public_id, name=name ))
		else:
			return "Dili pwede dzaii"
	else:
		return redirect('unauthorized')

@app.route('/assign/evacuee/<name>/<public_id>', methods=['POST', 'GET'])
def assign_evacuee(name, public_id):
	if g.user:
		url1 = api_url+'/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		latitude = json_data1["latitude"]
		longitude = json_data1["longitude"]

		if request.method == "POST":
			if session['role'] == "Main Admin" or session['role'] == "Social Worker Admin":
				name = request.form.get('name', '')

				url1 = api_url+'/evacuees/search/'+name
				headers = {
						'Authorization': '{}'.format(session['token'])
					}
				response1 = requests.request('GET', url1, headers=headers)
				json_data1 = response1.json()
				homeid = json_data1["data"][0]["home_id"]

				url2 = api_url+'/distcenter/search/'+public_id
				response2 = requests.request('GET', url2, headers=headers)
				json_data2 = response2.json()
				centerid = json_data2["data"][0]["id"]

				files = {
					'home_id' : (None, homeid),
					'center_id' : (None, centerid)
				}
				url3 = api_url+'/evacuees/assign/evacuee'
				response3 = requests.request('PUT', url3, headers=headers, files=files,  )
				json_data3 = response3.json()

				return redirect(url_for('view_spec_center', public_id=public_id, name=name))
			else: 
				return "Dili ka Main Admin dzaii"
		else:
			return render_template('assign-evacuee.html', public_id=public_id, name=name, latitude=latitude, longitude=longitude)
	else:
		return redirect('unauthorized')

@app.route('/assign/searched/evacuee/<name>/<public_id>/<home_id>')
def assign_searched_evacuee(name, public_id, home_id):
	if g.user:
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		url = api_url+'/distcenter/search/'+public_id
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		centerid = json_data["data"][0]["id"]
		files = {
			'home_id' : (None, home_id),
			'center_id' : (None, centerid)
		}
		url1 = api_url+'/evacuees/assign/evacuee'
		response1 = requests.request('PUT', url1, headers=headers, files=files,  )
		json_data1 = response1.json()

		return redirect(url_for('view_spec_center', public_id=public_id, name=name))

	else:
		return redirect('unauthorized')

@app.route('/view/center/<name>/<public_id>')
def view_spec_center(name, public_id):
	if g.user:
		url = api_url+'/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		center_id = json_data["id"]
		print(center_id)
		
		url1 = api_url+'/distcenter/assign/admin/'+public_id
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		address = json_data['address']

		url2 = api_url+'/evacuees/get/center/'+center_id
		response2 = requests.request('GET', url2, headers=headers)
		json_data2 = response2.json()
		print(json_data2)

		url3 = api_url+'/reliefupdates/get/'+public_id
		response3 = requests.request('GET', url3, headers=headers)
		json_data3 = response3.json()

		return render_template('view-center.html', json_data=json_data, json_data1=json_data1, json_data2=json_data2, json_data3=json_data3)
	else:
		return redirect('unauthorized')


@app.route('/add/center', methods=['POST', 'GET'])
def add_center():
	if g.user:
		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				address = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				#google_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyAayoLLtuuXjGtgaxIURWpfzRrGDZ1KgVc')
				#google_dict = json.loads(google_response.text)#
				#latitude=google_dict['results'][0]['geometry']['location']['lat']
				#longitude=google_dict['results'][0]['geometry']['location']['lng']
				#lat = str(latitude).encode('utf-16')
				#long1 = str(longitude).encode('utf-16')

				url = api_url+'/distcenter/'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}	
				files = {
				
					'name': (None, name),
					'address': (None, address),
					'capacity': (None, capacity)
				}

				response = requests.request('POST', url, files=files, headers=headers)
				distcenter_dict = json.loads(response.text)
				print(response.text)
				message = distcenter_dict["message"]
				print(message)
				if message == "Name already used.":
					return redirect(url_for('add_center'))
				else:
					print(response)
				return redirect(url_for('view_center'))
			else: 
				return "unauthorized lage ka"
		else:
			return render_template('add-evac.html')
	else:
		return redirect('unauthorized')




@app.route('/update/center/<public_id>', methods=['POST', 'GET'])
def update_center(public_id):
	if g.user:
		url1 = api_url+'/distcenter/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		center_dict = json.loads(response1.text)

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				address = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				url = api_url+'/distcenter/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				files = {
					'name' : (None, name),
					'address' : (None, address),
					'capacity' : (None, capacity)
				}
				response = requests.request('PUT', url, headers=headers, files=files)
				del_dict = json.loads(response.text)

				return redirect(url_for('view_center'))
			else:
				return redirect('unauthorized')
		else:
			return render_template('edit-evacs.html', name=center_dict['name'], address=center_dict['address'], public_id=center_dict['public_id'], capacity=center_dict['capacity'])
	else:
		return redirect('unauthorized')

@app.route('/delete/center/<public_id>')
def delete_evac(public_id):
	if g.user:
		if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':

			headers = { 'Authorization' : '{}'.format(session['token']) }
			public_id = public_id
			url = api_url+'/distcenter/'+public_id
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('view_center'))
		else:
			return "unauthorized ka gurl"
	else: 
		return render_template('unauthorized')



#Relief Goods
@app.route('/relief/updates')
def relief_updates():
	if g.user:
		url = api_url+'/reliefupdates/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)


		return render_template('relief-updates.html', json_data=json_data)
	else:
		return redirect(url_for('unauthorized'))

@app.route('/add/relief/<name>/<public_id>', methods=['POST', 'GET'])
def add_relief(name, public_id):
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin' or session['role'] == 'Relief Admin':
				number_goods = request.form.get('number_goods', '')
				center_public_id = public_id
				center = name

				url = api_url+'/reliefupdates/'
				files = {
					'center' : (None, center),
					'center_public_id' : (None, center_public_id),
					'number_goods' : (None, number_goods)
				}
				headers = { 'Authorization' : '{}'.format(session['token']) }
				response = requests.request('POST', url, files=files, headers=headers)
				json_data = response.json()
				print(json_data)

				return redirect(url_for('view_spec_center', name=name, public_id=public_id))
			else:
				return redirect(url_for('unauthorized'))
		else:
			return render_template('add-relief.html', name=name, public_id=public_id)

	else:
		return redirect(url_for('unauthorized'))	

if __name__=='__main__':
    app.run(debug=True, port=8080)	