from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

center_bp = Blueprint('center', __name__)

@center_bp.route('/view')
def view_center():
	if g.user:
		url = api_url+'/distcenter/'
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

@center_bp.route('/<public_id>/assign', methods=['POST', 'GET'])
def assign_admin(public_id):
	if g.user:
		url1 = api_url+'/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		latitude = json_data1["latitude"]
		longitude = json_data1["longitude"]


		if request.method == 'POST':
			center_public_id = public_id
			center_admin = request.form.get('center_admin', '')

			url2 = api_url+'/user/admin/search/'+center_admin
			response2 = requests.request('GET', url2, headers=headers)
			json_data2 = response2.json()
			print(json_data2)

			role = json_data2["data"][0]["role"]

			if role == "Social Worker Admin" or role == "Main Admin":
				files = {					
					'center_public_id': (None, center_public_id),
					'center_admin': (None, center_admin)
				}
				headers = {
					'Authorization': '{}'.format(session['token'])
				}
				url = api_url+'/distcenter/assign/admin/'+public_id
				response = requests.request('POST', url, files=files, headers=headers)
				json_data = response.json()
				print(json_data)
				message = json_data["message"]

				if message == "admin assigned successfully":
					return redirect(url_for('view_spec_center', public_id=public_id, name=name ))
				else:
					return "Dili pwede dzaii"
			else:
				return "Dili pwede kay dili Social Worker"
		else:
			return render_template('assign_admin.html', name=name, public_id=public_id, latitude=latitude, longitude=longitude)
	else:
		return redirect(url_for('unauthorized'))

@center_bp.route('/<public_id>/register-evac', methods=['POST', 'GET'])
def assign_evacuee(public_id):
	if g.user:
		url1 = api_url+'/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		latitude = json_data1["latitude"]
		longitude = json_data1["longitude"]

		if request.method == "POST":
			if session['role'] == "Main Admin" or session['role'] == "Social Worker Admin":
				name = request.form.get('name', '')

				url1 = api_url+'/evacuees/search/'+name
				headers = {
						'Authorization': '{}'.format(session['token'])
					}
				response1 = requests.request('GET', url1, headers=headers)
				json_data1 = response1.json()
				homeid = json_data1["data"][0]["home_id"]

				url2 = api_url+'/distcenter/search/'+public_id
				response2 = requests.request('GET', url2, headers=headers)
				json_data2 = response2.json()
				centerid = json_data2["data"][0]["id"]

				files = {
					'home_id' : (None, homeid),
					'center_id' : (None, centerid)
				}
				url3 = api_url+'/evacuees/assign/evacuee'
				response3 = requests.request('PUT', url3, headers=headers, files=files,  )
				json_data3 = response3.json()

				return redirect(url_for('view_spec_center', public_id=public_id, name=name))
			else: 
				return "Dili ka Main Admin dzaii"
		else:
			return render_template('assign-evacuee.html', public_id=public_id, name=name, latitude=latitude, longitude=longitude)
	else:
		return redirect('unauthorized')


@center_bp.route('/view/<public_id>')
def view_spec_center(public_id):
	if g.user:
		url = api_url+'/distcenter/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		center_id = json_data["id"]
		print(center_id)
		
		url1 = api_url+'/distcenter/assign/admin/'+public_id
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		address = json_data['address']

		url2 = api_url+'/evacuees/get/center/'+center_id
		response2 = requests.request('GET', url2, headers=headers)
		json_data2 = response2.json()
		print(json_data2)

		url3 = api_url+'/reliefupdates/get/'+public_id
		response3 = requests.request('GET', url3, headers=headers)
		json_data3 = response3.json()

		return render_template('view-center.html', json_data=json_data, json_data1=json_data1, json_data2=json_data2, json_data3=json_data3)
	else:
		return redirect('unauthorized')


@center_bp.route('/add', methods=['POST', 'GET'])
def add_center():
	if g.user:
		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				address = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				#google_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyAayoLLtuuXjGtgaxIURWpfzRrGDZ1KgVc')
				#google_dict = json.loads(google_response.text)#
				#latitude=google_dict['results'][0]['geometry']['location']['lat']
				#longitude=google_dict['results'][0]['geometry']['location']['lng']
				#lat = str(latitude).encode('utf-16')
				#long1 = str(longitude).encode('utf-16')

				url = api_url+'/distcenter/'
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}	
				files = {
				
					'name': (None, name),
					'address': (None, address),
					'capacity': (None, capacity)
				}

				response = requests.request('POST', url, files=files, headers=headers)
				distcenter_dict = json.loads(response.text)
				print(response.text)
				message = distcenter_dict["message"]
				print(message)
				if message == "Name already used.":
					return redirect(url_for('add_center'))
				else:
					print(response)
				return redirect(url_for('view_center'))
			else: 
				return "unauthorized lage ka"
		else:
			return render_template('add-evac.html')
	else:
		return redirect('unauthorized')




@center_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_center(public_id):
	if g.user:
		url1 = api_url+'/distcenter/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		center_dict = json.loads(response1.text)

		if request.method == 'POST':

			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				name = request.form.get('name', '')
				address = request.form.get('address', '')
				capacity = request.form.get('capacity', '')

				url = api_url+'/distcenter/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				files = {
					'name' : (None, name),
					'address' : (None, address),
					'capacity' : (None, capacity)
				}
				response = requests.request('PUT', url, headers=headers, files=files)
				del_dict = json.loads(response.text)

				return redirect(url_for('view_center'))
			else:
				return redirect('unauthorized')
		else:
			return render_template('edit-evacs.html', name=center_dict['name'], address=center_dict['address'], public_id=center_dict['public_id'], capacity=center_dict['capacity'])
	else:
		return redirect('unauthorized')

@center_bp.route('/<public_id>/delete')
def delete_evac(public_id):
	if g.user:
		if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':

			headers = { 'Authorization' : '{}'.format(session['token']) }
			public_id = public_id
			url = api_url+'/distcenter/'+public_id
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('view_center'))
		else:
			return "unauthorized ka gurl"
	else: 
		return render_template('unauthorized')