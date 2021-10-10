import os
import re
import hashlib

from db_access_layer import DB
from settings import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

db = DB()


def validate_user_data(data, photo_file):
    # Check if photo is valid
    is_valid, errors = validate_photo_file(photo_file)
    # Check user data
    try:
        if len(data['name']) <= 5 or len(data['name']) > 70:
            is_valid = False
            errors['name'] = 'Name must be longer than 5 characters and shorter than 70 characters in length.'
        if data['gender'] not in ['male', 'female']:
            errors['gender'] = 'Gender should be "male" or "female"'
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
    is_valid, errors = validate_user_data(user_data, photo_file)

    if not is_valid:
        return {'info': 'Invalid data', 'errors': errors}
    else:
        # If user data is correct
        user_data['photo_path'] = ''
        # Insert user data to database (with empty string as photo_path)
        results = db.insert('users', user_data.keys(), user_data)
        # Save user photo
        user_id = results[0][0]
        file_type = photo_file.filename.split('.')[-1]
        filename = generate_photo_path(user_id, file_type)
        photo_file.save(os.path.join(UPLOAD_FOLDER, filename))
        # Update photo_path field
        ...
        # Complete db transaction
        db.complete_transaction()
        return {'info': 'ok'}
