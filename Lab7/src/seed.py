import random
from faker import Faker
from src.db import session
from src.models import User, Book, Order

fake = Faker()


def create_user():
    for _ in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.ascii_free_email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
        )
        session.add(user)
    session.commit()


def create_book():
    a = ["available", "pending", "soldout"]
    for _ in range(15):
        book = Book(
            name=fake.sentence(nb_words=random.randint(1, 4)),
            author_first_name=fake.first_name(),
            author_last_name=fake.last_name(),
            pages=random.randint(50, 400),
            status=random.choice(a),
        )
        session.add(book)
    session.commit()


def create_orders():
    users = session.query(User).all()
    books = session.query(Book).all()

    for user in users:
        book = random.choice(books)
        rel = Order(user_id=user.id,
                    book_id=book.id,
                    quantity=1,
                    ship_date=fake.date_between(start_date='-10y'),
                    complete=random.choice([True, False]),
                    address=fake.address()
                    )
        session.add(rel)
    session.commit()


if __name__ == '__main__':
    create_user()
    create_book()
    create_orders()
