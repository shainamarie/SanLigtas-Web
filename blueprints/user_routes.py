from flask import Blueprint, render_template, session, g
from .. import app.config.['API_URL'] as api

user_bp = Blueprint('user', __name__)

@user_bp.route('/view/<public_id>')
def view_user():
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

@user_bp.route('/add', methods=['POST', 'GET'])
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
				}yt
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

@user_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_user(public_id):
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

@user_bp.route('/<public_id>/delete')
def delete_user(public_id):
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
		
@user_bp.route('/<public_id>/change_password', methods=['POST', 'GET'])
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