from flask import Blueprint, request

urls_blueprint = Blueprint('urls', __name__,)


# Users endpoints
@urls_blueprint.route('/users/<int:user_id>/', methods=['DELETE'])
def remove_user(user_id):
    return 'Remove user with id={}'.format(user_id)


@urls_blueprint.route('/users/<int:user_id>/', methods=['POST'])
def get_user(user_id):
    return 'Get one user with id={}'.format(user_id)


@urls_blueprint.route('/users/', methods=['POST'])
def get_users_list():
    return 'Get all users'


@urls_blueprint.route('/users/', methods=['PUT'])
def create_user():
    user_data = request.form.to_dict()

    return 'Create user {}'.format(user_data)


@urls_blueprint.route('/users/<int:user_id>/', methods=['PATCH'])
def update_user(user_id):
    return 'Update user {}'.format(user_id)
