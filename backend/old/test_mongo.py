import mongo
import re
import ast

from bson.objectid import ObjectId


def test_add_user():
    print('Tests for add user')
    id_re = re.compile('^[a-zA-Z0-9]*$')

    #Tests for user regitration
    test_index = 1
    total_tests = 6


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_user.delay('titus.pinta@gmail.com', 'unicova',
                                  'Titus', 'Pinta', 'BH12TIT')
    result = result.get()
    assert bool(id_re.match(result))
    user_id = result
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_user.delay('titus.pinta@gmail.com', 'unicova',
                                  'Titus', 'Pinta', 'BH12TIT')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Email already used'
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    email = 'titus.pintagmail.com'
    result = mongo.add_user.delay(email, 'unicova',
                                  'Titus', 'Pinta', 'BH12TIT')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for email: {}'.format(email)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    email = 'tituspint@agmailcom'
    result = mongo.add_user.delay(email, 'unicova',
                                  'Titus', 'Pinta', 'BH12TIT')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for email: {}'.format(email)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    licence_plate = 'bh12wek'
    result = mongo.add_user.delay('titus.pinta@gmail.com', 'unicova',
                                  'Titus', 'Pinta', licence_plate)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for licence plate: {}'.format(
        licence_plate)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    licence_plate = 'BH199AAA'
    result = mongo.add_user.delay('titus.pinta@gmail.com', 'unicova',
                                  'Titus', 'Pinta', licence_plate)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for licence plate: {}'.format(
        licence_plate)
    test_index += 1

    print('All tests for add user have passed')
    return user_id


def test_delete_user(user_id):
    print('Tests for delete user')
    #Tests for user delete
    test_index = 1
    total_tests = 3


    print('Test {} of {}'.format(test_index, total_tests))
    aux_user_id ='sdjfbgjuey7834hf2i3jceo2ce2f/fe4v84cds'
    result = mongo.delete_user.delay(aux_user_id)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Invalid id: {}'.format(aux_user_id)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.delete_user.delay(user_id)
    result = result.get()
    assert result == True
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.delete_user.delay(user_id)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'No user with this id'
    test_index += 1

    print('All test for delete user have passed')


def test_add_admin():
    print('Tests for add admin')
    id_re = re.compile('^[a-zA-Z0-9]*$')

    #Tests for admin regitration
    test_index = 1
    total_tests = 4


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_admin.delay('titus.pinta@yahoo.com', 'unicova',
                                  'Titus', 'Pinta')
    result = result.get()
    assert bool(id_re.match(result))
    user_id = result
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_admin.delay('titus.pinta@yahoo.com', 'unicova',
                                  'Titus', 'Pinta')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Email already used'
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    email = 'titus.pintagmail.com'
    result = mongo.add_admin.delay(email, 'unicova', 'Titus', 'Pinta')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for email: {}'.format(email)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    email = 'tituspint@agmailcom'
    result = mongo.add_admin.delay(email, 'unicova', 'Titus', 'Pinta')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for email: {}'.format(email)
    test_index += 1


    print('All tests for add admin have passed')
    return user_id


def test_delete_admin(admin_id):
    print('Tests for delete admin')
    #Tests for admin delete
    test_index = 1
    total_tests = 3


    print('Test {} of {}'.format(test_index, total_tests))
    aux_admin_id ='sdjfbgjuey7834hf2i3jceo2ce2f/fe4v84cds'
    result = mongo.delete_admin.delay(aux_admin_id)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Invalid id: {}'.format(aux_admin_id)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.delete_admin.delay(admin_id)
    result = result.get()
    assert result == True
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.delete_admin.delay(admin_id)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'No admin with this id'
    test_index += 1

    print('All test for delete admin have passed')


def test_add_parking():
    print('Tests for add parking')
    #Tests for add parking
    id_re = re.compile('^[a-zA-Z0-9]*$')
    test_index = 1
    total_tests = 5


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_parking.delay('Cluj n. 1', 1)
    result = result.get()
    parking_id = result
    assert bool(id_re.match(result))
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_parking.delay('Cluj n. 1', 127)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Parking already exists'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_parking.delay('Cluj n. 1', 0)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert 'Number of parking spots must be a positive' in result['error']
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    location = 'Cluj n? 1'
    result = mongo.add_parking.delay(location, 127)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Wrong format for location: {}'.format(location)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_parking.delay('Cluj n 1', '127')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert 'Number of parking spots must be a positive ' in result['error']
    test_index += 1

    print('All tests for add parking have passed')
    return parking_id


