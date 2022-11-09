import src.models as models
import src.db as db


def get_book_by_id(book_id: int) -> dict:
    book = db.session.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        return {}
    res = {'id': book.id, 'name': book.name, 'author_first_name': book.author_first_name,
           "author_last_name": book.author_last_name, "pages": book.pages, "status": book.status}
    return res
