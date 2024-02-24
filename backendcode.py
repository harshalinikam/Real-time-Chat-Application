from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

active_users = {}

@socketio.on('connect')
def on_connect():
    print('User connected:', request.sid)

@socketio.on('disconnect')
def on_disconnect():
    print('User disconnected:', request.sid)
    active_users.pop(request.sid, None)

@socketio.on('private_message')
def on_private_message(data):
    recipient_sid = data['recipient_sid']
    message = data['message']
    encrypted_message = cipher_suite.encrypt(message.encode())
    emit('private_message', {'sender_sid': request.sid, 'message': encrypted_message}, room=recipient_sid)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('join', {'user': active_users.get(request.sid), 'room': room}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('leave', {'user': active_users.get(request.sid), 'room': room}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
