from flask import Blueprint, render_template, session, g, request, redirect, url_for
from flask import current_app as app
import requests, json

auth_bp = Blueprint('auth', __name__)
api_url = app.config['API_URL']

def api_login(autho, username, last_name, first_name, role):
	session['user'] = username
	session['token'] = autho
	session['first_name'] = first_name 
	session['last_name'] = last_name
	session['role'] = role
	g.token = session['token'] 
	g.user = session['user']
	return session['token']

@auth_bp.route('/', methods=['POST', 'GET'])
def index():
	#if logged out/ session['user'] = anonymous/none,
	return render_template('login.html')
	#else if logged in
	#return redirect(url_for(home)).

@auth_bp.route('/unauthorized')
def unauthorized():
	return render_template('unauthorized.html')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
	#if logged out/ session['user'] = anonymous/none,
	#continue below
	#else if logged in
	#return redirect(url_for(home)).
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
		return redirect(url_for('apple.mainadminhome'))
	else:
		return render_template('login.html')

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
	if g.user:
		print(session['token'])
		url = api_url+'/authadmin/logout'
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response = requests.request('POST', url, headers=headers)
		print(response.text)
		return redirect(url_for('auth.index'))
	else:
		return redirect('unauthorized')