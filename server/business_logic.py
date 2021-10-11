import os
import re
import hashlib

from db_access_layer import DB
from db_settings import DB_TABLES
from settings import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

db = DB()


# ============= Users =============


def validate_field(context, data):
    is_valid = True
    message = ''
    valid_type = context['VALID_TYPE']
    condition = context['CONDITION']
    if valid_type == 'NULL':
        is_valid = (data is None) is condition
        if not is_valid:
            is_null = 'shouldn\'t' if not condition else 'should'
            message = '\'{}\' field ' + is_null + ' be null.'
    if valid_type == 'IN_RANGE':
        is_valid = data in condition
        if not is_valid:
            message = '\'{}\' field should be one of this values: [' + ', '.join(condition) + ']'
    if valid_type == 'REGULAR':
        if re.match(condition, data) is None:
            is_valid = False
            message = 'Invalid \'{}\' field format'
    if valid_type == 'STR_LEN':
        if len(data) < condition[0] or len(data) > condition[1]:
            is_valid = False
            message = '\'{}\' field must be ' + str(condition[0]) + ' characters or longer and ' \
                      + str(condition[1]) + ' characters and less in length.'
    if valid_type == 'IS_DIGIT':
        if (re.search(r'\d+', data) is not None) != condition:
            not_str = '' if condition else 'not '
            is_valid = False
            message = '\'{}\' field must ' + not_str + 'contain numbers.'
    return is_valid, message


def validate_data(data, columns, table_name):
    is_valid = True
    errors = {}
    # Check data
    for column in columns:
        if column not in DB_TABLES[table_name]['required']:
            is_valid = False
            errors[column] = '{} has no {} field'.format(DB_TABLES[table_name]['object_name']['singular'], column)
        try:
            for context in DB_TABLES[table_name]['validation'][column]:
                is_field_valid, message = validate_field(context=context, data=data[column])
                if not is_field_valid:
                    errors[column] = message.format(column)
                    is_valid = False

        except KeyError:
            errors['fields'] = 'Not enough {} record fields'.format(DB_TABLES[table_name]['record_name']['singular'])
    return is_valid, errors


def validate_user_data(data, columns, photo_file, is_photo_required=True):
    is_valid = True
    errors = {}
    # Check if photo is valid
    if is_photo_required:
        is_valid, errors = validate_photo_file(photo_file)
    # Check user data
    for column in columns:
        if column not in DB_TABLES['users']['required']:
            is_valid = False
            errors[column] = 'User object has no {} field'.format(column)
        try:
            if column == 'name':
                if len(data['name']) <= 5 or len(data['name']) > 70:
                    is_valid = False
                    errors['name'] = 'Name must be longer than 5 characters and shorter than 70 characters in length.'
            if column == 'gender':
                if data['gender'] not in ['male', 'female']:
                    errors['gender'] = 'Gender should be "male" or "female"'
            if column == 'born_at':
                if re.match(r'\d{2}-\d{2}-\d{4}', data['born_at']) is None:
                    errors['born_at'] = 'Invalid birth date format'
        except KeyError:
            errors['fields'] = 'Not enough user record fields'
    return is_valid, errors


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_photo_file(photo_file):
    errors = {}
    is_valid = True
    # If user does not select file, browser also
    # submit an empty part without filename
    if photo_file.filename == '':
        is_valid = False
        errors['photo'] = 'You need to select a photo file'
    # Check if the file is image file
    if not photo_file or not allowed_file(photo_file.filename):
        is_valid = False
        errors['photo'] = 'Invalid photo file'
    return is_valid, errors


def generate_photo_path(data, file_type):
    hash_object = hashlib.md5(str(data).encode())
    return '{}.{}'.format(hash_object.hexdigest(), file_type)


