from flask import Blueprint, render_template, session, g, request, redirect, url_for
from flask import current_app as app
import requests, json
api_url = app.config['API_URL']

center_bp = Blueprint('center', __name__)

@center_bp.route('/view')
def view_center():
	if g.user:
		url = api_url+'/center/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)

		if json_data == {'data': []}:
			return render_template('no-center-result.html')
		else:
			return render_template('view-evac.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@center_bp.route('/view/<public_id>')
def view_spec_center(public_id):
	if g.user:
		url = api_url+'/center/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()

		return render_template('view-center.html', json_data=json_data)
	else:
		return redirect('unauthorized')


@center_bp.route('/add', methods=['POST', 'GET'])
def add_center():
	if g.user:
		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				barangay_id = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				#google_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyAayoLLtuuXjGtgaxIURWpfzRrGDZ1KgVc')
				#google_dict = json.loads(google_response.text)#
				#latitude=google_dict['results'][0]['geometry']['location']['lat']
				#longitude=google_dict['results'][0]['geometry']['location']['lng']
				#lat = str(latitude).encode('utf-16')
				#long1 = str(longitude).encode('utf-16')

				url = api_url+'/center/'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}	
				files = {
				
					'Name': (None, name),
					'BarangayId': (None, barangay_id),
					'Capacity': (None, capacity)
				}

				response = requests.request('POST', url, files=files, headers=headers)
				center_dict = json.loads(response.text)

				return redirect(url_for('center.view_center'))
			else: 
				return "Unauthorized Page"
		else:
			return render_template('add-evac.html')
	else:
		return redirect('unauthorized')


@center_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_center(public_id):
	if g.user:
		url1 = api_url+'/center/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		center_dict = json.loads(response1.text)

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				barangay_id = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				url = api_url+'/center/'+public_id+'/update/'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				files = {
				
					'Name': (None, name),
					'BarangayId': (None, barangay_id),
					'Capacity': (None, capacity)
				}
				response = requests.request('PUT', url, headers=headers, files=files)
				del_dict = json.loads(response.text)

				return redirect(url_for('view_center'), center=center_dict)
			else:
				return redirect('unauthorized')
		else:
			return render_template('edit-evacs.html')
	else:
		return redirect('unauthorized')

@center_bp.route('/<public_id>/delete')
def delete_evac(public_id):
	if g.user:
		if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':

			headers = { 'Authorization' : '{}'.format(session['token']) }
			public_id = public_id
			url = api_url+'/center/'+public_id+'/delete/'
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('view_center'))
		else:
			return "Unauthorized Access"
	else: 
		return render_template('unauthorized')