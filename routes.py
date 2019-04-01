from flask import Flask, render_template, request, redirect, url_for
import requests
import pytemperature


# from blueprints.AdminSignUp import createuser, updateuser, deleteData


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secretkey'


@app.route('/', methods=['POST', 'GET'])
def landing():
	return render_template('login.html')



@app.route('/login', methods=['POST', 'GET'])
def loginprocess():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		response = requests.post('http://localhost:5000/auth/login', json={"email":email, "password":password}, )
		print(response.text)
		if response.text == "Login failed. Check email or password.":
			return render_template('error.html')
		else:
			# token = api_login(email, password, response)
			print(response)
			# print(session['token'])
		return render_template('mainadmin-base.html')
	else:
		return render_template('login.html')

	
	# return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
	response = requests.post('http://localhost:5000/auth/logout')
	print(response.text)
	return render_template('login.html')

@app.route('/main-admin/home')
def mainadminhome():
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
	# return render_template('mainadmin.html', weather=formatted_data, weather_icon=weather_icon, celcius=celcius, city=city)
	return render_template('mainadmin-base.html')


@app.route('/view-user')
def viewuser():

	return render_template('view-user.html')


@app.route('/add-user',  methods=['POST', 'GET'])
def adduser():
	# if request.method == 'POST':
 #        session.pop('user', None)
 #        username = request.form['username']
 #        password = request.form['password']
 #        response = requests.post(
 #            'http://localhost:5060/login',
 #            json={"username":username, "password":password},
 #        )
 #        print(response.text)
 #        if response.text == "Could not verify":
 #            return render_template('error.html')
 #        else:
 #            token = api_login(username, password, response)
 #        print(token)
 #        print(session['token'])
 #        return redirect(url_for('home'))
 #    else:
 #        return render_template('add-user.html')
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