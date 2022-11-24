from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
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


@user_bp.route('/', methods=['POST'])
def create_user():
    class User(Schema):
        username = fields.Str(required=True)
        password = fields.Str(required=True)
        email = fields.Str(required=True)
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
                           password=bcrypt.generate_password_hash(user['password']).decode('utf-8'))
    if user.__contains__('first_name'):
        new_user.first_name = user['first_name']
    if user.__contains__('last_name'):
        new_user.last_name = user['last_name']
    if user.__contains__('phone'):
        new_user.phone = user['phone']
    db.session.add(new_user)
    db.session.commit()
    return "Success", 200


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_me():
    return get_user(get_jwt_identity())


@user_bp.route('/login', methods=['POST'])
def login():
    try:
        class User(Schema):
            username = fields.Str(required=True)
            password = fields.Str(required=True)
            email = fields.Str(required=False)

        user = User().load(request.json)
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
def get_user(user_id):
    user = db.session.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    res = {'id': user.id, 'username': user.username, 'email': user.email, "first_name": user.first_name,
           "last_name": user.last_name, "phone": user.phone}
    return jsonify(res), 200


@user_bp.route('/', methods=['DELETE'])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = db.session.query(models.User).filter(models.User.id == user_id).first()
    orders = db.session.query(models.Order).filter(models.Order.user_id == get_jwt_identity()).all()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    if orders is not None:
        for order in orders:
            db.session.delete(order)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200


@user_bp.route('/', methods=['PUT'])
@jwt_required()
def update_user():
    try:
        class User(Schema):
            username = fields.Str()
            password = fields.Str(required=True)
            email = fields.Str(required=False)
            new_password = fields.Str()

        user = User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_id = get_jwt_identity()
    user_up = db.session.query(models.User).filter(models.User.id == user_id).first()

    if user_up is None:
        return jsonify({'error': 'User not found'}), 404

    if not bcrypt.check_password_hash(user_up.password, user['password']):
        return jsonify({'message': 'Incorrect password'}), 400

    if user.__contains__('username'):
        if db.session.query(models.User).filter(models.User.username == user['username']).count() != 0 and \
                user['username'] != user_up.username:
            return jsonify({'message': 'User already exists'}), 400
        user_up.username = user['username']
    if user.__contains__('new_password'):
        user_up.password = bcrypt.generate_password_hash(user['new_password']).decode('utf-8')

    db.session.commit()
    return "", 200
