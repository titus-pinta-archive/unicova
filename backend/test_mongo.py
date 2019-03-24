import mongo
import re


def test_add_user():
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
    assert result
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
    id_re = re.compile('^[a-zA-Z0-9]*$')

    #Tests for user regitration
    test_index = 1
    total_tests = 4


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_admin.delay('titus.pinta@gmail.com', 'unicova',
                                  'Titus', 'Pinta')
    result = result.get()
    assert bool(id_re.match(result))
    user_id = result
    test_index += 1


    print('Test {} of {}'.format(test_index, total_tests))
    result = mongo.add_admin.delay('titus.pinta@gmail.com', 'unicova',
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
    #Tests for user delete
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
    assert result
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

user_id = test_add_user()
test_delete_user(user_id)
admin_id = test_add_admin()
test_delete_admin(admin_id)
#TODO finish tests
