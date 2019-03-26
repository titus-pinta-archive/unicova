import pymongo
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from bson.objectid import ObjectId
from celery import Celery
from celery import Task
from celery.five import monotonic
from contextlib import contextmanager
import memcache


import datetime
import hashlib
import json
import re

email_re = re.compile('^[a-zA-Z0-9\.]*@[a-zA-Z]*\.[a-z]*$')
pwd_re = re.compile('^[a-zA-Z0-9]*$')
name_re = re.compile('^[a-zA-Z]*$')
licence_re = re.compile('^[A-Z]{2}[0-9]{2}[A-Z]{3}$')
location_re = re.compile('^[a-zA-Z0-9\.\- ]*$')
id_re = re.compile('^[a-zA-Z0-9]*$')

scheduler = Celery('mongo', backend='rpc://',
                   broker='pyamqp://guest@{}//'.format('127.0.0.1'))

cache = memcache.Client([('127.0.0.1', 11211)])

LOCK_EXPIRE = 30

@contextmanager
def memcached_lock(lock_id, tid):
    timeout_at = monotonic() + LOCK_EXPIRE + 3
    status = cache.add(lock_id, tid, LOCK_EXPIRE)

    yield status

    if monotonic() < timeout_at and status:
        cache.delete(lock_id)



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

@scheduler.task(base=MongoTask, bind=True)
def add_user(self, email, pwd, first_name, last_name, licence_plate,
             task_id=None):
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

    with memcached_lock('e{}'.format(hashlib.md5(email.encode('ascii')
                        ).hexdigest()), task_id) as acquired:
        if acquired:

            count_clients = self._client.count_documents(data)
            if count_clients != 0:
                return {'error': 'Email already used'}

            salt = hashlib.sha512(str(datetime.datetime.now()).encode(
                'ascii')).hexdigest()
            pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

            data = {'email': email, 'pwd': pwd, 'salt': salt, 'first_name':
                    first_name, 'last_name': last_name, 'licence_plate':
                    licence_plate}
            return str(self._client.insert_one(data).inserted_id)

        return self.retry(countdown=2)


@scheduler.task(base=MongoTask, bind=True)
def delete_user(self, _id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    count_clients = self._client.count_documents(data)
    if count_clients != 1:
        return {'error': 'No user with this id'}
    self._client.delete_one(data)

    return True


@scheduler.task(base=MongoTask, bind=True)
def add_admin(self, email, pwd, first_name, last_name, task_id=None):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}
    if not isinstance(first_name, str) or not bool(name_re.match(first_name)):
        return {'error': 'Wrong format for first name: {}'.format(first_name)}
    if not isinstance(last_name, str) or not bool(name_re.match(last_name)):
        return {'error': 'Wrong format for last name: {}'.format(last_name)}

    data = {'email': email}

    with memcached_lock('e{}'.format(hashlib.md5(email.encode('ascii')
                        ).hexdigest()), task_id) as acquired:
        if acquired:

            count_clients = self._client.count_documents(data)
            if count_clients != 0:
                return {'error': 'Email already used'}

            salt = hashlib.sha512(str(datetime.datetime.now()).encode(
                'ascii')).hexdigest()
            pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

            data = {'email': email, 'pwd': pwd, 'salt': salt, 'first_name':
                    first_name, 'last_name': last_name, 'admin': True}
            return str(self._client.insert_one(data).inserted_id)

        return self.retry(countdown=2)


