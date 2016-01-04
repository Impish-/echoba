import unittest

import re
from selenium import webdriver
from tornado.testing import AsyncHTTPTestCase

from ech import application
from manage.models import Staff, Board


class TestTornado(AsyncHTTPTestCase):
    def get_app(self):
        return application

    def test_homepage(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

    def test_login(self):
        from urllib import urlencode
        self.http_client.fetch(self.get_url('/manage'), self.stop,
                               method="POST",
                               body=urlencode(dict(login='admin', password='123',)),
                               headers={}
                               )

        response = self.wait()
        print response.__dict__
        self.assertEqual(response.code, 200)


class TestBoardModel(unittest.TestCase):
    def test_make_board(self):
        b = Board()


class TestStaffModel(unittest.TestCase):
    def test_make_user(self):
        staff = Staff.create_or_update_user(name='admin', password='123', role='adm')
        self.assertIsInstance(staff, Staff)

    def test_get_auth(self):
        auth = Staff.get_auth('admin', password='123')
        self.assertTrue(auth, True)


