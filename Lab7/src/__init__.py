from flask import Flask
from src.routes import user
from src.routes import book
from src.routes import orders

app = Flask(__name__)

app.register_blueprint(user.user_bp)
app.register_blueprint(book.book_bp)
app.register_blueprint(orders.order_bp)
