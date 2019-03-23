import mongo

user_id = mongo.add_user.delay('Mihai', 'Mihai', 'Mihai', 'Titus', 'Titus')
parking_id = mongo.add_parking.delay('Cluj', 10)
user_id = user_id.get()
parking_id = parking_id.get()

print(user_id)
print(parking_id)

result = mongo.reserve_parking.delay(user_id, parking_id, 'normal')

time = result.get()[1]
mongo.free_parking.apply_async([user_id, parking_id], countdown=time)

