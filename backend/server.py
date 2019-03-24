from os import environ

from flask import Flask, request
from flask_socketio import SocketIO

import json

import mongo

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def view():
    with open('main.html') as f:
        return f.read()

@socketio.on('authentificate')
def authentificate(email, pwd):
    print('Authentificatio from {} with email: {} and pwd: {}'.format(
            request.sid, email, pwd))
    result = mongo.authentificate_user.delay(email, pwd)
    data = result.get()
    socketio.emit('logged_on', data)

@socketio.on('register')
def register(email, pwd, first_name, last_name, licence_plate):
    print('esti prost in plm?')
    print(('Registered {} with email: {}, pwd: {}, licence_plate:' +
            '{} and name:{} {}').format(request.sid, email, pwd,
            licence_plate, first_name, last_name))
    result = mongo.add_user.delay(email, pwd, first_name,
                                  last_name, licence_plate)
    data = result.get()
    socketio.emit('signed_up', data)

@socketio.on('get_parkings')
def get_parkings():
    print('Get parkings from {}'.format(request.sid))
    result = mongo.get_parkings.delay()
    data = result.get()

@socketio.on('reserve_parking')
def reserve_parking(parking_id, _type):
    pass



if __name__ == '__main__':
    socketio.run()
