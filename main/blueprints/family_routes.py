from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

family_bp = Blueprint('family', __name__)

@family_bp.route('/view-list/')
def view_family():
	if g.user:
		url = api_url+'/family/get/'
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

@family_bp.route('/add', methods=['POST', 'GET'])
def add_family():	
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin':
				family_name = request.form.get('family_name', '')

				url = api_url+'/family/add/'
				files = {
					'FamilyName' : (None, family_name)
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

@family_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_family(public_id):
	if g.user:
		url1 = api_url+'/family/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				family_name = request.form.get('family_name', '')

				url = api_url+'/family/'+public_id+'/update'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
					'FamilyName' : (None, family_name)
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

@family_bp.route('/<public_id>/delete')
def delete_family(public_id):
	if g.user:
		headers = { 'Authorization' : '{}'.format(session['token']) }
		url = api_url+'/family/'+public_id+'/delete'
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')
		