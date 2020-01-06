from flask import Blueprint, render_template, session, g
from flask import current_app as app
api_url = app.config['API_URL']

goods_bp = Blueprint('relief', __name__)

@goods_bp.route('/updates')
#@app.route(/goods_db)
def relief_updates():
	if g.user:
		url = api_url+'/reliefupdates/'
		headers = {
			'Authorization' : '{}'.format(session['token'])
		}
		response = requests.request('GET', url, headers=headers)
		json_data = response.json()
		print(json_data)


		return render_template('relief-updates.html', json_data=json_data)
	else:
		return redirect(url_for('unauthorized'))

@goods_bp.route('/<public_id>/add', methods=['POST', 'GET'])
#@app.route(/goods_db/public_id/add)
def add_relief(public_id):
	if g.user:	
		if request.method == 'POST':
			if session['role'] == 'Main Admin' or session['role'] == 'Relief Admin':
				number_goods = request.form.get('number_goods', '')
				center_public_id = public_id
				center = name

				url = api_url+'/reliefupdates/'
				files = {
					'center' : (None, center),
					'center_public_id' : (None, center_public_id),
					'number_goods' : (None, number_goods)
				}
				headers = { 'Authorization' : '{}'.format(session['token']) }
				response = requests.request('POST', url, files=files, headers=headers)
				json_data = response.json()
				print(json_data)

				return redirect(url_for('view_spec_center', name=name, public_id=public_id))
			else:
				return redirect(url_for('unauthorized'))
		else:
			return render_template('add-relief.html', name=name, public_id=public_id)

	else:
		return redirect(url_for('unauthorized'))