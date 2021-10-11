import json
import os
import re
import hashlib

from db_access_layer import DB
from db_settings import DB_TABLES
from settings import UPLOAD_FOLDER

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
            is_valid = False
            errors['fields'] = 'Not enough {} record fields'.format(DB_TABLES[table_name]['record_name']['singular'])
    return is_valid, errors


def generate_photo_path(data, file_type):
    hash_object = hashlib.md5(str(data).encode())
    return '{}.{}'.format(hash_object.hexdigest(), file_type)


def pop_key(dictionary, key):
    key_data = '[]'
    if key in dictionary.keys():
        key_data = dictionary[key]
        del dictionary[key]
    return key_data


def check_user_additional_data(emails, phones):
    is_valid = True
    errors = {}
    # Temporary set user_id as 1 for validating another fields
    for i, email in enumerate(emails):
        email['user_id'] = 1
        is_emails_valid, errors['emails[{i}]'] = validate_data(data=email, columns=DB_TABLES['emails']['required'],
                                                               table_name='emails')
        if not is_emails_valid:
            is_valid = False

    for i, phone in enumerate(phones):
        phone['user_id'] = 1
        is_phones_valid, errors['phones[{i}]'] = validate_data(data=phone, columns=DB_TABLES['phones']['required'],
                                                               table_name='phones')
        if not is_phones_valid:
            is_valid = False
    return is_valid, errors


def set_user_id_to_list(data, user_id):   # Set user_id to additional user data (emails, phones)
    for elem in data:
        elem['user_id'] = user_id
    return data


def create_user(user_data, photo_file):
    user_data['photo_path'] = ''

    # Get emails and phones fields as string and parse to dict
    emails = json.loads(pop_key(user_data, 'emails'))
    phones = json.loads(pop_key(user_data, 'photos'))

    # Check if user data is valid
    is_valid, errors = validate_data(data=user_data, columns=DB_TABLES['users']['required'], table_name='users')
    is_valid, messages = check_user_additional_data(emails, phones)

    creating_result = {}
    if not is_valid:
        creating_result['info'] = 'Invalid data'
        creating_result['errors'] = errors
        creating_result['additional_fields'] = messages
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
        # Insert emails and photos if exists
        set_user_id_to_list(data=emails, user_id=user_id)
        set_user_id_to_list(data=phones, user_id=user_id)
        if len(emails) > 0:
            db.insert('emails', emails[0].keys(), emails)
        if len(phones) > 0:
            db.insert('phones', phones[0].keys(), phones)
        # Complete db transaction
        db.complete_transaction()
        creating_result['info'] = 'Created'
    return creating_result


def update_user(user_id, user_data, photo_file=None):
    is_valid, errors = validate_data(data=user_data, columns=user_data.keys(), table_name='users')
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


def get_data(table_name, id=None, sort_by=None):
    condition = None if id is None else {'id': id}
    order = tuple()
    if sort_by:
        column = sort_by[0]
        value = sort_by[1].lower()
        if column in DB_TABLES[table_name]['fields'] and value in ['asc', 'desc']:
            order = (column, value)
    result = db.select(table_name=table_name, columns='*', condition=condition, order=order)
    db.complete_transaction()
    select_result = {}

    if id is None:
        select_result[DB_TABLES[table_name]['record_name']['plural']] = result
    else:
        select_result[DB_TABLES[table_name]['record_name']['singular']] = result
    return select_result


def update_data(id, data, table_name):
    is_valid, errors = validate_data(data=data, columns=data.keys(), table_name=table_name)
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
    is_valid, errors = validate_data(data=data, columns=DB_TABLES[table_name]['required'], table_name=table_name)
    creating_result = {}
    if not is_valid:
        creating_result['info'] = 'Invalid data'
        creating_result['errors'] = errors
    else:
        # If data is correct
        # Insert data to database
        selected = db.select('users', 'id', condition={'id': data['user_id']})
        if len(selected) == 1:
            result = db.insert(table_name=table_name, column_names=data.keys(), values=data)
            if len(result) == 0:
                creating_result['info'] = 'Doesn\'t created'
            else:
                creating_result['info'] = 'Created'
        else:
            creating_result['info'] = 'Invalid user_id'
        # Complete db transaction
        db.complete_transaction()
    return creating_result
