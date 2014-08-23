# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, Response, make_response, json
from contextlib import closing
import re
from iwtba_back_end import *
from functools import wraps

# kvsession stuff
from flask import Flask
from flaskext.kvsession import KVSessionExtension
import redis
from simplekv.memory.redisstore import RedisStore

store = RedisStore(redis.StrictRedis()) # The process running Flask needs write access to this directory:
app = Flask(__name__)
KVSessionExtension(store, app) # this will replace the app's session handling


# configuration
DEBUG = True # keep True for debug mode
SECRET_KEY = 'asfjk2308hsdafkna020sakasdfa'


# create the application
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = DEBUG

@app.route('/')
def home():
    return render_template('home.html', job='none')

@app.route('/skills', methods=['POST'])
def skills():
    job = request.form['jobtitle']
    skills = get_skills(job)
    return render_template('show_skills.html', skills=skills, job=job)

@app.route('/about')
def about():
    return render_template('about.html')

#run server
if __name__ == '__main__':
	if DEBUG == False: # debug has to be off to see on other devices
		app.run(host='0.0.0.0') # to view from other computer visit 'your-local-ip:port'
	else: app.run()