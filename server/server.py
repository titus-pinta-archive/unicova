from os import environ

from flask import Flask, request
from flask_socketio import SocketIO

import json

from  ... import db
from db import mongo

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def view():
    with open('main.html') as f:
        return f.read()

if __name__ == '__main__':
    socketio.run()
