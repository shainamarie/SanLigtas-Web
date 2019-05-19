from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_mail import Mail, Message
from flask_googlemaps import GoogleMaps, Map
import dateutil.parser
import requests, json
import pytemperature
import string
from random import *




app = Flask(__name__, template_folder="templates")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'zxcvbnm'
app.config['GOOGLEMAPS_KEY'] = 'qwertyuiop'

GoogleMaps(app, key="AIzaSyAayoLLtuuXjGtgaxIURWpfzRrGDZ1KgVc")

api_url = 'http://127.0.0.1:8080'


app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '3c42180c5ffb31'
app.config['MAIL_PASSWORD'] = '2f695055c2fd0f'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)


def api_login(autho, username, last_name, first_name, role):
	session['user'] = username
	session['token'] = autho
	session['first_name'] = first_name 
	session['last_name'] = last_name
	session['role'] = role
	g.token = session['token'] 
	g.user = session['user']
	print(g.user)
	return session['token']




def generate_password():
	characters = string.ascii_letters + string.punctuation + string.digits
	password = "".join(choice(characters) for x in range(randint(8, 16)))
	# print(password)

	return password


@app.before_request
def before_request():
    g.user = None
    g.token = None
    if 'user' in session and 'token' in session:
        g.user = session['user']
        g.token = session['token']


@app.route('/maps')
def maps():
	if g.user:
		url = 'http://127.0.0.1:5000/distcenter/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)

		return render_template('maps.html', json_data=json_data)
	else:
		return redirect('unauthorized')




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
		url = 'http://127.0.0.1:5000/authadmin/login'
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
			print(role)
			print(token)
		return redirect(url_for('mainadminhome', username=username, last_name=last_name, first_name=first_name))
	else:
		return render_template('login.html')





@app.route('/logout', methods=['POST', 'GET'])
def logout():
	if g.user:
		print(session['token'])
		url = 'http://127.0.0.1:5000/authadmin/logout'
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response = requests.request('POST', url, headers=headers)
		print(response.text)
		return redirect(url_for('index'))
	else:
		return redirect('unauthorized')


@app.route('/own/profile')
def ownprofile():
	if g.user:
		url1 = 'http://127.0.0.1:5000/user/admin/search/'+session['user']
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		# print(json_data["data"][0]["username"])
		url = 'http://127.0.0.1:5000/user/admin/'+json_data1["data"][0]["public_id"]
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data= response.json()
		# print(username)
		print(json_data)
		return render_template('profile-page.html', json_data=json_data)
	else:
		return redirect('unauthorized')



@app.route('/profile-page/<username>/<public_id>')
def viewprofile(username, public_id):
	if g.user:
		url = 'http://127.0.0.1:5000/user/admin/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(username)
		print(json_data)
		return render_template('profile-page.html', json_data=json_data)
	else:
		return redirect('unauthorized')





@app.route('/main-admin/home/<username>/<first_name>/<last_name>')
def mainadminhome(username, first_name, last_name):
	print(g.user)
	if g.user:
		return render_template('mainadmin-base.html', username=username, first_name=first_name, last_name=last_name)
	else:
		return redirect('unauthorized')


@app.route('/search/center', methods=['POST', 'GET'])
def search_center():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = 'http://127.0.0.1:5000/distcenter/search/'+keywords
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
			return 'Wala mumsh'

	else:
		return redirect('unauthorized')	


@app.route('/search/user', methods=['POST', 'GET'])
def search_user():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = 'http://127.0.0.1:5000/user/admin/search/'+keywords
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
			return 'Wala mumsh'

	else:
		return redirect('unauthorized')


@app.route('/view-user')
def viewuser():
	if g.user:
		url = 'http://127.0.0.1:5000/user/admin/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		# print(json_data['data'][0]['registered_on'])
		print(json_data)
		return render_template('view-user.html', json_data=json_data)
	else:
		return redirect('unauthorized')




@app.route('/add/user/admin', methods=['POST', 'GET'])
def add_user():	
	if g.user:
		if request.method == 'POST':
			email = request.form.get('email', '')
			first_name = request.form.get('first_name', '')
			last_name = request.form.get('last_name', '')
			role = request.form.get('role', '')
			username = request.form.get('username', '')
			# password = 'admin'
			gender = request.form.get('gender', '')
			print(role)
			print(gender)
			password_generator = generate_password()
			print(password_generator)
			password = password_generator
			url = 'http://127.0.0.1:5000/user/admin/'
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
			print(email)
			print(response.text)
			message = login_dict["message"]
			print(message)
			if message == "Email already used.":
				return redirect(url_for('add_user'))
			else:
				print(response)
				mat = password
				msg = Message(body="You have been registered on SanLigtas.\n Username:"+username+"\n Password: "+mat+"\n Welcome to the team!",
					sender="noreply@sanligtas.com",
					recipients=[email],
					subject="Welcome to San Ligtas")
				mail.send(msg)
			return redirect(url_for('viewuser'))
		else:
			return render_template('add-user.html')
	else:
		return redirect('unauthorized')



