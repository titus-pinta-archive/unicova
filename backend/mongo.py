import pymongo
from bson.objectid import ObjectId
from celery import Celery

connection = None
db = None
client = None
parking = None
info = None

scheduler = None

def connect_scheduler(ip='127.0.0.1'):
    global scheduler

    schedule = Celery('mongo', 'amqp://{}//'.format(ip))

@scheduler.task
def connect(ip='127.0.0.1', port=27017):
    global connection
    global db
    global client
    global parking
    global info

    global scheduler

    connection = pymongo.MongoClient(ip, port)
    db = connection['unicova']
    client = db['client']
    parking = db['parking']
    info = db['info']

@scheduler.task
def disconnect():
    connection.close()

@scheduler.task
def add_user(email, pwd, first_name, last_name, licence_plate):
    data = {'email': email, 'pwd': pwd, 'first_name': first_name,
            'last_name': last_name, 'licence_plate': licence_plate}
    return client.insert_one(data).inserted_id

@scheduler.task
def delete_user(_id):
    data = {'_id': ObjectId(_id)}
    client.delete_one(data)

@scheduler.task
def add_parking(location, num_spots):
    data = {'location': location, 'num_spots': num_spots,
            'available_spots': num_spots}
    return parking.insert_one(data).inserted_id

@scheduler.task
def delete_parking(_id):
    data = {'_id': ObjectId(_id)}
    parking.delete_one(data)

@scheduler.task
def authentificate_user(email, pwd):
    data = {'email': email, 'pwd': pwd}
    cursor  = client.find(data)
    entries = list(cursor)
    if len(entries) == 1:
        entries[0].pop('pwd')
        return entries[0]
    else:
        return False

@scheduler.task
def get_parkings():
    return list(parking.find())

@scheduler.task
def reserve_parking(user_id, parking_id, _type):
    data = {'_id': ObjectId(_id), 'park_id':
            {'$exists': True, '$ne': None}}

    count_clients = client.count_documents(data)
    if count_clients != 0:
        return {'error': 'Already reserved a parking spot'}

    data = {'_id': ObjectId(parking_id), 'available_spots': {'$gt': 0}}
    count_parkings = parking.count_documents(data)
    if count_parkings != 1:
        return {'error': 'No available parking spots'}

    times = info.find_one({'times':
                                {'$exists': True, '$ne': None}})['times']

    if _type not in times.keys():
        return {'error': 'Invalid parking type'}

    data = {'_id': ObjectId(_id)}
    client.update_one(data, {'$set':
            {'park_id': ObjectId(parking_id), 'type': _type}})

    data = {'_id': ObjectId(parking_id)}
    parking.update_one(data, {'$inc': {'available_spots': -1}})


    return True

@scheduler.task
def free_parking(user_id, parking_id):
    data = {'_id': ObjectId(_id)}
    client.update_one(data, {'$unset':
            {'park_id': '', 'type': ''}})

    data = {'_id': ObjectId(parking_id)}
    parking.update_one(data, {'$inc': {'available_spots': 1}})

    return True

connect_scheduler()
connect.delay()
_id = add_user.delay('Mihai', 'Mihai', 'Mihai', '', '')
delete_user.delay(_id)
