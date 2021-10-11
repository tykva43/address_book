DB_TABLES = {
    'users': {
        'primary': 'id',
        'fields': ['id', 'name', 'photo_path', 'gender', 'born_at', 'address'],
        'required': ['name', 'photo_path', 'gender', 'born_at', 'address'],
        'object_name': {
            'singular': 'User',
            'plural': 'Users'
        },
        'record_name': {
            'singular': 'user',
            'plural': 'users'
        },
        'validation': {
            'name': [
                {
                    'VALID_TYPE': 'STR_LEN',
                    'CONDITION': (5, 70)
                },
                {
                    'VALID_TYPE': 'IS_DIGIT',
                    'CONDITION': False
                },
            ],

            'photo_path': [{
                'VALID_TYPE': 'STR_LEN',
                'CONDITION': (0, 250)
            }],

            'gender': [{
                'VALID_TYPE': 'IN_RANGE',
                'CONDITION': ['male', 'female']
            }],

            'born_at': [{
                'VALID_TYPE': 'REGULAR',
                'CONDITION': r'(?<!\d)(?:19[0-9][0-9]|20[01][0-9])-(?:0?[1-9]|1[0-2])-(?:0?[1-9]|[12][0-9]|3[01])(?!\d)'
            }],

            'address': [{
                    'VALID_TYPE': 'STR_LEN',
                    'CONDITION': (10, 150)
                }],
        }
    },
    'phones': {
        'primary': 'id',
        'fields': ['id', 'user_id', 'type', 'number'],
        'required': ['user_id', 'type', 'number'],
        'object_name': {
            'singular': 'Phone',
            'plural': 'Phones'
        },
        'record_name': {
            'singular': 'phone',
            'plural': 'phones'
        },
        'validation': {
            'user_id': [{
                'VALID_TYPE': 'NULL',
                'CONDITION': False
            }],
            'type': [{
                'VALID_TYPE': 'IN_RANGE',
                'CONDITION': ['mobile', 'city']
            }],

            'number': [{
                'VALID_TYPE': 'REGULAR',
                'CONDITION': r'^(\+)?((\d{2,3}) ?\d|\d)(([ -]?\d)|( ?(\d{2,3}) ?)){5,12}\d$'
            }]
        }
    },
    'emails': {
        'primary': 'id',
        'fields': ['id', 'user_id', 'type', 'email'],
        'required': ['user_id', 'type', 'email'],
        'object_name': {
            'singular': 'Email',
            'plural': 'Emails'
        },
        'record_name': {
            'singular': 'email',
            'plural': 'emails'
        },
        'validation': {
            'user_id': [{
                'VALID_TYPE': 'NULL',
                'CONDITION': False
            }],
            'type': [{
                'VALID_TYPE': 'IN_RANGE',
                'CONDITION': ['personal', 'work']
            }],

            'email': [{
                'VALID_TYPE': 'REGULAR',
                'CONDITION': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            }]
        }
    }
}