@app.route('/delete/user/<public_id>')
def delete_user(public_id):
	if g.user:
		print(session['token'])
		headers = { 'Authorization' : '{}'.format(session['token']) }
		public_id = public_id
		print(public_id)
		url = 'http://127.0.0.1:5000/user/admin/'+public_id
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')


@app.route('/change/password/<public_id>', methods=['POST', 'GET'])
def change_pass(public_id):
	if g.user:
		public_id = public_id
		if request.method == 'POST':
			old_pass = request.form.get('old_pass', '')		
			new_pass = request.form.get('new_pass', '')	

			url = 'http://127.0.0.1:5000/user/admin/'+public_id
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
				url2 = 'http://127.0.0.1:5000/user/admin/password/'+public_id
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
				return "Old password entered and old password did not matched."
		else:
			return render_template('change-password.html', public_id=public_id)

	else:
		return redirect('unauthorized')




@app.route('/update/user/<public_id>', methods=['POST', 'GET'])
def update_user(public_id):
	if g.user:
		url1 = 'http://127.0.0.1:5000/user/admin/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		print(json_data1['username'])

		
		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				username = request.form.get('username', '')
				email = request.form.get('email', '')
				first_name = request.form.get('first_name', '')
				last_name = request.form.get('last_name', '')
				role = request.form.get('role', '')
				gender = request.form.get('gender', '')

				public_id = public_id
				print(public_id)
				url = 'http://127.0.0.1:5000/user/admin/'+public_id
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
				print(response.text)

				return redirect(url_for('viewuser'))

			else:

				return redirect('unauthorized')

		else:

			return render_template('edit-user.html', username=json_data1['username'], email=json_data1['email'], public_id=json_data1['public_id'], first_name=json_data1['first_name'], last_name=json_data1['last_name'], role=json_data1['role'], gender=json_data1['gender'] )	

	else:
		return redirect('unauthorized')


@app.route('/view/center')
def view_center():
	if g.user:
		url = 'http://127.0.0.1:5000/distcenter/'
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




@app.route('/view/center/<name>/<public_id>')
def view_spec_center(name, public_id):
	if g.user:
		url = 'http://127.0.0.1:5000/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)
		address = json_data['address']

		print(json_data['latitude'])
		print(json_data['longitude'])


		return render_template('view-center.html', json_data=json_data)
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

				google_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyAayoLLtuuXjGtgaxIURWpfzRrGDZ1KgVc')
				google_dict = json.loads(google_response.text)
				print(google_dict)
				latitude=google_dict['results'][0]['geometry']['location']['lat']
				longitude=google_dict['results'][0]['geometry']['location']['lng']



				

				lat = str(latitude).encode('utf-16')
				long1 = str(longitude).encode('utf-16')


				url = 'http://127.0.0.1:5000/distcenter/'
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
		url1 = 'http://127.0.0.1:5000/distcenter/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		print(response1.text)
		center_dict = json.loads(response1.text)


		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				address = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				url = 'http://127.0.0.1:5000/distcenter/'+public_id
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
				print(response.text)

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
			print(public_id)
			url = 'http://127.0.0.1:5000/distcenter/'+public_id
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('view_center'))

		else:
			return "unauthorized ka gurl"
	else: 
		return render_template('unauthorized')



@app.route('/home')
def home():
	# api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=8f46c985e7b5f885798e9a5a68d9c036&q=Iligan'
	# json_data = requests.get(api_address).json()
	# city = json_data['name']
	# formatted_data = json_data['weather'][0]['description']
	# weather_icon = json_data['weather'][0]['icon']
	# temp = json_data['main']['temp']
	# final_temp = pytemperature.k2c(temp)
	# celcius = round(final_temp, 2)
	# print(city)
	# print(formatted_data)
	# print(weather_icon)
	# print(temp)
	# print(final_temp)
	# print(celcius)
	# return render_template('home.html', weather=formatted_data, weather_icon=weather_icon, celcius=celcius, city=city)
	return render_template('home.html')



if __name__=='__main__':
    app.run(debug=True, port=8080)	