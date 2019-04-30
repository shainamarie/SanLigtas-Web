from flask import Flask, render_template, request, redirect, url_for, session, g
import dateutil.parser
import requests, json
import pytemperature
import string
from random import *


# from blueprints.AdminSignUp import createuser, updateuser, deleteData


app = Flask(__name__, template_folder="templates")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'zxcvbnm'


def api_login(autho, username, last_name, first_name):
	session['user'] = username
	session['token'] = autho
	session['first_name'] = first_name 
	session['last_name'] = last_name
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
			autho = login_dict["Authorization"]
			first_name = login_dict["first_name"]
			last_name = login_dict["last_name"]
			username = login_dict["username"]
			token = api_login(autho, username, last_name, first_name)
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




@app.route('/main-admin/home/<username>/<first_name>/<last_name>')
def mainadminhome(username, first_name, last_name):
	print(g.user)
	if g.user:
		return render_template('mainadmin-base.html', username=username, first_name=first_name, last_name=last_name)
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




# @app.route('/update/user/<public_id>')
# def update_user(public_id):
# 	if g.user:
# 		if request.method == 'POST':
# 			email = request.form.get('email', '')
# 			username = request.form.get('username', '')
# 			password = request.form.get('password', '')
# 			first_name = request.form.get('first_name', '')
# 			last_name = request.form.get('last_name', '')
# 			gender = request.form.get('gender', '')
# 			role = request.form.get('role', '')

# 			print(session['token'])
# 			headers = { 
# 				'Authorization' : '{}'.format(session['token']) 
# 			}
# 			public_id = public_id
# 			print(public_id)
# 			url = 'http://127.0.0.1:5000/user/admin/'+public_id
# 			files = {
# 				'email' : (None, email),
# 				'username' : (None, username),
# 				'password' : (None, password),
# 				'first_name' : (None, first_name),
# 				'last_name' : (None, last_name),
# 				'role' : (None, role),
# 				'gender': (None, gender)

# 			}
# 			response = requests.request('PUT', url, headers=headers, files=files)
# 			del_dict = json.loads(response.text)
# 			print(response.text)

# 			return redirect(url_for('viewuser'))
# 		else:
# 			# return render_template('add-user.html')
# 			return render_template('edit-user.html', username=username, email=email, public_id=public_id, first_name=first_name, last_name=last_name, role=role)
# 	else:
# 		return redirect('unauthorized')


@app.route('/update/user/<public_id>', methods=['POST', 'GET'])
def update_user(public_id):
	if g.user:
		if request.method != 'POST':
			url1 = 'http://127.0.0.1:5000/user/admin/'+public_id
			headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
			response1 = requests.request('GET', url1, headers=headers)
			print(url1)
			print(response1.text)
			user_dict = json.loads(response1.text)

			return render_template('edit-user.html', username=user_dict['username'], email=user_dict['email'], public_id=user_dict['public_id'], first_name=user_dict['first_name'], last_name=user_dict['last_name'], role=user_dict['role'], gender=user_dict['gender'])



		if request.method == 'POST':
			username = request.form.get('username', '')
			email = request.form.get('email', '')
			first_name = request.form.get('first_name', '')
			last_name = request.form.get('last_name', '')
			role = request.form.get('role', '')
			gender = request.form.get('gender', '')

			print(session['token'])
			
			public_id = public_id
			print(public_id)
			url3 = 'http://127.0.0.1:5000/user/admin/'+public_id
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
			response = requests.request('PUT', url3, headers=headers, data=payload)
			# print(url2)
			del_dict = json.loads(response.text)
			print(response.text)

			return redirect(url_for('viewuser'))
		else:
			return render_template('edit-user.html', username=username, email=email, public_id=public_id, first_name=first_name, last_name=last_name, role=role, gender=gender)
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
		
		return render_template('view-evac.html', json_data=json_data)
	else:
		return redirect('unauthorized')



@app.route('/add/center', methods=['POST', 'GET'])
def add_center():
	if g.user:
		if request.method == 'POST':
			name = request.form.get('name', '')
			address = request.form.get('address', '')
			capacity = request.form.get('capacity', '')
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
			return render_template('add-evac.html')
	else:
		return redirect('unauthorized')




@app.route('/update/center/<public_id>', methods=['POST', 'GET'])
def update_center(public_id):
	if g.user:
		if request.method != 'POST':
			url1 = 'http://127.0.0.1:5000/distcenter/'+public_id
			headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
			response1 = requests.request('GET', url1, headers=headers)
			print(response1.text)
			center_dict = json.loads(response1.text)

			return render_template('edit-evacs.html', name=center_dict['name'], address=center_dict['address'], public_id=center_dict['public_id'], capacity=center_dict['capacity'])



		if request.method == 'POST':
			name = request.form.get('name', '')
			address = request.form.get('address', '')
			capacity = request.form.get('capacity', '')

			print(session['token'])
			
			public_id = public_id
			print(public_id)
			url2 = 'http://127.0.0.1:5000/distcenter/'+public_id
			headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
			files = {
				'name' : (None, name),
				'address' : (None, address),
				'capacity' : (None, capacity)
			}
			response = requests.request('PUT', url2, headers=headers, files=files)
			del_dict = json.loads(response.text)
			print(response.text)

			return redirect(url_for('view_center'))
		else:
			return render_template('edit-evacs.html', name=name, address=address, public_id=public_id, capacity=capacity)
	else:
		return redirect('unauthorized')




@app.route('/delete/center/<public_id>')
def delete_evac(public_id):
	if g.user:
		print(session['token'])
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