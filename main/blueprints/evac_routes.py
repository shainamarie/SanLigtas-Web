from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

evac_bp = Blueprint('evacuee', __name__)

@evac_bp.route('/')
def viewevacuees():
	if g.user:
		url = api_url+'/evacuees/'
		url2 = api_url+'/house/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		response2 = requests.request('GET', url2, headers=headers)
		json_data = response.json()
		json_data2 = response2.json()
		return render_template('view-evacuees.html', json_data=json_data, json_data2=json_data2)
	else:
		return redirect(url_for('unauthorized'))

@evac_bp.route('/add',methods=['POST', 'GET'])
def add_evacuee():
	if g.user:
		if request.method == 'POST':
			if session['role'] == 'Main Admin' or session['role'] == 'Social Worker Admin':
				n = 4
				name = request.form.get('name', '')
				home_id = ''.join(["%s" % randint(0, 9) for num in range(0, n)])
				address = request.form.get('address', '')
				gender = request.form.get('gender', '')
				age = request.form.get('age', '')
				religion = request.form.get('religion', '')
				civil_status = request.form.get('civil_status', '')
				educ_attainment = request.form.get('educ_attainment', '')
				occupation = request.form.get('occupation', '')

				url = api_url+'/evacuees/'
				files = {
					'name' : (None, name),
					'home_id' : (None, home_id),
					'address' : (None, address),
					'gender' : (None, gender),
					'age' : (None, age),
					'religion' : (None, religion),
					'civil_status' : (None, civil_status),
					'educ_attainment' : (None, educ_attainment),
					'occupation' : (None, occupation)
				}
				headers = { 'Authorization' : '{}'.format(session['token']) }
				response = requests.request('POST', url, files=files, headers=headers)
				json_data = response.json()

				return redirect(url_for('viewevacuees'))
			else:
				return redirect(url_for('unauthorized'))
		else:
			return render_template('add-evacuee.html')
	else:
		return redirect(url_for('unauthorized'))

@evac_bp.route('/<public_id>/update', methods=['POST', 'GET'])
def update_evacuee(public_id):
	if g.user:
		url1 = api_url+'/evacuees/'+public_id
		headers = { 
			'Authorization' : '{}'.format(session['token']) 
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()

		if request.method == 'POST':

			if session['role'] == 'Main Admin':

				name = request.form.get('name', '')
				gender = request.form.get('gender', '')
				age = request.form.get('age', '')
				religion = request.form.get('religion', '')
				civil_status = request.form.get('civil_status', '')
				educ_attainment = request.form.get('educ_attainment', '')
				occupation = request.form.get('occupation', '')

				url = api_url+'/evacuees/'+public_id
				headers = { 
					'Authorization' : '{}'.format(session['token']) 
				}
				payload = {	
					'name' : (None, name),
					'gender' : (None, gender),
					'age' : (None, age),
					'religion' : (None, religion),
					'civil_status' : (None, civil_status),
					'educ_attainment' : (None, educ_attainment),
					'occupation' : (None, occupation)
				}

				response = requests.request('PUT', url, headers=headers, data=payload)
				del_dict = json.loads(response.text)
				
				return redirect(url_for('viewevacuees'))
			else:
				return redirect('unauthorized')
		else:
			return render_template('edit-evacuee.html',	 name=json_data1['name'], religion=json_data1['religion'], age=json_data1['age'], public_id=json_data1['public_id'], civil_status=json_data1['civil_status'], educ_attainment=json_data1['educ_attainment'], occupation=json_data1['occupation'] )	
	else:
		return redirect('unauthorized')

@evac_bp.route('/<public_id>/delete')
def delete_evacuee(public_id):
	if g.user:
		print (session['role'])
		if session['role'] == 'Social Worker Admin' or session['role'] == 'Main Admin':
			print(session['token'])
			headers = { 'Authorization' : '{}'.format(session['token']) }
			
			url = api_url+'/evacuees/'+public_id
			files = {
					'public_id' : (None, public_id),
				}
			response = requests.request('DELETE', url, headers=headers, files=files)
		
			return redirect(url_for('viewevacuees'))
		else:
			return redirect(url_for('unauthorized'))
	else: 
		return render_template('unauthorized')