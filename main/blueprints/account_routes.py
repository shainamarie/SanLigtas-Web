from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

account_bp = Blueprint('account', __name__)

def generate_password():
	characters = string.ascii_letters + string.punctuation + string.digits
	password = "".join(choice(characters) for x in range(randint(8, 16)))
	return password

@account_bp.route('/view-list/')
def view_account():
	if g.user:
		url = api_url+'/user/get/'
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

@account_bp.route('/add', methods=['POST', 'GET'])
def add_account():	
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin':
				username = request.form.get('username', '')
				role = request.form.get('role', '')
				isActive = True
				password_generator = generate_password()
				password = password_generator
				url = api_url+'/account/add/'
				files = {
					'Username' : (None, username),
					'Password' : (None, password),
					'RoleId' : (None, role),
					'IsActive' : (None, isActive)
				}
				response = requests.request('POST', url, files=files)
				login_dict = json.loads(response.text)

				return redirect(url_for('viewuser'))
			else:
				return redirect(url_for('unauthorized'))
		else:
			return render_template('add-user.html')
	else:
		return redirect(url_for('unauthorized'))

@account_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_account(public_id):
	if g.user:
		url1 = api_url+'/account/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				username = request.form.get('username', '')
				role = request.form.get('role', '')
				password = request.form.get('password', '')

				url = api_url+'/user/'+public_id+'/update'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
					'Username' : (None, username),
					'Password' : (None, password),
					'RoleId' : (None, role)
				}
				response = requests.request('PUT', url, headers=headers, data=payload)
				del_dict = json.loads(response.text)

				return redirect(url_for('viewuser'))
			else:
				return redirect('unauthorized')
		else:

			return render_template('edit-admin.html')	
	else:
		return redirect('unauthorized')

@account_bp.route('/<public_id>/delete')
def delete_account(public_id):
	if g.user:
		headers = { 'Authorization' : '{}'.format(session['token']) }
		url = api_url+'/account/'+public_id+'/delete'
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')
		