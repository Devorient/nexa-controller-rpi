from flask import render_template, request, session, flash, redirect
from json import load
from time import sleep
from app import app, switcher

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

@app.route('/switch')
def switch():
  with open('controller_db.json', 'r') as db_file:
    db = load(db_file)
    devices = db['devices']
  if 'id' in request.args and 'switch' in request.args:
    switcher.switch(devices[request.args.get('id')]['code'],
                    request.args.get('switch') == 'on')
  return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  elif 'password' in request.form and request.form['password'] == app.config['PASSWORD']:
    session['logged_in'] = True
    return redirect('/')
  else:
    sleep(1)
    return render_template('login.html', error=True)