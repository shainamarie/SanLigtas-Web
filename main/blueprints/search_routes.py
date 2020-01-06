from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']
search_bp = Blueprint('search', __name__)

@search_bp.route('/center', methods=['POST'])
def search_center():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/distcenter/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)

			if json_data == {'data': []}:
				return render_template('no-center-result.html')
			else:
				return render_template('center-result.html', json_data=json_data)
	else:
		return redirect('unauthorized')	

@search_bp.route('/user', methods=['POST'])
def search_user():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/user/admin/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)
			if json_data == {'data': []}:
				return render_template('no-user-result.html')
			else:
				return render_template('user-result.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@search_bp.route('/evacuee', methods=['POST'])
#params == eg. ?searchby=public_id/name&params
def search_evacuee():
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/evacuees/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)
			if json_data == {'data': []}:
				return render_template('no-user-result.html')
			else:
				return render_template('evacuee-result.html', json_data=json_data, name=name, public_id=public_id)
	else:
		return redirect('unauthorized')

@search_bp.route('/admin', methods=['POST'])
#params == eg. ?searchby=public_id/name&params
def search_admin(name, public_id):
	if g.user:
		if request.method == 'POST':
			keywords = request.form.get('keyword', '')

			url = api_url+'/user/admin/search/'+keywords
			print(url)
			headers = {
				'Authorization' : '{}'.format(session['token'])
			}
			response = requests.request('GET', url, headers=headers)
			json_data = response.json()
			print(json_data)
			if json_data == {'data': []}:
				return render_template('no-user-result.html')
			else:
				return render_template('admin-result.html', json_data=json_data, name=name, public_id=public_id)
	else:
		return redirect('unauthorized')