def test_delete_parking(parking_id):
    print('Tests for delete parking')
    #Tests for admin delete
    test_index = 1
    total_tests = 3


    print('Test {} of {}'.format(test_index, total_tests))
    aux_parking_id ='sdjfbgjuey7834hf2i3jceo2ce2f/fe4v84cds'
    result = mongo.delete_parking.delay(aux_parking_id)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'Invalid id: {}'.format(aux_parking_id)
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.delete_parking.delay(parking_id)
    result = result.get()
    assert result == True
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.delete_parking.delay(parking_id)
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert len(result.keys()) == 1
    assert result['error'] == 'No parking with this id'
    test_index += 1

    print('All test for delete parking have passed')


def test_get_user(user_id, admin_id):
    #Tests for authentificate user
    print('Tests for get user')
    test_index = 1
    total_tests = 2

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.get_user.delay(user_id)
    result = result.get()
    try:
        result = ast.literal_eval(result)
    except ValueError as e:
        raise AssertionError(e)

    assert isinstance(result, dict)
    assert 'email' in result.keys()
    assert not 'pwd' in result.keys()
    assert not 'salt' in result.keys()
    assert result['email'] == 'titus.pinta@gmail.com'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.get_user.delay(admin_id)
    result = result.get()
    try:
        result = ast.literal_eval(result)
    except ValueError as e:
        raise AssertionError(e)

    assert isinstance(result, dict)
    assert 'email' in result.keys()
    assert not 'pwd' in result.keys()
    assert not 'salt' in result.keys()
    assert result['email'] == 'titus.pinta@yahoo.com'
    test_index += 1

    print('All tests for get user have passed')


def test_authentificate_user():
    #Tests for authentificate user
    print('Tests for authentificate user')
    test_index = 1
    total_tests = 3

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_user.delay('titus.pinta@gmail.com',
                                            'unicova')
    result = result.get()
    try:
        result = ast.literal_eval(result)
    except ValueError as e:
        raise AssertionError(e)

    assert isinstance(result, dict)
    assert 'email' in result.keys()
    assert not 'pwd' in result.keys()
    assert not 'salt' in result.keys()
    assert result['email'] == 'titus.pinta@gmail.com'
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_user.delay('titu.pinta@gmail.com',
                                            'unicova')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Email and password do not match'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_user.delay('titus.pinta@gmail.com',
                                            'unicov')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Email and password do not match'
    test_index += 1


def test_authentificate_admin():
    #Tests for authentificate admin
    print('Tests for authentificate admin')
    test_index = 1
    total_tests = 4

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_admin.delay('titus.pinta@yahoo.com',
                                            'unicova')
    result = result.get()
    try:
        result = ast.literal_eval(result)
    except ValueError as e:
        raise AssertionError(e)

    assert isinstance(result, dict)
    assert 'email' in result.keys()
    assert not 'pwd' in result.keys()
    assert not 'salt' in result.keys()
    assert 'admin' in result.keys()
    assert result['admin'] == True
    assert result['email'] == 'titus.pinta@yahoo.com'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_admin.delay('titus.pinta@gmail.com',
                                            'unicova')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Email and password do not match'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_admin.delay('titu.pinta@yahoo.com',
                                            'unicova')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Email and password do not match'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.authentificate_admin.delay('titus.pinta@yahoo.com',
                                            'unicov')
    result = result.get()
    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Email and password do not match'
    test_index += 1

    print('All tests for authentificate admin have passed')


def test_get_parkings():
    print('Test for get parkings')

    test_index = 1
    total_tests = 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.get_parkings.delay()
    result = result.get()

    try:
        result = ast.literal_eval(result)
    except ValueError as e:
        raise AssertionError(e)

    assert isinstance(result, list)

    for elem in result:
        assert 'location' in elem.keys()
        assert 'num_spots' in elem.keys()
        assert 'available_spots' in elem.keys()
        assert isinstance(elem['available_spots'], int)
    print('All tests for get parkings have passed')


