import pymongo
from bson.objectid import ObjectId
from celery import Celery
from celery import Task

import re

email_re = re.compile('^[a-zA-Z0-9\.]*@[a-zA-Z]*\.[a-z]*$')
pwd_re = re.compile('^[a-zA-Z0-9]*$')
name_re = re.compile('^[a-zA-Z]*$')
licence_re = re.compile('^[A-Z]{2}[0-9]{2}[A-Z]{3}$')
location_re = re.compile('^[a-zA-Z0-9\ ]*$')

scheduler = Celery('mongo', backend='rpc://',
                   broker='pyamqp://guest@{}//'.format('127.0.0.1'))

_connection = None
_db = None
_client = None
_parking = None
_info = None

@scheduler.worker_process_init.connect
def connect(ip='127.0.0.1', port=27017, user='Titus',
             pwd='unicova'):
    _connection = pymongo.MongoClient(ip, port)

    _db = _connection['unicova']
    _db.authenticate(user, pwd)

    _client = _db['client']
    _parking = _db['parking']
    _info = _db['info']

@scheduler.worker_process_shutdown.connect
def disconnect(self):
    _connection.close()

@scheduler.task()
def add_user(email, pwd, first_name, last_name, licence_plate):
    if not bool(email_re.match(email)):
        return {'error': 'Wrong format for email'}
    if not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password'}
    if not bool(name_re.match(first_name)):
        return {'error': 'Wrong format for first name'}
    if not bool(name_re.match(last_name)):
        return {'error': 'Wrong format for last name'}
    if not bool(licence_re.match(licence_plate)):
        return {'error': 'Wrong format for licence plate'}

    data = {'email': email}
    count_clients = _client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Email already used'}

    data = {'email': email, 'pwd': pwd, 'first_name': first_name,
            'last_name': last_name, 'licence_plate': licence_plate}
    return str(_client.insert_one(data).inserted_id)

