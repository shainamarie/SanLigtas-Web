from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/<public_id>')
#@app.route('/profile/user_id')
def ownprofile():
	if g.user:
		url1 = api_url+'/user/admin/search/'+session['user']
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response1 = requests.request('GET', url1, headers=headers)
		json_data1 = response1.json()
		url = api_url+'/user/admin/'+json_data1["data"][0]["public_id"]
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data= response.json()
		return render_template('profile-page.html', json_data=json_data)
	else:
		return redirect('unauthorized')

@profile_bp.route('/<public_id>')
#@app.route('/profile/user_id')
def viewprofile_admin(public_id):
	if g.user:
		url = api_url+'/user/admin/'+public_id
		headers = {
			'Authorization': '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		return render_template('profile-admin.html', json_data=json_data)
	else:
		return redirect('unauthorized')



