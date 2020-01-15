from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

barangay_bp = Blueprint('barangay', __name__)

@barangay_bp.route('/view-list/')
def view_barangay():
	if g.user:
		url = api_url+'/barangay/get/'
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

@barangay_bp.route('/add', methods=['POST', 'GET'])
def add_barangay():	
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin':
				name = request.form.get('name', '')
				url = api_url+'/barangay/add/'
				files = {
					'Name' : (None, name)
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

@barangay_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_barangay(public_id):
	if g.user:
		url1 = api_url+'/barangay/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				name = request.form.get('name', '')

				url = api_url+'/barangay/'+public_id+'/update'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
					'Name' : (None, name)
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

@barangay_bp.route('/<public_id>/delete')
def delete_barangay(public_id):
	if g.user:
		headers = { 'Authorization' : '{}'.format(session['token']) }
		url = api_url+'/barangay/'+public_id+'/delete'
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')
		