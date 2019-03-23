import pymongo
from bson.objectid import ObjectId
from celery import Celery
from celery import Task


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

class T1(Task):
    def __init__(self):
        self._x = 8

@scheduler.task(base=MongoTask)
def add_user(email, pwd, first_name, last_name, licence_plate):
    data = {'email': email, 'pwd': pwd, 'first_name': first_name,
            'last_name': last_name, 'licence_plate': licence_plate}
    return str(add_user._client.insert_one(data).inserted_id)

@scheduler.task(base=MongoTask)
def delete_user(_id):
    data = {'_id': ObjectId(_id)}
    delet_user._client.delete_one(data)

    return True

@scheduler.task(base=MongoTask)
def add_parking(location, num_spots):
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
    data = {'email': email, 'pwd': pwd}
    cursor  = authentificate_user._client.find(data)
    entries = list(cursor)
    if len(entries) == 1:
        entries[0].pop('pwd')
        return entries[0]
    else:
        return False

@scheduler.task(base=MongoTask)
def get_parkings():
    return list(get_parkings._parking.find())

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
    count_clients = reserve_parking._client.count_documents(data)
    if count_clients != 1:
        return {'error': 'Not a valid user'}

    data_parking = {'_id': ObjectId(parking_id)}
    count_parkings = reserve_parking._parking.count_documents(data)
    if count_parkings != 1:
        return {'error': 'Not a valid parking spot'}

    free_parking._client.update_one(data_user, {'$unset':
            {'parking_id': '', 'type': ''}})

    free_parking._parking.update_one(data_parking,
            {'$inc': {'available_spots': 1}})

    return True

