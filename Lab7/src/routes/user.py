from marshmallow import Schema, fields, ValidationError
from marshmallow_enum import EnumField
from enum import Enum, IntEnum
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from src.utils import *
import src.models as models
import src.db as db
from src import app
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

jwt = JWTManager(app)

user_bp = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()


class UserRole(IntEnum):
    User = 1
    Administrator = 2


@user_bp.route('/', methods=['POST'])
def create_user():
    class User(Schema):
        username = fields.Str(required=True)
        email = fields.Str(required=True)
        password = fields.Str(required=True)
        role = EnumField(UserRole, by_value=False, required=True)
        first_name = fields.Str(required=False)
        last_name = fields.Str(required=False)
        phone = fields.Str(required=False)

    try:
        user = User().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    if db.session.query(models.User).filter(models.User.username == user['username']).count() != 0:
        return jsonify({'message': 'User already exists'}), 400

    new_user = models.User(username=user['username'], email=user['email'],
                           password=bcrypt.generate_password_hash(user['password']).decode('utf-8'), role=user['role'])
    if user.__contains__('first_name'):
        new_user.first_name = user['first_name']
    if user.__contains__('last_name'):
        new_user.last_name = user['last_name']
    if user.__contains__('phone'):
        new_user.phone = user['phone']
    try:
        db.session.add(new_user)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error creating user'}), 500
    db.session.commit()
    return get_user(new_user.id)[0], 200


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_me():
    return get_user(get_jwt_identity())


@user_bp.route('/login', methods=['POST'])
def login():
    class UserToLogin(Schema):
        username = fields.Str(required=True)
        password = fields.Str(required=True)

    try:
        user = UserToLogin().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    db_user = db.session.query(models.User).filter(models.User.username == user['username']).first()
    if db_user is None:
        return jsonify({'message': 'User not found'}), 404
    if not bcrypt.check_password_hash(db_user.password, user['password']):
        return jsonify({'message': 'Incorrect password'}), 400
    access_token = create_access_token(identity=db_user.id)
    return jsonify({'token': access_token}), 200


@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out'}), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_user(user_id):
    user = db.session.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    res = {'id': user.id, 'username': user.username, 'orders': []}
    if get_jwt_identity() == user_id:
        orders = db.session.query(models.Order).filter(models.Order.user_id == user_id).all()
        for _ in orders:
            res['orders'].append(get_orders_of_user(user_id))
    else:
        res = {'id': user.id, 'username': user.username}
    return jsonify(res), 200


@user_bp.route('/', methods=['DELETE'])
@jwt_required()
def delete_user():
    user = db.session.query(models.User).filter(models.User.id == get_jwt_identity()).first()
    orders = db.session.query(models.Order).filter(models.Order.user_id == get_jwt_identity()).all()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    try:
        for order in orders:
            db.session.delete(order)
        db.session.delete(user)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting user'}), 500
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200


@user_bp.route('/', methods=['PUT'])
@jwt_required()
def update_user():
    class UserToUpdate(Schema):
        username = fields.Str()
        password = fields.Str(required=True)
        new_password = fields.Str()

    try:
        user = UserToUpdate().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    user_id = get_jwt_identity()
    user_to_update = db.session.query(models.User).filter(models.User.id == user_id).first()
    if user_to_update is None:
        return jsonify({'message': 'User not found'}), 404
    if not bcrypt.check_password_hash(user_to_update.password, user['password']):
        return jsonify({'message': 'Incorrect password'}), 400

    if user.__contains__('username'):
        if db.session.query(models.User).filter(models.User.username == user['username']).count() != 0 and \
                user['username'] != user_to_update.username:
            return jsonify({'message': 'User already exists'}), 400
        user_to_update.username = user['username']
    if user.__contains__('new_password'):
        user_to_update.password = bcrypt.generate_password_hash(user['new_password']).decode('utf-8')

    db.session.commit()
    return get_user(user_id)

# @user_bp.route('/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     class User(Schema):
#         username = fields.Str(required=True)
#         password = fields.Str(required=True)
#         new_username = fields.Str(required=False)
#         new_password = fields.Str(required=False)
#         new_email = fields.Str(required=False)
#         new_first_name = fields.Str(required=False)
#         new_last_name = fields.Str(required=False)
#         new_phone = fields.Str(required=False)
#
#     try:
#         user = User().load(request.json)
#     except ValidationError as error:
#         return jsonify(error.messages), 400
#     user_to_update = db.session.query(models.User).filter(models.User.id == user_id).first()
#     if user_to_update is None:
#         return jsonify({'message': 'User not found'}), 404
#     if not bcrypt.check_password_hash(user_to_update.password, user['password']):
#         return jsonify({'message': 'Incorrect password'}), 400
#     if not user_to_update.username == user['username']:
#         return jsonify({'message': 'Incorrect username'}), 400
#     try:
#         if user.__contains__('new_username'):
#             if db.session.query(models.User).filter(models.User.username == user['new_username']).count() != 0:
#                 return jsonify({'message': 'User already exists'}), 400
#             user_to_update.username = user['new_username']
#         if user.__contains__('new_email'):
#             user_to_update.email = user['new_email']
#         if user.__contains__('new_first_name'):
#             user_to_update.first_name = user['new_first_name']
#         if user.__contains__('new_last_name'):
#             user_to_update.last_name = user['new_last_name']
#         if user.__contains__('new_phone'):
#             user_to_update.phone = user['new_phone']
#         if user.__contains__('new_password'):
#             user_to_update.password = bcrypt.generate_password_hash(user['new_password']).decode('utf-8')
#     except:
#         db.session.rollback()
#         return jsonify({'message': 'Error updating user'}), 500
#     db.session.commit()
#     return get_user(user_id)[0], 200

# @user_bp.route('/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     user = db.session.query(models.User).filter(models.User.id == user_id).first()
#     if user is None:
#         return jsonify({'message': 'User not found'}), 404
#     res = {'id': user.id, 'username': user.username, 'email': user.email, "first_name": user.first_name,
#            "last_name": user.last_name, "phone": user.phone}
#     return jsonify(res), 200

# @user_bp.route('/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = db.session.query(models.User).filter(models.User.id == user_id).first()
#     if user is None:
#         return jsonify({'message': 'User not found'}), 404
#     try:
#         db.session.delete(user)
#     except:
#         db.session.rollback()
#         return jsonify({'message': 'Error deleting user'}), 500
#     db.session.commit()
#     return jsonify({'message': 'User deleted'}), 200
