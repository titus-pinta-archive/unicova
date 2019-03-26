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

class MongoTask(Task):

    def __init__(self, ip='127.0.0.1', port=27017, user='Titus',
                 pwd='unicova'):
        self._connection = pymongo.MongoClient(ip, port)

        self._db = self._connection['unicova']
        self._db.authenticate(user, pwd)

        self._client = self._db['client']
        self._parking = self._db['parking']
        self._info = self._db['info']

    def __del__(self):
        self._connection.close()

@scheduler.task(base=MongoTask)
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
    count_clients = add_user._client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Email already used'}

    data = {'email': email, 'pwd': pwd, 'first_name': first_name,
            'last_name': last_name, 'licence_plate': licence_plate}
    return str(add_user._client.insert_one(data).inserted_id)

@scheduler.task(base=MongoTask)
def delete_user(_id):
    data = {'_id': ObjectId(_id)}
    delet_user._client.delete_one(data)

    return True

@scheduler.task(base=MongoTask)
def add_admin(email, pwd, first_name, last_name):
    if not bool(email_re.match(email)):
        return {'error': 'Wrong format for email'}
    if not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password'}
    if not bool(name_re.match(first_name)):
        return {'error': 'Wrong format for first name'}
    if not bool(name_re.match(last_name)):
        return {'error': 'Wrong format for last name'}

    data = {'email': email}
    count_clients = add_admin._client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Email already used'}

    data = {'email': email, 'pwd': pwd, 'first_name': first_name,
            'last_name': last_name, 'admin': True}
    return str(add_user._client.insert_one(data).inserted_id)

@scheduler.task(base=MongoTask)
def delete_admin(_id):
    data = {'_id': ObjectId(_id)}
    delete_admin._client.delete_one(data)

    return True

@scheduler.task(base=MongoTask)
def add_parking(location, num_spots):
    if not bool(location_re.match(location)):
        return {'error': 'Parking already exists'}
    if not isinstance(num_spots, int):
        return {'error': 'Number of parking spots must be an integer'}

    data = {'location': location}
    count_parkings = add_parking._parking.count_documents(data)
    if count_parkings != 0:
        return {'error': 'Parking already exists'}

    data = {'location': location, 'num_spots': num_spots,
            'available_spots': num_spots}
    return str(add_parking._parking.insert_one(data).inserted_id)

@scheduler.task(base=MongoTask)
def delete_parking(_id):
    data = {'_id': ObjectId(_id)}
    delete_parking._parking.delete_one(data)

    return True

@scheduler.task(base=MongoTask)
def authentificate_user(email, pwd):
    if not bool(email_re.match(email)):
        return {'error': 'Wrong format for email'}
    if not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password'}

    data = {'email': email, 'pwd': pwd, 'admin': {'$exists': False}}
    cursor  = authentificate_user._client.find(data)
    entries = list(cursor)
    if len(entries) == 1:
        entries[0].pop('pwd')
        return repr(entries[0])
    else:
        return False

@scheduler.task(base=MongoTask)
def authentificate_admin(email, pwd):
    if not bool(email_re.match(email)):
        return {'error': 'Wrong format for email'}
    if not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password'}

    data = {'email': email, 'pwd': pwd, 'admin': True}
    cursor  = authentificate_admin._client.find(data)
    entries = list(cursor)
    if len(entries) == 1:
        entries[0].pop('pwd')
        return repr(entries[0])
    else:
        return False

@scheduler.task(base=MongoTask)
def get_parkings():
    return repr(list(get_parkings._parking.find()))

@scheduler.task(base=MongoTask)
def reserve_parking(user_id, parking_id, _type):
    data = {'_id': ObjectId(user_id), 'parking_id':
            {'$exists': True, '$ne': None}}

    count_clients = reserve_parking._client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Already reserved a parking spot'}

    data = {'_id': ObjectId(parking_id), 'available_spots': {'$gt': 0}}
    count_parkings = reserve_parking._parking.count_documents(data)
    if count_parkings != 1:
        return {'error': 'No available parking spots'}

    times = reserve_parking._info.find_one({'times':
                                {'$exists': True, '$ne': None}})['times']

    if _type not in times.keys():
        return {'error': 'Invalid parking type'}

    data = {'_id': ObjectId(user_id)}
    reserve_parking._client.update_one(data, {'$set':
            {'parking_id': ObjectId(parking_id), 'type': _type}})

    data = {'_id': ObjectId(parking_id)}
    reserve_parking._parking.update_one(data,
                                       {'$inc': {'available_spots': -1}})

    return True, times[_type]

@scheduler.task(base=MongoTask)
def free_parking(user_id, parking_id):
    data_user = {'_id': ObjectId(user_id)}
    count_clients = reserve_parking._client.count_documents(data_user)
    if count_clients != 1:
        return {'error': 'Not a valid user'}

    data_parking = {'_id': ObjectId(parking_id)}
    count_parkings = reserve_parking._parking.count_documents(data_parking)
    if count_parkings != 1:
        return {'error': 'Not a valid parking spot'}

    free_parking._client.update_one(data_user, {'$unset':
            {'parking_id': '', 'type': ''}})

    free_parking._parking.update_one(data_parking,
            {'$inc': {'available_spots': 1}})

    return True

