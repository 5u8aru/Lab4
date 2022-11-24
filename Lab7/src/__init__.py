import configparser
import config
import pathlib
from flask import Flask

file_config = pathlib.Path(__file__).parent.parent.joinpath('config.ini')
config_db = configparser.ConfigParser()
config_db.read(file_config)

username = config_db.get('DB', 'user')
password = config_db.get('DB', 'password')
db_name = config_db.get('DB', 'db_name')
domain = config_db.get('DB', 'domain')

url = f'postgresql://{username}:{password}@{domain}:5432/{db_name}'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'

app.config["SQLALCHEMY_DATABASE_STR"] = url
if config.is_testing:
    app.config["SQLALCHEMY_DATABASE_STR"] = 'sqlite:///test.db'

from src.routes import user, book, orders

app.register_blueprint(user.user_bp)
app.register_blueprint(book.book_bp)
app.register_blueprint(orders.order_bp)
