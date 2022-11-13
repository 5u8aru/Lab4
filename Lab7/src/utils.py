import src.models as models
import src.db as db


def get_book_by_id(book_id: int) -> dict:
    book = db.session.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        return {}
    res = {'id': book.id, 'name': book.name, 'author_first_name': book.author_first_name,
           "author_last_name": book.author_last_name, "pages": book.pages, "status": book.status}
    return res


def get_orders_of_user(user_id: int) -> dict | list:
    orders = db.session.query(models.Order).filter(models.Order.user_id == user_id).all()
    if orders is None:
        return {}
    return [{"ship_date": order.ship_date, "complete": order.complete, "address": order.address,
             "user_id": order.user_id, "book_id": order.book_id} for order in orders]
