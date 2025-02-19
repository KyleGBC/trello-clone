from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def membership_required(func):
	@functools.wraps(func)
	def inner(*args, **kwargs):
		if not db.is_board_member(db.reversibleEncrypt('decrypt', session['email']), kwargs['board_id']):
			return redirect('/home/')
		return func(*args, **kwargs)
	return inner
		
@app.context_processor
def getUser():
	return dict(user = db.reversibleEncrypt('decrypt', session['email']) if 'email' in session else 'Unknown')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/process_login', methods = ["POST"])
def process_login():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

	auth = db.authenticate(form_fields['email'], form_fields['password'])
	if auth['success'] == 1:
		session['email'] = db.reversibleEncrypt('encrypt', form_fields['email'])

	return json.dumps(auth)

@app.route('/process_signup', methods = ["POST"])
def process_signup():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

	user = db.createUser(form_fields['email'], form_fields['password'])
	if user['success'] == 1:
		session['email'] = db.reversibleEncrypt('encrypt', form_fields['email'])
	
	return json.dumps(user)

@app.route('/delete_board/<int:board_id>/', methods = ["POST"])
def delete_board(board_id):
	return json.dumps(db.deleteBoard(board_id, getUser()['user']))

	
#######################################################################################
# MAIN PAGES
#######################################################################################
@app.route('/')
def root():
	return redirect('/home/')

@app.route('/home/')
@login_required
def home():
	return render_template('home.html', boards=db.getUserBoards(getUser()['user']));

@app.route('/board/<int:board_id>/')
@login_required
@membership_required
def board(board_id):
	print("board_data", db.getBoard(board_id))
	return render_template('board.html', board_data=db.getBoard(board_id));

#######################################################################################
# SOCKET IO
#######################################################################################
@socketio.on('join')
def join(data):
	if 'room' in data:
		join_room(data['room'])
		emit('message', {'user': None, 'msg': getUser()['user'] + ' has entered the room.' }, broadcast=True, include_self=False, to=data['room'])
	else:
		join_room(getUser()['user'])
		

@socketio.on('message')
def message(data):
	data['user'] = getUser()['user'];
	emit('message', data, broadcast=True, include_self=False, to=data['room']);

@socketio.on('leave')
def leave(data):
	print('leave from', request.sid)
	emit('message', {'user': None, 'msg': getUser()['user'] + ' has left the room.' }, broadcast=True, include_self=False, to=data['room'])
	leave_room(data['room'])


@socketio.on('create_board')
def create_board(data):
	print('create_board from', request.sid)
	members_list = [m.strip(' ') for m in data['boardMembers'].split(',')]
	members_list = [] if members_list == [''] else members_list

	status = db.createBoard(data['boardName'], getUser()['user'], members_list)

	if status['success'] == 1:
		# Emit the board creation event to all members of the board
		creation_data = db.getBoard(status['board_id'])
		for member in members_list:
			emit('create_board', creation_data, broadcast=True, include_self=False, to=member)

	return status

@socketio.on('delete_board')
def delete_board(data):
	print('delete_board from', request.sid)
	users = db.getBoard(data['boardID'])['users']
	status = db.deleteBoard(data['boardID'], getUser()['user'])

	if status['success'] == 1:
		# Emit the board deletion event to all members of the board
		for user in users:
			emit('delete_board', data, broadcast=True, include_self=False, to=user['email'])

		# Emit the board deletion event to all members inside the board at the time of deletion
		emit('delete_board', data, broadcast=True, include_self=False, to=data['boardID'])

	return status

@socketio.on('refresh_board_stats')
def refresh_board_stats(data):
	data = db.getBoard(data['boardID'])

	print("refresh_board_stats from", request.sid)
	for user in data['users']:
		emit('refresh_board_stats', data, broadcast=True, include_self=False, to=user['email'])

@socketio.on('create_task')
def create_task(data):
	res = db.createTask(data['boardID'], "", "", data['listID'])
	data['taskID'] = res['task_id']

	print("create from", request.sid)
	emit('create_task', data, broadcast=True, include_self=False, to=data['room'])

	return res['task_id']

@socketio.on('edit_task')
def update_task(data):
	corrected_id = data['taskID'].lstrip('task-')
	db.updateTask(corrected_id, data['taskName'], data['taskDescription'])

	print("edit from", request.sid)
	emit('edit_task', data, broadcast=True, include_self=False, to=data['room'])

@socketio.on('move_task')
def move_task(data):
	corrected_id = data['taskID'].lstrip('task-')
	db.moveTask(corrected_id, new_status=data['destListID'], after_task_id=data['afterTaskID'])

	print("move from", request.sid)

	emit('move_task', data, broadcast=True, include_self=False, to=data['room'])


@socketio.on('delete_task')
def delete_task(data):
	corrected_id = data['taskID'].lstrip('task-')
	db.deleteTask(corrected_id)

	print("delete from", request.sid)
	emit('delete_task', data, broadcast=True, include_self=False, to=data['room'])

#######################################################################################
# OTHER
#######################################################################################
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
