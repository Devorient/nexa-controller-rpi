from flask import render_template, request, session, flash, redirect
from json import load
from time import sleep
from app import app, switcher, verify_password

@app.route('/')
def index():
  if not session.get('logged_in'):
    return redirect('/login')
  else:
    with open('controller_db.json', 'r') as db_file:
      db = load(db_file)
      devices = db['devices']
      rooms = db['rooms']
    return render_template('index.html', rooms=rooms, devices=devices)

@app.route('/switch', methods=['POST'])
def switch():
  if request.mimetype == 'application/json':
    data = request.get_json()
  if data and 'id' in data and 'switch' in data:
    with open('controller_db.json', 'r') as db_file:
      db = load(db_file)
      devices = db['devices']
    switcher.switch(devices[data['id']]['code'], data['switch'])
  return '', 200

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  elif 'password' in request.form and \
        verify_password(app.config['PASSWORD_HASH'], request.form['password']):
    session['logged_in'] = True
    return redirect('/')
  else:
    sleep(1)
    return render_template('login.html', error=True)