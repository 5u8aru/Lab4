from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from src.utils import *
import src.models as models
import src.db as db

order_bp = Blueprint('order', __name__, url_prefix='/order')


@order_bp.route('/store/inventory', methods=['GET'])
def get_books():
    books = db.session.query(models.Book).all()
    return jsonify([get_book_by_id(book.id) for book in books]), 200


@order_bp.route('/store/make_order', methods=['POST'])
def create_order():
    class Order(Schema):
        ship_date = fields.Date(required=True)
        complete = fields.Bool(required=True)
        address = fields.Str(required=True)
        user_id = fields.Int(required=True)
        book_id = fields.Int(required=True)

    try:
        order = Order().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    new_order = models.Order(ship_date=order['ship_date'], complete=order['complete'],
                             address=order['address'], user_id=order['user_id'], book_id=order['book_id'])
    try:
        db.session.add(new_order)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error creating book'}), 500
    db.session.commit()
    return get_order_id(new_order.id)[0], 200


@order_bp.route('/store/<int:order_id>/', methods=['GET'])
def get_order_id(order_id):
    order = db.session.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        return jsonify({'message': 'Order not found'}), 404
    res = {'ship_date': order.ship_date, 'complete': order.complete, 'address': order.address,
           "user_id": order.user_id, "book_id": order.book_id}
    return jsonify(res), 200


@order_bp.route('/store/<int:order_id>/', methods=['PUT'])
def update_order(order_id):
    class Order(Schema):
        new_ship_date = fields.Date(required=False)
        new_complete = fields.Bool(required=False)
        new_address = fields.Str(required=False)
        new_user_id = fields.Int(required=False)
        new_book_id = fields.Int(required=False)

    try:
        order = Order().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    order_to_update = db.session.query(models.Order).filter(models.Order.id == order_id).first()
    if order_to_update is None:
        return jsonify({'message': 'Book not found'}), 404
    try:
        if order.__contains__('new_ship_date'):
            order_to_update.ship_date = order['new_ship_date']
        if order.__contains__('new_complete'):
            order_to_update.complete = order['new_complete']
        if order.__contains__('new_address'):
            order_to_update.address = order['new_address']
        if order.__contains__('new_user_id'):
            order_to_update.user_id = order['new_user_id']
        if order.__contains__('new_book_id'):
            order_to_update.book_id = order['new_book_id']
    except:
        db.session.rollback()
        return jsonify({'message': 'Error updating book'}), 500
    db.session.commit()
    return get_order_id(order_id)[0], 200


@order_bp.route('/store/<int:order_id>/', methods=['DELETE'])
def delete_order(order_id):
    order = db.session.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        return jsonify({'message': 'Order not found'}), 404
    try:
        db.session.delete(order)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting order'}), 500
    db.session.commit()
    return jsonify({'message': 'Order deleted'}), 200
