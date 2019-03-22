from flask import Flask, render_template, flash, redirect, url_for, session, request, logging,send_from_directory
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secretkey'


@app.route('/')
def home():
    return ('Hello world')



if __name__=='__main__':
    app.run(debug=True)