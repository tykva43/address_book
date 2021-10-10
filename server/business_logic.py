import os
import re
import hashlib

from db_access_layer import DB
from settings import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, DB_TABLES

db = DB()


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
    is_valid, errors = validate_user_data(data=user_data, columns=DB_TABLES['users']['required'],
                                          photo_file=photo_file)
    creating_result = {}
    if not is_valid:
        creating_result['info'] = 'Invalid data'
        creating_result['errors'] = errors
    else:
        # If user data is correct
        # Insert user data to database (with empty string as photo_path)
        results = db.insert(table_name='users', column_names=user_data.keys(), values=user_data)
        # Save user photo
        user_id = results[0][0]
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
            os.remove(result[0][0])
        except:
            pass
        deleting_result['info'] = 'Deleted'
    else:
        deleting_result['info'] = 'Doesn\'t removed.  No user with such id.'
    return deleting_result
