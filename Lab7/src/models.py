from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

from src.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(120), nullable=False)
    email = Column('email', String(100), nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=True)
    phone = Column(String(100), nullable=True)
    orders = relationship('Order', back_populates='user')


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    author_first_name = Column(String(120), nullable=False)
    author_last_name = Column(String(120), nullable=False)
    pages = Column(Integer, nullable=False)
    status = Column(String(100), nullable=True)
    orders = relationship('Order', back_populates='book')


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    ship_date = Column(String(100), nullable=False)
    complete = Column(Boolean, nullable=False)
    address = Column(String(100), nullable=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='orders')
    book_id = Column('book_id', ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    book = relationship('Book', back_populates='orders')