@scheduler.task(base=MongoTask, bind=True)
def delete_admin(self, _id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    count_admins = self._client.count_documents(data)
    if count_admins != 1:
        return {'error': 'No admin with this id'}
    self._client.delete_one(data)

    return True


@scheduler.task(base=MongoTask, bind=True)
def add_parking(self, location, num_spots, task_id=None):
    if not isinstance(location, str) or not bool(location_re.match(location)):
        return {'error': 'Wrong format for location: {}'.format(location)}
    if not isinstance(num_spots, int) or num_spots <= 0:
        return {'error': ('Number of parking spots must be a' +
                          ' positive integer: {}').format(num_spots)}

    data = {'location': location}

    with memcached_lock('l{}'.format(hashlib.md5(location.encode('ascii')
                        ).hexdigest()), task_id) as acquired:
        if acquired:

            count_parkings = self._parking.count_documents(data)
            if count_parkings != 0:
                return {'error': 'Parking already exists'}

            data = {'location': location, 'num_spots': num_spots,
                    'available_spots': num_spots}
            return str(self._parking.insert_one(data).inserted_id)

        return self.retry(countdown=2)


@scheduler.task(base=MongoTask, bind=True)
def delete_parking(self, _id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    count_parkings = self._parking.count_documents(data)
    if count_parkings != 1:
        return {'error': 'No parking with this id'}
    self._parking.delete_one(data)

    return True


@scheduler.task(base=MongoTask, bind=True)
def get_user(self, _id):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}
    data = {'_id': ObjectId(_id)}
    cursor  = self._client.find(data)
    entries = list(cursor)

    if len(entries) != 1:
        return {'error': 'Invalid user id: {}'.format(_id)}

    entries[0].pop('pwd')
    entries[0].pop('salt')
    if 'parking_id' in entries[0].keys():
        entries[0]['parking_id'] = str(entries[0]['parking_id'])
    entries[0]['_id'] = str(entries[0]['_id'])

    return json.dumps(entries[0])


@scheduler.task(base=MongoTask, bind=True)
def authentificate_user(self, email, pwd):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}

    data = {'email': email, 'admin': {'$exists': False}}
    cursor  = self._client.find(data)
    entries = list(cursor)

    if len(entries) != 1:
        return {'error': 'Email and password do not match'}

    salt = entries[0]['salt']
    pwd = hashlib.sha512((pwd + salt).encode('ascii')).hexdigest()

    if pwd != entries[0]['pwd']:
        return {'error': 'Email and password do not match'}

    entries[0].pop('pwd')
    entries[0].pop('salt')
    if 'parking_id' in entries[0].keys():
        entries[0]['parking_id'] = str(entries[0]['parking_id'])
    entries[0]['_id'] = str(entries[0]['_id'])

    return json.dumps(entries[0])


@scheduler.task(base=MongoTask, bind=True)
def authentificate_admin(self, email, pwd):
    if not isinstance(email, str) or not bool(email_re.match(email)):
        return {'error': 'Wrong format for email: {}'.format(email)}
    if not isinstance(pwd, str) or not bool(pwd_re.match(pwd)):
        return {'error': 'Wrong format for password: {}'.format(pwd)}

    data = {'email': email, 'admin': True}
    cursor  = self._client.find(data)
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

    return json.dumps(entries[0])


@scheduler.task(base=MongoTask, bind=True)
def get_parkings(self):
    result = list(self._parking.find())
    for element in result:
        element['_id'] = str(element['_id'])
    return json.dumps(result)


@scheduler.task(base=MongoTask, bind=True)
def reserve_parking(self, user_id, parking_id, _type, task_id=None):
    if not isinstance(user_id, str) or not bool(id_re.match(user_id)):
        return {'error': 'Invalid user id: {}'.format(user_id)}
    if not isinstance(parking_id, str ) or not bool(id_re.match(parking_id)):
        return {'error': 'Invalid parking id: {}'.format(parking_id)}
    if not _type in ['normal', 'fast']:
        return {'error': 'Invalid type: {}'.format(_type)}


    with self._connection.start_session({'readPreference':
                        {'mode': 'primary'}}) as session:

        with session.start_transaction(ReadConcern(level='snapshot'),
                                       WriteConcern(w='majority')):

            with memcached_lock('p{}'.format(parking_id),
                                task_id) as acquired_user:
                with memcached_lock('u{}'.format(user_id),
                                    task_id) as acquired_parking:

                    if acquired_user and acquired_parking:

                        data = {'_id': ObjectId(user_id)}
                        count_clients = self._client.count_documents(data)
                        if count_clients != 1:
                            return {'error': 'Not a valid user'}


                        data = {'_id': ObjectId(user_id), '$or':
                                [{'parking_id': {'$exists': True,
                                '$ne': None}}, {'admin': True}]}

                        count_clients = self._client.count_documents(data)
                        if count_clients != 0:
                            return {'error': 'Already reserved a parking spot'}

                        data = {'_id': ObjectId(parking_id),
                                'available_spots': {'$gt': 0}}

                        count_parkings = self._parking.count_documents(data)
                        if count_parkings != 1:
                            return {'error': 'No available parking spots'}

                        times = self._info.find_one({'times': {'$exists':
                                                True, '$ne': None}})['times']

                        if _type not in times.keys():
                            return {'error': 'Invalid parking type'}

                        data = {'_id': ObjectId(user_id)}
                        self._client.update_one(data, {'$set':
                                {'parking_id': ObjectId(parking_id),
                                 'type': _type}})

                        data = {'_id': ObjectId(parking_id)}
                        self._parking.update_one(data, {'$inc':
                                        {'available_spots': -1}})

                        session.commit_transaction()
                        return times[_type]

                return self.retry(countdown=2)

    return {'error': 'Unknown backend error'}