def test_reserve_parking(user_id, parking_id, admin_id):
    print('Tests for reserve parking')

    test_index = 1
    total_tests = 6

    print('Test {} of {}'.format(test_index, total_tests))
    parkings_initial = mongo.get_parkings.delay()

    result = mongo.reserve_parking.delay(user_id, parking_id, 'normal')
    result = result.get()

    assert isinstance(result, float)
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.get_parkings.delay()
    result = mongo.reserve_parking.delay(user_id, parking_id, 123)
    result = result.get()

    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Invalid type: 123'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.get_parkings.delay()
    result = mongo.reserve_parking.delay(admin_id, parking_id, 'normal')
    result = result.get()

    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Already reserved a parking spot'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_user.delay('titus.pinta@outlook.com', 'unicova',
                                  'Titus', 'Pinta', 'BH12TIT')
    user_id_2 = result.get()
    result = mongo.reserve_parking.delay(user_id_2, parking_id, 'normal')
    result = result.get()
    mongo.delete_user(user_id_2)

    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'No available parking spots'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.reserve_parking.delay(user_id, parking_id, 'normal')
    result = result.get()

    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Already reserved a parking spot'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))

    parkings = mongo.get_parkings.delay()
    parkings_initial = parkings_initial.get()
    parkings = parkings.get()

    parkings_initial = ast.literal_eval(parkings_initial)
    parkings = ast.literal_eval(parkings)

    for i in range(len(parkings)):
        if parkings[i]['_id'] == parking_id:
            assert parkings_initial[i]['available_spots'] -\
                parkings[i]['available_spots'] == 1


    print('All tests for reserve  parkings have passed')


def test_free_parking(user_id, parking_id, admin_id):
    print('Tests for free parking')

    test_index = 1
    total_tests = 4

    print('Test {} of {}'.format(test_index, total_tests))
    parkings_initial = mongo.get_parkings.delay()

    result = mongo.free_parking.delay(admin_id, parking_id)
    result = result.get()

    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Not a valid user'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))

    result = mongo.free_parking.delay(user_id, user_id)
    result = result.get()

    assert isinstance(result, dict)
    assert 'error' in result.keys()
    assert result['error'] == 'Not a valid user'
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))

    result = mongo.free_parking.delay(user_id, parking_id)
    result = result.get()

    assert result == True
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))

    parkings = mongo.get_parkings.delay()
    parkings_initial = parkings_initial.get()
    parkings = parkings.get()

    parkings_initial = ast.literal_eval(parkings_initial)
    parkings = ast.literal_eval(parkings)

    for i in range(len(parkings)):
        if parkings[i]['_id'] == parking_id:
            assert parkings_initial[i]['available_spots'] -\
                parkings[i]['available_spots'] == -1

    print('All tests for free parking have passed')


def test_block_spot(parking_id):
    print('Tests for block spot')

    test_index = 1
    total_tests = 2

    print('Test {} of {}'.format(test_index, total_tests))
    parkings_initial = mongo.get_parkings.delay()

    result = mongo.block_spot.delay(parking_id)
    result = result.get()

    assert result == True
    test_index += 1

    print('Test {} of {}'.format(test_index, total_tests))

    parkings = mongo.get_parkings.delay()
    parkings_initial = parkings_initial.get()
    parkings = parkings.get()

    parkings_initial = ast.literal_eval(parkings_initial)
    parkings = ast.literal_eval(parkings)

    for i in range(len(parkings)):
        if parkings[i]['_id'] == parking_id:
            assert parkings_initial[i]['available_spots'] -\
                parkings[i]['available_spots'] == 1

    print('All tests for block spot have passed')


def test_all():
    print('Running all tests')
    input('Press ENTER')
    user_id = test_add_user()
    input('Press ENTER')
    admin_id = test_add_admin()
    input('Press ENTER')
    parking_id = test_add_parking()
    input('Press ENTER')
    test_authentificate_user()
    input('Press ENTER')
    test_authentificate_admin()
    input('Press ENTER')
    test_get_parkings()
    input('Press ENTER')
    test_get_user(user_id, admin_id)
    input('Press ENTER')
    test_reserve_parking(user_id, parking_id, admin_id)
    input('Press ENTER')
    test_free_parking(user_id, parking_id, admin_id)
    input('Press ENTER')
    test_block_spot(parking_id)
    input('Press ENTER')

    test_delete_user(user_id)
    input('Press ENTER')
    test_delete_admin(admin_id)
    input('Press ENTER')
    test_delete_parking(parking_id)
    input('Press ENTER')

    print('All tests have passed')
    input('Press ENTER')
test_all()

