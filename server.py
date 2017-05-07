#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat May  6 18:31:11 2017

@author: paul
"""

import os
from flask import *
import json
from flask_socketio import SocketIO
import time
import threading

encoder = json.JSONEncoder();
addr_serv = "192.168.43.19"
connected = False;
music_dir = './music'

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/api/ask_code', methods=['GET'])
def return_code():
    return json.dumps({"code" : "111222333444"}, separators=(',', ':'));

@app.route('/<filename>')
def song(filename):
    return render_template('play.html', title = filename, music_file = filename);

@app.route('/serv', methods=['POST'])
def cmd2app():
	connected = True; # a chager !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	if connected:
		print(request.data.decode("utf-8"))
		socketio.emit('order', {'value': request.data.decode("utf-8")})
	return "ok"

	
# @socketio.on('my event')
# def handle_my_custom_event(json):
	# connected = True;
	# print("Connected")
	# socketio.emit('order', {'data': 1})
	# threading.Timer(10, handle_my_custom_event).start()
	
@socketio.on('connect')
def test():
	connected = True;
	print("Connected")
	# socketio.emit('order', {'data': 1})
	# threading.Timer(10, handle_my_custom_event).start()
	
# def foo():
	# socketio.emit('order', {'data': 42})
	# time.sleep(5)
	# socketio.emit('order', {'data': 47})
	# threading.Timer(10, foo).start()

# envoie tout mais on peut se deplacer
@app.route('/music/<path:path>')
def send_js(path):
	return send_from_directory('music', path);
	
# envoie le fichier petit a petit mais pas possibilite de se deplacer :/
# @app.route("/wav")
# def streamwav():
	# def generate():
		# with open("music/f.mp3", "rb") as f:
			# data = f.read(1024)
			# while data:
				# yield data
				# data = f.read(1024)
	# return Response(generate(), mimetype="audio/mp3")
						
if __name__ == '__main__':
    socketio.run(app, host = addr_serv, debug = True)
	# app.run(host = addr_serv, debug = True);