# -*- coding: utf-8 -*-
import unittest

import re
from selenium import webdriver
from tornado.testing import AsyncHTTPTestCase

from ech import application
from manage.models import Staff, Board


class TestStaff(AsyncHTTPTestCase):
    test_user = 'test_user_lol1'
    test_password = '123123123'

    def get_app(self):
        return application

    def test_homepage(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

    def test_set_up(self):
        self.staff = Staff.create_user(name=self.test_user, password=self.test_password, role='adm')
        self.assertIsInstance(self.staff, Staff)

    def test_login(self):
        from urllib import urlencode
        self.http_client.fetch(self.get_url('/manage'), self.stop,
                               method="POST",
                               body=urlencode(dict(login=self.test_user, password=self.test_password,)),
                               headers={}
                               )

        response = self.wait()
        self.assertEqual(response.code, 200)

    def test_remove(self):
        removed = Staff.remove_user(name=self.test_user)
        self.assertIsNone(removed)


class TestBoardModel(unittest.TestCase):
    def test_make_board(self):
        b = Board(name=u'Бред', dir='b')


