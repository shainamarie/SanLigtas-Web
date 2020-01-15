from flask import Blueprint, render_template, session, g, request, redirect, url_for
from flask import current_app as app
import requests, json
from datetime import datetime
api_url = app.config['API_URL']

user_bp = Blueprint('user', __name__)

@user_bp.route('/view-list/')
def view_user():
	if g.user:
		url = api_url+'/user/'
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
				first_name = request.form.get('first_name', '')
				middle_name = request.form.get('middle_name', '')
				last_name = request.form.get('last_name', '')
				role = request.form.get('role', '')
				barangay = request.form.get('barangay', '')
				age = request.form.get('age', '')
				religion = request.form.get('religion', '')
				civil_status = request.form.get('civil_status', '')
				account_id = request.form.get('account_id', '')
				isActive = True
				register_date = datetime.now()
				gender = request.form.get('gender', '')
				url = api_url+'/user/'
				files = {
					'FirstName' : (None, first_name),
					'MiddleName' : (None, middle_name),
					'LastName' : (None, last_name),
					'BarangayId' : (None, barangay),
					'Age' : (None, age),
					'Religion' : (None, religion),
					'Gender' : (None, gender),
					'CivilStatus' : (None, civil_status),
					'DateRegistered' : (None, register_date),
					'AccountId' : (None, account_id),
					'IsActive' : (None, isActive),
					'RoleId' : (None, role)
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

@user_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_user(public_id):
	if g.user:
		url1 = api_url+'/user/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				first_name = request.form.get('first_name', '')
				middle_name = request.form.get('middle_name', '')
				last_name = request.form.get('last_name', '')
				role = request.form.get('role', '')
				barangay = request.form.get('barangay', '')
				age = request.form.get('age', '')
				religion = request.form.get('religion', '')
				civil_status = request.form.get('civil_status', '')
				account_id = request.form.get('account_id', '')
				gender = request.form.get('gender', '')

				url = api_url+'/user/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
					'FirstName' : (None, first_name),
					'MiddleName' : (None, middle_name),
					'LastName' : (None, last_name),
					'BarangayId' : (None, barangay),
					'Age' : (None, age),
					'Religion' : (None, religion),
					'Gender' : (None, gender),
					'CivilStatus' : (None, civil_status),
					'DateRegistered' : DateTime.now(),
					'AccountId' : (None, account_id),
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

@user_bp.route('/<public_id>/delete')
def delete_user(public_id):
	if g.user:
		headers = { 'Authorization' : '{}'.format(session['token']) }
		url = api_url+'/user/'+public_id
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')
		