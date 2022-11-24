from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src import app
import config


#  f'postgresql://username:password@domain_name:port/database_name'


Base = declarative_base()
engine = create_engine(app.config['SQLALCHEMY_DATABASE_STR'], echo=True)
metadata = Base.metadata

DBSession = sessionmaker(bind=engine)
session = DBSession()

if config.is_testing:
    metadata.drop_all(engine)
    metadata.create_all(engine)