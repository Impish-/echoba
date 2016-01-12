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

    def test_login(self):
        from urllib import urlencode
        try:
            self.staff = Staff.create_user(name=self.test_user, password=self.test_password, role='adm')
        except:
            self.staff = Staff.get_user(name=self.test_user)

        self.http_client.fetch(self.get_url('/manage'), self.stop,
                               method="POST",
                               body=urlencode(dict(login=self.test_user, password=self.test_password,)),
                               headers={}
                               )

        response = self.wait()
        self.assertEqual(response.code, 200)

        Staff.remove_user(name=self.test_user)
        self.assertIsNone(Staff.get_user(name=self.test_user))



class TestBoardModel(unittest.TestCase):
    test_user = 'test_user_lol1'
    test_password = '123123123'

    def test_make_board(self):
        try:
            self.staff = Staff.create_user(name=self.test_user, password=self.test_password, role='adm')
        except:
            self.staff = Staff.get_user(name=self.test_user)
        self.assertIsInstance(self.staff, Staff)

        Board.remove_board(u'Бредtest')

        b = Board.create(name=u'Бредtest', dir='test')

        b.add_moderator(self.staff.id)

        mods = b.staff.all()
        print mods

        b.remove_moderator(self.staff.id)

        Staff.remove_user(name=self.test_user)
        self.assertIsNone(Staff.get_user(name=self.test_user))


