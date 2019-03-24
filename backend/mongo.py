import pymongo
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from bson.objectid import ObjectId
from celery import Celery
from celery import Task

import datetime
import hashlib
import re

email_re = re.compile('^[a-zA-Z0-9\.]*@[a-zA-Z]*\.[a-z]*$')
pwd_re = re.compile('^[a-zA-Z0-9]*$')
name_re = re.compile('^[a-zA-Z]*$')
licence_re = re.compile('^[A-Z]{2}[0-9]{2}[A-Z]{3}$')
location_re = re.compile('^[a-zA-Z0-9\.\- ]*$')
id_re = re.compile('^[a-zA-Z0-9]*$')

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
        try:
            self._connection.close()
        except:
            pass

@scheduler.task(base=MongoTask)
def add_user(email, pwd, first_name, last_name, licence_plate):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}
    if not isinstance(first_name, str) or not bool(name_re.match(first_name)):
        return {'error': 'Wrong format for first name: {}'.format(first_name)}
    if not isinstance(last_name, str) or not bool(name_re.match(last_name)):
        return {'error': 'Wrong format for last name: {}'.format(last_name)}
    if not isinstance(licence_plate, str) or not bool(
        licence_re.match(licence_plate)):
        return {'error': 'Wrong format for licence plate: {}'.format(
            licence_plate)}

    data = {'email': email}
    count_clients = add_user._client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Email already used'}

    salt = hashlib.sha512(str(datetime.datetime.now()).encode(
        'ascii')).hexdigest()
    pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

    data = {'email': email, 'pwd': pwd, 'salt': salt, 'first_name': first_name,
            'last_name': last_name, 'licence_plate': licence_plate}
    return str(add_user._client.insert_one(data).inserted_id)


@scheduler.task(base=MongoTask)
def delete_user(_id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    count_clients = delete_user._client.count_documents(data)
    if count_clients != 1:
        return {'error': 'No user with this id'}
    delete_user._client.delete_one(data)

    return True


@scheduler.task(base=MongoTask)
def add_admin(email, pwd, first_name, last_name):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}
    if not isinstance(first_name, str) or not bool(name_re.match(first_name)):
        return {'error': 'Wrong format for first name: {}'.format(first_name)}
    if not isinstance(last_name, str) or not bool(name_re.match(last_name)):
        return {'error': 'Wrong format for last name: {}'.format(last_name)}

    data = {'email': email}
    count_clients = add_admin._client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Email already used'}

    salt = hashlib.sha512(str(datetime.datetime.now()).encode(
        'ascii')).hexdigest()
    pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

    data = {'email': email, 'pwd': pwd, 'salt': salt, 'first_name': first_name,
            'last_name': last_name, 'admin': True}
    return str(add_user._client.insert_one(data).inserted_id)


