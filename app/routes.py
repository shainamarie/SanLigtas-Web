from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secretkey'


@app.route('/')
def home():
    return ('Hello world')



if __name__=='__main__':
    app.run(debug=True)