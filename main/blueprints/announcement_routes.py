from flask import Blueprint, render_template, session, g
from flask import current_app as app
from datetime import datetime
api_url = app.config['API_URL']

announce_bp = Blueprint('announcement', __name__)

@announce_bp.route('/view-list/')
def view():
	if g.user:
		url = api_url+'/announcement/get/'
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

@announce_bp.route('/add', methods=['POST', 'GET'])
def add():	
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin':
				type_id = request.form.get('type_id', '')
				title = request.form.get('title', '')
				details = request.form.get('details', '')
				post_date = datetime.now()
				isActive = True
				url = api_url+'/announcement/add/'
				files = {
					'AnnouncementTypeId' : (None, type_id),
					'Title' : (None, title),
					'Details' : (None, desc),
					'PostDate' : (None, post_date),
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

@announce_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update(public_id):
	if g.user:
		url1 = api_url+'/announcement/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				type_id = request.form.get('type_id', '')
				title = request.form.get('title', '')
				details = request.form.get('details', '')

				url = api_url+'/announcement/'+public_id+'/update'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {
					'AnnouncementTypeId' : (None, type_id),
					'Title' : (None, title),
					'Details' : (None, desc)
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

@announce_bp.route('/<public_id>/delete')
def delete(public_id):
	if g.user:
		headers = { 'Authorization' : '{}'.format(session['token']) }
		url = api_url+'/announcement/'+public_id+'/delete'
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')
		
#announcement_type CRUDL

@announce_bp.route('/type/view-list/')
def view_type():
	if g.user:
		url = api_url+'/announcement-type/get/'
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

@announce_bp.route('/type/add', methods=['POST', 'GET'])
def add_type():	
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin':
				name = request.form.get('name', '')
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

@announce_bp.route('/type/<public_id>/update', methods=['POST', 'GET'])
def update_type(public_id):
	if g.user:
		url1 = api_url+'/announcement-type/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or json_data1['username'] == session['user']:

				name = request.form.get('name', '')

				url = api_url+'/announcement-type/'+public_id+'/update'
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

@announce_bp.route('/type/<public_id>/delete')
def delete_type(public_id):
	if g.user:
		headers = { 'Authorization' : '{}'.format(session['token']) }
		url = api_url+'/announcement-type/'+public_id+'/delete'
		files = {
				'public_id' : (None, public_id),
			}
		response = requests.request('DELETE', url, headers=headers, files=files)
	
		return redirect(url_for('viewuser'))
	else: 
		return render_template('unauthorized')
		