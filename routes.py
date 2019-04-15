from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_mail import Mail, Message
import dateutil.parser
import requests, json
import pytemperature
import string, random


# from blueprints.AdminSignUp import createuser, updateuser, deleteData
# install flask-login

app = Flask(__name__, template_folder="templates")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'zxcvbnm'

api_url = 'http://127.0.0.1:5000'

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '5379c5a04f264e'
app.config['MAIL_PASSWORD'] = '7896cd6b514abe'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

def api_login(autho, username, last_name, first_name):
	session['user'] = username
	session['token'] = autho
	session['first_name'] = first_name 
	session['last_name'] = last_name
	g.token = session['token'] 
	g.user = session['user']
	print(g.user)
	return session['token']

convert_to_role = {"Main Admin": 3, "Relief Admin": 2, "Social Worker Admin": 1, "No Permissions": 0}
convert_to_str_role = {3: "Main Admin", 2: "Relief Admin", 1: "Social Worker Admin", 0: "No Permissions"}


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
		url = api_url+'/auth/login'
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
			token = api_login(autho, 'username', 'last_name', 'first_name')
			print(token)
		return redirect(url_for('mainadminhome', username=username, last_name=last_name, first_name=first_name))
	else:
		return render_template('login.html')




@app.route('/logout', methods=['POST', 'GET'])
def logout():
	if g.user:
		print(session['token'])
		url = api_url+'/auth/logout'
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
		url = api_url+'/user/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)
		email = json_data['data'][0]['email']
		date1 = json_data['data'][0]['registered_on']
		return render_template('view-user.html', json_data=json_data, dict=convert_to_str_role)
	else:
		return redirect('unauthorized')




@app.route('/adduser', methods=['POST', 'GET'])
def add_user():	
	if g.user:
		if request.method == 'POST':
			email = request.form.get('email', '')
			first_name = request.form.get('first_name')
			last_name = request.form.get('last_name')
			admin_type = request.form.get('admin_type', '')
			username = request.form.get('username', '')
			password = passgen()
			url = api_url+'/user/'
			files = {
				'email' : (None, email),
				'username' : (None, username),
				'password' : (None, password),
				'role' : (None, admin_type),
				'first_name' : (None, first_name),
				'last_name' : (None, last_name)
			}
			response = requests.request('POST', url, files=files)
			login_dict = json.loads(response.text)
			print(email)
			print(password)
			print(response.text)
			message = login_dict["message"]
			print(message)
			if message == "Email already used.":
				return redirect(url_for('add_user'))
			else:
				print(response)
				mat=passgen()
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
def delete(public_id):
	if g.user:
		print(session['token'])
		headers = { 'Authorization' : '{}'.format(session['token']) }
		public_id = public_id
		print(public_id)
		url = api_url+'/user/'+public_id
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
		del_dict = json.loads(response.text)
		print(response.text)
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')




@app.route('/update/user/<public_id>')
def update(public_id):
	if g.user:
		get_url = api_url+'/user/'+public_id
		headers = { 'Authorization' : '{}'.format(session['token']) }
		use = requests.request('GET', url=get_url, headers=headers)

		json_data = use.json()
		email = json_data['data']['email']
		username = json_data['data']['username']
		first_name = json_data['data']['first_name']
		last_name = json_data['data']['last_name']
		admin_type = json_data['data']['role']
		if request.method == 'POST':
			email1 = request.form.get('email', '')
			username1 = request.form.get('username', '')
			password1 = request.form.get('password', '')
			first_name1 = request.form.get('first_name', '')
			last_name1 = request.form.get('last_name', '')
			admin_type1 = request.form.get('admin_type', '')

			print(session['token'])
			headers = { 
				'Authorization' : '{}'.format(session['token']) 
			}
			public_id = public_id
			print(public_id)
			url = api_url+'/user/'+public_id
			files = {
				'email' : (None, email1),
				'username' : (None, username1),
				'password' : (None, password1),
				'first_name' : (None, first_name1),
				'last_name' : (None, last_name1),
				'role' : (None, admin_type1),

			}
			response = requests.request('PUT', url, headers=headers, files=files)
			del_dict = json.loads(response.text)
			print(response.text)

			return redirect(url_for('viewuser'))
		else:
			# return render_template('add-user.html')
			return render_template('edit-user.html', username=username, email=email, first_name=first_name, last_name=last_name, admin_type=admin_type)
	else:
		return redirect('unauthorized')



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

def passgen():
	chars = string.ascii_letters + string.digits
	#chars = set of all english alphabet letters + 0-9 number characters
	return ''.join(random.choice(chars) for _ in range(8))
	#returns length 8 strings eg. ABCDEFG, 12345678, Secret01

if __name__=='__main__':
    app.run(debug=True, port=8080)	