def create_user(user_data, photo_file):
    user_data['photo_path'] = ''
    # is_valid, errors = validate_user_data(data=user_data, columns=DB_TABLES['users']['required'],
    #                                       photo_file=photo_file)
    is_valid, errors = validate_data(data=user_data, columns=DB_TABLES['users']['required'], table_name='users')
    creating_result = {}
    if not is_valid:
        creating_result['info'] = 'Invalid data'
        creating_result['errors'] = errors
    else:
        # If user data is correct
        # Insert user data to database (with empty string as photo_path)
        results = db.insert(table_name='users', column_names=user_data.keys(), values=user_data)
        # Save user photo
        user_id = results[0]['id']
        file_type = photo_file.filename.split('.')[-1]
        filename = generate_photo_path(user_id, file_type)
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        photo_file.save(photo_path)
        # Update photo_path field in user record
        db.update(table_name='users', values={'photo_path': photo_path}, id=user_id)
        # Complete db transaction
        db.complete_transaction()
        creating_result['info'] = 'Created'
    return creating_result


def update_user(user_id, user_data, photo_file=None):
    is_valid, errors = validate_user_data(data=user_data, columns=user_data.keys(),
                                          photo_file=photo_file, is_photo_required=photo_file is not None)
    updating_result = {}
    if not is_valid:
        updating_result['info'] = 'Invalid data'
        updating_result['errors'] = errors
    else:
        # If user data is correct
        # If new photo is received
        if photo_file is not None:
            # Resave photo
            file_type = photo_file.filename.split('.')[-1]
            filename = generate_photo_path(user_id, file_type)
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(photo_path)
            user_data['photo_path'] = filename
        # Update user data
        updated_ids = db.update(table_name='users', values=user_data, id=user_id)
        # Complete db transaction
        db.complete_transaction()
        if len(updated_ids) == 0:
            updating_result['info'] = 'Doesn\'t updated.  No user with such id.'
        else:
            updating_result['info'] = 'Updated'
    return updating_result


def remove_user(user_id):
    deleting_result = {}
    # Remove user with id = user_id
    result = db.delete(table_name='users', id=user_id, returning='photo_path')
    # Complete db transaction
    db.complete_transaction()
    if len(result) is not 0:
        try:
            os.remove(result[0]['photo_path'])
        except:
            pass
        deleting_result['info'] = 'Deleted'
    else:
        deleting_result['info'] = 'Doesn\'t removed.  No user with such id.'
    return deleting_result


def remove_data(id, table_name):
    deleting_result = {}
    # Remove record with id = id
    result = db.delete(table_name=table_name, id=id)
    # Complete db transaction
    db.complete_transaction()
    if len(result) is not 0:
        deleting_result['info'] = 'Deleted'
    else:
        deleting_result['info'] = 'Doesn\'t removed.  No record with such id.'
    return deleting_result


def get_data(table_name, id=None):
    condition = None if id is None else {'id': id}
    result = db.select(table_name=table_name, columns='*', condition=condition)
    db.complete_transaction()
    select_result = {}
    if id is None:
        select_result[DB_TABLES[table_name]['record_name']['plural']] = result
    else:
        select_result[DB_TABLES[table_name]['record_name']['singular']] = result
    return select_result


def update_data(id, data, table_name):
    # is_valid, errors = validate_user_data(data=user_data, columns=user_data.keys(),
    #                                       photo_file=photo_file, is_photo_required=photo_file is not None)
    is_valid = True
    errors = {}
    # todo: validate data
    updating_result = {}
    if not is_valid:
        updating_result['info'] = 'Invalid data'
        updating_result['errors'] = errors
    else:
        # If data is correct
        # Update it
        updated_ids = db.update(table_name=table_name, values=data, id=id)
        # Complete db transaction
        db.complete_transaction()
        if len(updated_ids) == 0:
            updating_result['info'] = 'Doesn\'t updated.  No record with such id.'
        else:
            updating_result['info'] = 'Updated'
    return updating_result


def create_data(data, table_name):
    # is_valid, errors = validate_data(data=data, columns=DB_TABLES[table_name]['required'])
    # todo: validation
    is_valid = True
    errors = {}
    creating_result = {}
    if not is_valid:
        creating_result['info'] = 'Invalid data'
        creating_result['errors'] = errors
    else:
        # If data is correct
        # Insert data to database
        results = db.insert(table_name=table_name, column_names=data.keys(), values=data)
        # Complete db transaction
        db.complete_transaction()
        creating_result['info'] = 'Created'
    return creating_result
