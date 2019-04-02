from flask import Flask, render_template, request, redirect, url_for, session, g
import requests, json
import pytemperature


# from blueprints.AdminSignUp import createuser, updateuser, deleteData


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secretkey'


def api_login(autho):
    session['token'] = autho
    g.token = session['token'] 
    return session['token']



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




@app.route('/login', methods=['POST', 'GET'])
def loginprocess():
	if request.method == 'POST':
		# session.pop('user', None)
		email = request.form['email']
		password = request.form['password']
		files = {
			'email' : (None, email),
			'password' : (None, password),
		}
		response = requests.post('http://127.0.0.1:5000/auth/login', files=files)
		login_dict = json.loads(response.text)
		print(response.text)
		message = login_dict["message"]
		autho = login_dict["Authorization"]
		print(message)
		if message == "Login failed. Check email or password.":
			return render_template('login.html')
		else:
			token = api_login(autho)
		return redirect(url_for('mainadminhome'))
	else:
		return render_template('login.html')




@app.route('/logout', methods=['POST', 'GET'])
def logout():
	print(session['token'])
	headers = { 'Authorization' : '{}'.format(session['token']) }
	response = requests.post('http://127.0.0.1:5000/auth/logout', headers=headers)
	print(response.text)
	return redirect(url_for('index'))




@app.route('/main-admin/home')
def mainadminhome():
	return render_template('mainadmin-base.html')





@app.route('/view-user')
def viewuser():
	headers = { 'Authorization' : '{}'.format(session['token']) }
	response = requests.get('http://127.0.0.1:5000/user/', headers=headers)
	# print(response.text)
	json_data = response.json()
	print(json_data)
	email = json_data['data'][0]['email']

	print(email)
	# view_dict = json.loads(response.text)
	# email = view_dict[0]["email"]

	return render_template('view-user.html', json_data=json_data)





@app.route('/adduser', methods=['POST', 'GET'])
def add_user():	
	if request.method == 'POST':
		email = request.form.get('email', '')
		username = request.form.get('username', '')
		password = request.form.get('password', '')
		public_id = request.form.get('public_id', '')
		files = {
			'email' : (None, email),
			'username' : (None, username),
			'password' : (None, password),
			'public_id' : (None, public_id),
		}
		response = requests.post('http://127.0.0.1:5000/user/', files=files)
		login_dict = json.loads(response.text)
		print(email)
		print(password)
		print(public_id)
		print(response.text)
		message = login_dict["message"]
		print(message)
		if message == "Email already used.":
			return render_template('add-user.html')
		else:
			# token = api_login(email, password, response)
			print(response)
			# print(session['token'])
		return render_template('home.html')
	else:
		return render_template('mainadmin-base.html')

	return render_template('add-user.html')



@app.route('/add-user')
def adduser():
	return render_template('add-user.html')


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