import os
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe

socketio = SocketIO()

@failsafe
def create_app(debug=False):
	app = Flask(__name__)

	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.debug = debug
	app.secret_key = 'redacted'
	# ----------------------------------------------

	from .utils.database.database import database
	db = database()
	db.createTables(purge=True)

	db.createUser(email='redacted' ,password='redacted', role='owner')
	db.createUser(email='redacted' ,password='redacted', role='guest')
	# ----------------------------------------------

	socketio.init_app(app)

	with app.app_context():
		from . import routes
		return app
