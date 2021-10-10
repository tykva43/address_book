DEBUG = True
PORT = 8000
HOST = '0.0.0.0'
UPLOAD_FOLDER = './users/photos/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DB_TABLES = {
    'users': {
        'primary': 'id',
        'fields': ['id', 'name', 'photo_path', 'gender', 'born_at', 'address'],
        'required': ['name', 'photo_path', 'gender', 'born_at', 'address']
    },
    'phones': {
        'primary': 'id',
        'fields': ['id', 'user_id', 'type', 'number'],
        'required': ['user_id', 'type', 'number']
    },
    'emails': {
        'primary': 'id',
        'fields': ['id', 'user_id', 'type', 'email'],
        'required': ['user_id', 'type', 'email']
    }
}
