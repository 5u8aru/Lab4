import datetime
from abc import ABC

from src import app
import src.db as db
from unittest.mock import ANY
import src.models as models
from flask_testing import TestCase
import copy

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()

        models.Base.metadata.drop_all(db.engine)
        models.Base.metadata.create_all(db.engine)

        self.user_1_data = {
            "username": "unittestuser1",
            "password": "unittestuserpassword1",
            "email": "unittestusermail1@mail.com"
        }

        self.user_1_data_hashed = {
            "username": self.user_1_data["username"],
            "password": bcrypt.generate_password_hash(self.user_1_data["password"]).decode('utf-8'),
            "email": self.user_1_data["email"]
        }

        self.user_2_data = {
            "username": "unittestuser2",
            "password": "unittestuserpassword2",
            "email": "unittestusermail2@mail.com"
        }

        self.user_2_data_hashed = {
            "username": self.user_2_data["username"],
            "password": bcrypt.generate_password_hash(self.user_2_data["password"]).decode('utf-8'),
            "email": self.user_2_data["email"]
        }

        user1 = models.User(username=self.user_1_data_hashed['username'], password=self.user_1_data_hashed['password'],
                            email=self.user_1_data_hashed['email'])
        user2 = models.User(username=self.user_2_data_hashed['username'], password=self.user_2_data_hashed['password'],
                            email=self.user_2_data_hashed['email'])
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.user2_id = user2.id

        self.book_1 = {
            "name": "bookname1",
            "author_first_name": "authorfn1",
            "author_last_name": "authorln1",
            "pages": 250
        }

        self.book_2 = {
            "name": "bookname2",
            "author_first_name": "authorfn2",
            "author_last_name": "authorln2",
            "pages": 300
        }

        book1 = models.Book(name=self.book_1['name'],
                            author_first_name=self.book_1['author_first_name'],
                            author_last_name=self.book_1['author_last_name'],
                            pages=self.book_1["pages"])
        book2 = models.Book(name=self.book_2['name'],
                            author_first_name=self.book_2['author_first_name'],
                            author_last_name=self.book_2['author_last_name'],
                            pages=self.book_2["pages"])
        db.session.add(book1)
        db.session.add(book2)
        db.session.commit()

        self.book1_id = book1.id
        self.book2_id = book1.id

        self.order_1 = {
            "ship_date": "2022-09-10",
            "complete": False,
            "address": "Bandera`s street, city Lviv",
            "user_id": user2.id,
            "book_id": book1.id,
        }

        order1 = models.Order(ship_date=self.order_1["ship_date"], complete=self.order_1["complete"],
                              address=self.order_1["address"], user_id=self.order_1["user_id"],
                              book_id=self.order_1["book_id"])

        db.session.add(order1)
        db.session.commit()

        self.order1_id = order1.id

    def tearDown(self):
        db.session.rollback()

    def create_app(self):
        return app

    def get_auth_header(self, credentials):
        resp = self.client.post('user/login', json=credentials)
        access_token = resp.json['token']
        return {"Authorization": f'Bearer {access_token}'}


# User test


class TestLogin(BaseTestCase):
    def test_user_login(self):
        resp = self.client.post('user/login', json=self.user_1_data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'token': ANY})

        resp = self.client.post('user/login', json={"wrong": "wrong"})

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_1_data)
        test_user["username"] = "notexistingunittestusername"
        resp = self.client.post('user/login', json=test_user)

        self.assertEqual(resp.status_code, 404)

        test_user = copy.deepcopy(self.user_1_data)
        test_user["password"] = "notexistingunittestpassword"
        resp = self.client.post('user/login', json=test_user)

        self.assertEqual(resp.status_code, 400)


class TestGetUser(BaseTestCase):
    def test_get_user(self):
        resp = self.client.get('user/', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'user/{999999}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)


class TestDeleteUser(BaseTestCase):
    def test_delete_user(self):
        test_token = self.get_auth_header(self.user_1_data)
        resp = self.client.delete('user/', headers=self.get_auth_header(self.user_1_data))

        self.assertEqual(resp.status_code, 200)

        resp = self.client.delete('user/', headers=test_token)

        self.assertEqual(resp.status_code, 404)


class TestLogoutUser(BaseTestCase):
    def test_logout_user(self):
        resp = self.client.post('user/logout', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


class TestPostUser(BaseTestCase):
    def test_post_user(self):
        resp = self.client.post('user/', json={"wrong": "wrong"})

        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('user/', json=self.user_1_data)

        self.assertEqual(resp.status_code, 400)

        testuser = self.user_1_data
        testuser["username"] = "unittestuser3"
        resp = self.client.post('user/', json=testuser)

        self.assertEqual(resp.status_code, 200)


class TestPutUser(BaseTestCase):
    def test_put_user(self):
        test_token = self.get_auth_header(self.user_2_data)

        resp = self.client.put('user/', json={"wrong": "wrong"}, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_2_data)
        test_user["password"] = "wrong password"
        resp = self.client.put('user/', json=test_user, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_2_data)
        test_user["username"] = self.user_1_data["username"]
        resp = self.client.put('user/', json=test_user, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_2_data)
        test_user["new_password"] = "new_password"
        resp = self.client.put('user/', json=test_user, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)

        self.client.delete('user/', headers=test_token)
        resp = self.client.put('user/', json=self.user_2_data, headers=test_token)

        self.assertEqual(resp.status_code, 404)


# Book test


class TestPostBook(BaseTestCase):
    def test_post_book(self):
        test_token = self.get_auth_header(self.user_2_data)

        resp = self.client.post('book/', json={"wrong": "wrong"}, headers=self.get_auth_header(self.user_1_data))

        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('book/', json=self.book_1, headers=self.get_auth_header(self.user_1_data))

        self.assertEqual(resp.status_code, 400)

        self.client.delete('user/', headers=test_token)
        resp = self.client.post('book/', json=self.book_1, headers=test_token)

        self.assertEqual(resp.status_code, 403)

        testbook = self.book_1
        testbook["name"] = "testbook3"
        resp = self.client.post('book/', json=testbook, headers=self.get_auth_header(self.user_1_data))

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.status_code, 200)


class TestGetBook(BaseTestCase):
    def test_get_book(self):
        resp = self.client.get(f'book/{self.book1_id}/')

        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'book/{999999}/')

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(f'book/wrong_status/')

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(f'book/pending/')

        self.assertEqual(resp.status_code, 200)


