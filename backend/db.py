import pymongo
from bson.objectid import ObjectId

import schedule


class Mongo:

    def __init__(self, ip='127.0.0.1', port=27017):
        self.connection = pymongo.MongoClient(ip, port)
        db = self.connection['unicova']
        self.client = db['client']
        self.parking = db['parking']
        self.info = db['info']



    def __del__(self):
        self.connection.close()

    def add_user(self, email, pwd, first_name, last_name, licence_plate):
        data = {'email': email, 'pwd': pwd, 'first_name': first_name,
                'last_name': last_name, 'licence_plate': licence_plate}
        return self.client.insert_one(data).inserted_id

    def delete_user(self, _id):
        data = {'_id': ObjectId(_id)}
        self.client.delete_one(data)

    def add_parking(self, location, num_spots):
        data = {'location': location, 'num_spots': num_spots,
                'available_spots': num_spots}
        return self.parking.insert_one(data).inserted_id

    def delete_parking(self, _id):
        data = {'_id': ObjectId(_id)}
        self.parking.delete_one(data)

    def authentificate_user(self, email, pwd):
        data = {'email': email, 'pwd': pwd}
        cursor  = self.client.find(data)
        entries = list(cursor)
        if len(entries) == 1:
            entries[0].pop('pwd')
            return entries[0]
        else:
            return False

    def get_parkings(self):
        return list(self.parking.find())

    def reserve_parking(self, user_id, parking_id, _type):
        data = {'_id': ObjectId(_id), 'park_id':
                {'$exists': True, '$ne': None}}

        count_clients = self.client.count_documents(data)
        if count_clients != 0:
            return {'error': 'Already reserved a parking spot'}

        data = {'_id': ObjectId(parking_id), 'available_spots': {'$gt': 0}}
        count_parkings = self.parking.count_documents(data)
        if count_parkings != 1:
            return {'error': 'No available parking spots'}

        times = self.info.find_one({'times':
                                    {'$exists': True, '$ne': None}})['times']

        if _type not in times.keys():
            return {'error': 'Invalid parking type'}

        data = {'_id': ObjectId(_id)}
        self.client.update_one(data, {'$set':
                {'park_id': ObjectId(parking_id), 'type': _type}})

        data = {'_id': ObjectId(parking_id)}
        self.parking.update_one(data, {'$inc': {'available_spots': -1}})


        return True

    def free_parking(self, user_id, parking_id):
        data = {'_id': ObjectId(_id)}
        self.client.update_one(data, {'$unset':
                {'park_id': '', 'type': ''}})

        data = {'_id': ObjectId(parking_id)}
        self.parking.update_one(data, {'$inc': {'available_spots': 1}})

        return True

m = Mongo()
_id = m.add_user('Mihai', 'Mihai', 'Mihai', '', '')

_id_park = m.add_parking('Cluj', 1)

print(m.get_parkings())
print(m.authentificate_user('Mihai', 'Mihai'))

m.reserve_parking(_id, _id_park, 'normal')


print(m.get_parkings())
print(m.authentificate_user('Mihai', 'Mihai'))

m.free_parking(_id, _id_park)

print(m.get_parkings())
print(m.authentificate_user('Mihai', 'Mihai'))


m.delete_user(_id)
m.delete_parking(_id_park)
