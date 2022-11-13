from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

from src.routes import user
from src.routes import book
from src.routes import orders

app.register_blueprint(user.user_bp)
app.register_blueprint(book.book_bp)
app.register_blueprint(orders.order_bp)
