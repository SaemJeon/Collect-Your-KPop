''' Saem Jeon, sj846@drexel.edu
CS530: GUI, Project '''

from flask import Flask, render_template, send_file, jsonify, request, g, redirect, session
from passlib.hash import pbkdf2_sha256
import json
import os
from db import Database
from uszipcode import Zipcode

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = Database()
	return db


@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

# Handle the index (home) page
@app.route('/')
def index():
	return render_template('index.html')

# Handle Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	msg = None
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		if email and password:
			user = get_db().get_user(email)
			if user:
				if pbkdf2_sha256.verify(password, user['encrypted_password']):
					session['user'] = user
					return redirect('/my_collection')
				else:
					msg = "Email or password you entered is incorrect."
		else:
			msg = "Email or password you entered is incorrect."
	return render_template('login.html', message=msg)

# Log out functionality
@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')

# Handle Create an Account page
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
	msg = None
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		dob = request.form['dob']
		artist = request.form['artist']
		member = request.form['member']
		if name and email and password and dob and artist and member:
			if get_db().get_user(email):
				msg = "Account with the provided email already exists"
			else:
				encrypted_password = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
				get_db().create_account(name, email, encrypted_password, dob, artist, member)
				return redirect('/login')
		else:
			msg = "Please enter all the information"
	return render_template('create_account.html', message=msg)

# Handle Edit My Pop page
@app.route('/edit_my_pop', methods=['GET', 'POST'])
def edit_my_pop():
	if request.method == 'POST':
		artist = request.form['artist']
		member = request.form['member']
		city = request.form['city']
		state = request.form['state']
		zipcode = request.form['zipcode']
		distance = request.form['distance']
		language = request.form['language']
		user = session['user']
		if artist and member and city and state and zipcode and language:
			get_db().update_profile(artist, member, city, state, zipcode, distance, language, user['user_id'])
			return redirect('my_collection')
	return render_template('edit_my_pop.html')

# Handle My Collection page
@app.route('/my_collection')
def my_collection():
	return render_template('my_collection.html')

# Handle Buy page
@app.route('/buy')
def buy():
	return render_template('buy.html')

# Handle Sell page
@app.route('/sell')
def sell():
	return render_template('sell.html')

# Handle any files that begin "/course" by loading from the course directory
@app.route('/course/<path:path>')
def base_static(path):
	return send_file(os.path.join(app.root_path, '..', 'course', path))

# # Handle any unhandled filename by loading its template
@app.route('/<name>')
def generic(name):
	return render_template(name + '.html')

# Any additional handlers that go beyond simply loading a template
# (e.g., a handler that needs to pass data to a template) can be added here
# Function to return content from data.txt
@app.route('/api/data')
def api_data():
	with open('data.txt', 'r') as f:
		content = f.read()
		# Add braceks to make it a list
		content = "[" + content + "]"
		# Convert string to list
		data = {"content": eval(content)}
	return data

@app.route('/api/get_user_profile')
def api_profile():
	user = session['user']
	profile = get_db().get_profile(user['user_id'])
	return profile

@app.route('/api/get_groups')
def api_groups():
	groups = get_db().get_groups()
	return groups

@app.route('/api/get_members/<int:group_id>')
def api_members(group_id):
	members = get_db().get_members(group_id)
	return members

@app.route('/api/get_my_pop')
def api_my_pop():
	user = session['user']
	pop = get_db().get_my_pop(user['user_id'])
	print(pop)
	return pop

if __name__ == "__main__":
	app.run(host='127.0.0.1', port=8080, debug=True)