class TestPutBook(BaseTestCase):
    def test_put_book(self):
        test_token = self.get_auth_header(self.user_1_data)

        resp = self.client.put(f'book/{self.book1_id}', json={"wrong": "wrong"}, headers=test_token)

        self.assertEqual(resp.status_code, 400)

        self.client.delete('user/', headers=test_token)
        resp = self.client.put(f'book/{self.book1_id}', json={"name": "new_name_test"}, headers=test_token)

        self.assertEqual(resp.status_code, 403)

        resp = self.client.put(f'book/{99999}', json={"name": "new_name_test"},
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)

        resp = self.client.put(f'book/{self.book1_id}', json={"name": "new_name_test"},
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


class TestDeleteBook(BaseTestCase):
    def test_delete_book(self):
        test_token = self.get_auth_header(self.user_1_data)

        self.client.delete('user/', headers=test_token)
        resp = self.client.delete(f'book/{self.book1_id}', headers=test_token)

        self.assertEqual(resp.status_code, 403)

        resp = self.client.delete(f'book/{99999}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)

        resp = self.client.delete(f'book/{self.book1_id}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


# Order test


class TestPostOrder(BaseTestCase):
    def test_post_order(self):
        test_token = self.get_auth_header(self.user_1_data)
        resp = self.client.post('/order/store/make_order', json={"wrong": "wrong"},
                                headers=test_token)

        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('/order/store/make_order', json={"ship_date": "2022-09-10",
                                                                 "complete": False,
                                                                 "address": "Bandera`s street, city Lviv",
                                                                 "user_id": self.user2_id,
                                                                 "book_id": self.book1_id},
                                headers=test_token)

        self.assertEqual(resp.status_code, 404)

        resp = self.client.post('/order/store/make_order', json={"ship_date": "2022-09-10",
                                                                 "complete": False,
                                                                 "address": "Bandera`s street, city Lviv",
                                                                 "user_id": self.user2_id,
                                                                 "book_id": 9999},
                                headers=test_token)

        self.assertEqual(resp.status_code, 404)

        self.client.delete('user/', headers=test_token)
        resp = self.client.post('/order/store/make_order', json={"ship_date": "2022-09-10",
                                                                 "complete": False,
                                                                 "address": "Bandera`s street, city Lviv",
                                                                 "user_id": self.user2_id,
                                                                 "book_id": self.book1_id},
                                headers=test_token)

        self.assertEqual(resp.status_code, 403)

        resp = self.client.post('/order/store/make_order', json={"ship_date": "2022-09-10",
                                                                 "complete": False,
                                                                 "address": "Bandera`s street, city Lviv",
                                                                 "user_id": self.user2_id,
                                                                 "book_id": self.book1_id},
                                headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


class TestGetInventory(BaseTestCase):
    def test_get_inventory(self):
        resp = self.client.get('/order/store/inventory')

        self.assertEqual(resp.status_code, 200)


class TestGetOrder(BaseTestCase):
    def test_get_order(self):
        resp = self.client.get(f'/order/store/{self.order1_id}/')

        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/order/store/{8435798}/')

        self.assertEqual(resp.status_code, 404)


class TestPutOrder(BaseTestCase):
    def test_put_order(self):
        test_token = self.get_auth_header(self.user_1_data)
        resp = self.client.put(f'/order/store/{self.order1_id}/', json={"wrong": "wrong"},
                               headers=test_token)

        self.assertEqual(resp.status_code, 400)

        resp = self.client.put(f'/order/store/{4389509348}/',
                               json={"new_ship_date": "2021-09-10", "new_complete": True,
                                     "new_address": "Bandera`s street, city Khm"},
                               headers=test_token)

        self.assertEqual(resp.status_code, 404)

        self.client.delete('user/', headers=test_token)
        resp = self.client.put(f'/order/store/{self.order1_id}/',
                               json={"new_ship_date": "2021-09-10", "new_complete": True,
                                     "new_address": "Bandera`s street, city Khm"},
                               headers=test_token)

        self.assertEqual(resp.status_code, 403)

        resp = self.client.put(f'/order/store/{self.order1_id}/',
                               json={"new_ship_date": "2021-09-10", "new_complete": True,
                                     "new_address": "Bandera`s street, city Khm"},
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


class TestDeleteOrder(BaseTestCase):
    def test_delete_order(self):
        test_token = self.get_auth_header(self.user_1_data)

        resp = self.client.delete(f'/order/store/{4389509348}/', headers=test_token)

        self.assertEqual(resp.status_code, 404)

        self.client.delete('user/', headers=test_token)
        resp = self.client.delete(f'/order/store/{self.order1_id}/', headers=test_token)

        self.assertEqual(resp.status_code, 403)

        resp = self.client.delete(f'/order/store/{self.order1_id}/', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)

