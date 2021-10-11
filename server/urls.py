from flask import Blueprint, request

import business_logic as bl

urls_blueprint = Blueprint('urls', __name__,)


# ============= Users endpoints =============
@urls_blueprint.route('/users/<int:user_id>/', methods=['DELETE'])
def remove_user(user_id):
    return bl.remove_user(user_id=user_id)


@urls_blueprint.route('/users/<int:user_id>/', methods=['POST'])
def get_user(user_id):
    return bl.get_data(id=user_id, table_name='users')


@urls_blueprint.route('/users/', methods=['POST'])
def get_users_list():
    return bl.get_data(table_name='users')


@urls_blueprint.route('/users/', methods=['PUT'])
def create_user():
    # Check if the request has the file part
    if 'photo' not in request.files:
        return {'errors': 'Photo is required'}
    photo_file = request.files['photo']
    result = bl.create_user(user_data=request.form.to_dict(), photo_file=photo_file)
    return result


@urls_blueprint.route('/users/<int:user_id>/', methods=['PATCH'])
def update_user(user_id):
    # Check if the request has the file part
    photo_file = None
    if 'photo' in request.files:
        photo_file = request.files['photo']
    result = bl.update_user(user_id=user_id, user_data=request.form.to_dict(), photo_file=photo_file)
    return result


# ============= Emails endpoints =============

@urls_blueprint.route('/emails/<int:email_id>/', methods=['DELETE'])
def remove_email(email_id):
    return bl.remove_data(id=email_id, table_name='emails')


@urls_blueprint.route('/emails/<int:email_id>/', methods=['POST'])
def get_email(email_id):
    return bl.get_data(id=email_id, table_name='emails')


@urls_blueprint.route('/emails/', methods=['POST'])
def get_emails_list():
    return bl.get_data(table_name='emails')


@urls_blueprint.route('/emails/', methods=['PUT'])
def create_email():
    return bl.create_data(data=request.form.to_dict(), table_name='emails')


@urls_blueprint.route('/emails/<int:email_id>/', methods=['PATCH'])
def update_email(email_id):
    return bl.update_data(id=email_id, data=request.form.to_dict(), table_name='emails')


# ============= Phones endpoints =============

@urls_blueprint.route('/phones/<int:phone_id>/', methods=['DELETE'])
def remove_phone(phone_id):
    return bl.remove_data(id=phone_id, table_name='phones')


@urls_blueprint.route('/phones/<int:phone_id>/', methods=['POST'])
def get_phone(phone_id):
    return bl.get_data(id=phone_id, table_name='phones')


@urls_blueprint.route('/phones/', methods=['POST'])
def get_phones_list():
    return bl.get_data(table_name='phones')


@urls_blueprint.route('/phones/', methods=['PUT'])
def create_phone():
    return bl.create_data(data=request.form.to_dict(), table_name='phones')


@urls_blueprint.route('/phones/<int:phone_id>/', methods=['PATCH'])
def update_phone(phone_id):
    return bl.update_data(id=phone_id, data=request.form.to_dict(), table_name='phones')
