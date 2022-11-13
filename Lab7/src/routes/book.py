from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from src.utils import *
import src.models as models
import src.db as db
from src.routes.user import UserRole
from src import app
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity
)
jwt = JWTManager(app)

book_bp = Blueprint('book', __name__, url_prefix='/book')


@book_bp.route('/', methods=['POST'])
@jwt_required()
def create_book():
    class Book(Schema):
        name = fields.Str(required=True)
        author_first_name = fields.Str(required=True)
        author_last_name = fields.Str(required=True)
        pages = fields.Int(required=True)
        status = fields.Str(required=False)

    try:
        book = Book().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    user = db.session.query(models.User).filter(models.User.id == get_jwt_identity()).first()
    if user is None:
        return jsonify({'message': 'Unauthorized'}), 404
    if user.role != UserRole.Administrator:
        return jsonify({'message': 'Forbidden'}), 401
    if db.session.query(models.Book).filter(models.Book.name == book['name']).count() != 0:
        return jsonify({'message': 'Book already exists'}), 400
    new_book = models.Book(name=book['name'], author_first_name=book['author_first_name'],
                           author_last_name=book['author_last_name'], pages=book['pages'], status=book['status'])
    try:
        db.session.add(new_book)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error creating book'}), 500
    db.session.commit()
    return get_book_id(new_book.id)[0], 200


@book_bp.route('/<int:book_id>/', methods=['GET'])
def get_book_id(book_id):
    book = db.session.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    res = {'id': book.id, 'name': book.name, 'author_first_name': book.author_first_name,
           "author_last_name": book.author_last_name, "pages": book.pages, "status": book.status}
    return jsonify(res), 200


@book_bp.route('/<values>/', methods=['GET'])
def get_book_status(values):
    book = db.session.query(models.Book).filter(models.Book.status == values).all()
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    if values not in ['available', 'pending', 'sold-out']:
        return jsonify({'message': 'Wrong status'}), 404
    return jsonify([get_book_by_id(el.id) for el in book]), 200


@book_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    class Book(Schema):
        name = fields.Str(required=True)
        new_status = fields.Str(required=True)

    try:
        book = Book().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    user = db.session.query(models.User).filter(models.User.id == get_jwt_identity()).first()
    if user is None:
        return jsonify({'message': 'Unauthorized'}), 404
    if user.role != UserRole.Administrator:
        return jsonify({'message': 'Forbidden'}), 401
    book_to_update = db.session.query(models.Book).filter(models.Book.id == book_id).first()
    if book_to_update is None:
        return jsonify({'message': 'Book not found'}), 404
    if not book_to_update.name == book['name']:
        return jsonify({'message': 'Incorrect book name'}), 400
    try:
        if book.__contains__('new_status'):
            book_to_update.status = book['new_status']
    except:
        db.session.rollback()
        return jsonify({'message': 'Error updating book'}), 500
    db.session.commit()
    return get_book_id(book_id)[0], 200


@book_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = db.session.query(models.Book).filter(models.Book.id == book_id).first()
    user = db.session.query(models.User).filter(models.User.id == get_jwt_identity()).first()
    orders = db.session.query(models.Order).filter(models.Order.user_id == get_jwt_identity()).all()
    if user is None:
        return jsonify({'message': 'Unauthorized'}), 404
    if user.role != UserRole.Administrator:
        return jsonify({'message': 'Forbidden'}), 401
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    try:
        for order in orders:
            db.session.delete(order)
        db.session.delete(book)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting book'}), 500
    db.session.commit()
    return jsonify({'message': 'Book deleted'}), 200