@scheduler.task(base=MongoTask, bind=True)
def free_parking(self, user_id, parking_id, task_id=None):
    if not isinstance(user_id, str) or not bool(id_re.match(user_id)):
        return {'error': 'Invalid user id: {}'.format(user_id)}
    if not isinstance(parking_id, str) or not bool(id_re.match(parking_id)):
        return {'error': 'Invalid parking id: {}'.format(parking_id)}

    with self._connection.start_session({'readPreference':
                        {'mode': 'primary'}}) as session:

        with session.start_transaction(ReadConcern(level='snapshot'),
                                       WriteConcern(w='majority')):

            with memcached_lock('p{}'.format(parking_id),
                                task_id) as acquired_user:
                with memcached_lock('u{}'.format(user_id),
                                    task_id) as acquired_parking:

                    if acquired_user and acquired_parking:

                        data_user = {'_id': ObjectId(user_id), 'admin':
                                     {'$exists': False}, 'parking_id':
                                     ObjectId(parking_id)}

                        count_clients = self._client.count_documents(data_user)
                        if count_clients != 1:
                            return {'error': 'Not a valid user'}

                        data_parking = {'_id': ObjectId(parking_id)}
                        count_parkings = self._parking.count_documents(
                            data_parking)

                        if count_parkings != 1:
                            return {'error': 'Not a valid parking spot'}

                        self._client.update_one(data_user, {'$unset':
                                {'parking_id': '', 'type': ''}})

                        self._parking.update_one(data_parking,
                                {'$inc': {'available_spots': 1}})

                        return True

                    return self.retry(countdown=2)

    return {'error': 'Unknown backend error'}


@scheduler.task(base=MongoTask, bind=True)
def block_spot(self, _id, task_id=None):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}

    data = {'_id': ObjectId(_id), 'available_spots': {'$gt': 0}}

    with memcached_lock('p{}'.format(_id), task_id) as acquired:
        if acquired:
            count_parkings = self._parking.count_documents(data)

            if count_parkings != 1:
                return {'error': 'No parcking with this id and ' +
                        'available parking spots'}
            self._parking.update_one(data, {'$inc': {'available_spots': -1,
                                            'blocked_spots': 1}})

            return True
        return self.retry(countdown=2)


@scheduler.task(base=MongoTask, bind=True)
def free_spot(self, _id, task_id=None):
    if not isinstance(_id, str) or not bool(id_re.match(_id)):
        return {'error': 'Invalid id: {}'.format(_id)}

    data = {'_id': ObjectId(_id), 'blocked_spots': {'$gt': 0}}

    with memcached_lock('p{}'.format(_id), task_id) as acquired:
        if acquired:
            coursor = self._parking.find(data)
            entries = list(coursor)
            if len(entries) != 1 or entries[0]['available_spots'] >=\
               entries[0]['num_spots']:

                return {'error': 'No parcking with this id and ' +
                        'free parking spots'}

            if entries[0]['blocked_spots'] == 1:
                update_data = {'$unset': {'blocked_spots': ''}, '$inc':
                               {'available_spots': 1}}
            else:
                update_data = {'$inc': {'available_spots': 1,
                                        'blocked_spots': -1}}

            self._parking.update_one(data, update_data)
            return True
        return self.retry(countdown=2)