@scheduler.task(base=MongoTask)
def delete_admin(_id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    count_admins = delete_admin._client.count_documents(data)
    if count_admins != 1:
        return {'error': 'No admin with this id'}
    delete_admin._client.delete_one(data)

    return True


@scheduler.task(base=MongoTask)
def add_parking(location, num_spots):
    if not isinstance(location, str) or not bool(location_re.match(location)):
        return {'error': 'Wrong format for location: {}'.format(location)}
    if not isinstance(num_spots, int) or num_spots <= 0:
        return {'error': ('Number of parking spots must be a' +
                          ' positive integer: {}').format(num_spots)}

    data = {'location': location}
    count_parkings = add_parking._parking.count_documents(data)
    if count_parkings != 0:
        return {'error': 'Parking already exists'}

    data = {'location': location, 'num_spots': num_spots,
            'available_spots': num_spots}
    return str(add_parking._parking.insert_one(data).inserted_id)


@scheduler.task(base=MongoTask)
def delete_parking(_id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    count_parkings = delete_parking._parking.count_documents(data)
    if count_parkings != 1:
        return {'error': 'No parking with this id'}
    delete_parking._parking.delete_one(data)

    return True


@scheduler.task(base=MongoTask)
def get_user(_id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    cursor  = get_user._client.find(data)
    entries = list(cursor)

    if len(entries) != 1:
        return {'error': 'Invalid user id: {}'.format(_id)}

    entries[0].pop('pwd')
    entries[0].pop('salt')
    entries[0]['_id'] = str(entries[0]['_id'])

    return repr(entries[0])


@scheduler.task(base=MongoTask)
def authentificate_user(email, pwd):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}

    data = {'email': email, 'admin': {'$exists': False}}
    cursor  = authentificate_user._client.find(data)
    entries = list(cursor)

    if len(entries) != 1:
        return {'error': 'Email and password do not match'}

    salt = entries[0]['salt']
    pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

    if pwd != entries[0]['pwd']:
        return {'error': 'Email and password do not match'}

    entries[0].pop('pwd')
    entries[0].pop('salt')
    entries[0]['_id'] = str(entries[0]['_id'])

    return repr(entries[0])


@scheduler.task(base=MongoTask)
def authentificate_admin(email, pwd):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}

    data = {'email': email, 'admin': True}
    cursor  = authentificate_admin._client.find(data)
    entries = list(cursor)

    if len(entries) != 1:
        return {'error': 'Email and password do not match'}

    salt = entries[0]['salt']
    pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

    if pwd != entries[0]['pwd']:
        return {'error': 'Email and password do not match'}

    entries[0].pop('pwd')
    entries[0].pop('salt')
    entries[0]['_id'] = str(entries[0]['_id'])

    return repr(entries[0])


@scheduler.task(base=MongoTask)
def get_parkings():
    result = list(get_parkings._parking.find())
    for element in result:
        element['_id'] = str(element['_id'])
    return repr(result)


@scheduler.task(base=MongoTask)
def reserve_parking(user_id, parking_id, _type):
    if not isinstance(user_id, str) or not bool(id_re.match(user_id)):
        return {'error': 'Invalid user id: {}'.format(user_id)}
    if not isinstance(parking_id, str ) or not bool(id_re.match(parking_id)):
        return {'error': 'Invalid parking id: {}'.format(parking_id)}
    if not _type in ['normal', 'fast']:
        return {'error': 'Invalid type: {}'.format(_type)}


    with reserve_parking._connection.start_session({'readPreference':
                        {'mode': 'primary'}}) as session:

        session.start_transaction(ReadConcern(level='snapshot'),
                                 WriteConcern(w='majority'))

        data = {'_id': ObjectId(user_id)}
        count_clients = reserve_parking._client.count_documents(data)
        if count_clients != 1:
            return {'error': 'Not a valid user'}


        data = {'_id': ObjectId(user_id), '$or': [{'parking_id':
                    {'$exists': True, '$ne': None}}, {'admin': True}]}

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

        session.commit_transaction()
        return times[_type]

    return {'error': 'Unknown backend error'}


@scheduler.task(base=MongoTask)
def free_parking(user_id, parking_id):
    if not isinstance(user_id, str) or not bool(id_re.match(user_id)):
        return {'error': 'Invalid user id: {}'.format(user_id)}
    if not isinstance(parking_id, str) or not bool(id_re.match(parking_id)):
        return {'error': 'Invalid parking id: {}'.format(parking_id)}

    with reserve_parking._connection.start_session({'readPreference':
                        {'mode': 'primary'}}) as session:

        session.start_transaction(ReadConcern(level='snapshot'),
                                 WriteConcern(w='majority'))
        data_user = {'_id': ObjectId(user_id), 'admin': {'$exists': False},
                     'parking_id': ObjectId(parking_id)}
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

        session.commit_transaction()
        return True

    return {'error': 'Unknown backend error'}


@scheduler.task(base=MongoTask)
def block_spot(_id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id), 'available_spots': {'$gt': 0}}
    count_parkings = block_spot._parking.count_documents(data)
    if count_parkings != 1:
        return {'error': 'No parcking with this id and ' +
                'available parking spots'}
    block_spot._parking.update_one(data, {'$inc': {'available_spots': -1}})
    return True

