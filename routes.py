from flask import Flask, render_template
import requests
import pytemperature


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secretkey'



@app.route('/')
def home():
	api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=8f46c985e7b5f885798e9a5a68d9c036&q=Iligan'
	json_data = requests.get(api_address).json()
	city = json_data['name']
	formatted_data = json_data['weather'][0]['description']
	weather_icon = json_data['weather'][0]['icon']
	temp = json_data['main']['temp']
	final_temp = pytemperature.k2c(temp)
	celcius = round(final_temp, 2)
	print(city)
	print(formatted_data)
	print(weather_icon)
	print(temp)
	print(final_temp)
	print(celcius)
	return render_template('home.html', weather=formatted_data, weather_icon=weather_icon, celcius=celcius, city=city)
	# return render_template('home.html')



if __name__=='__main__':
    app.run(debug=True)	