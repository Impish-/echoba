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

        self.staff = Staff.get_user(name=self.test_user)
        if not self.staff:
            self.staff = Staff.create_user(name=self.test_user, password=self.test_password, role='adm')
        self.assertIsInstance(self.staff, Staff)

        self.http_client.fetch(self.get_url('/manage'), self.stop,
                               method="POST",
                               body=urlencode(dict(login=self.test_user, password=self.test_password,)),
                               headers={}
                               )

        response = self.wait()
        self.assertEqual(response.code, 200)

        #Staff.remove_user(name=self.test_user)
        #self.assertIsNone(Staff.get_user(name=self.test_user))

        #self.staff = Staff.create_user(name='adm', password='', role='adm')



class TestBoardModel(AsyncHTTPTestCase):
    test_user = 'test_user_lol1'
    test_password = '123123123'

    def get_app(self):
        return application

    def test_make_board(self):

        #Board.remove_board(u'Бредtest')

        b = Board.get_board(dir='test')

        if not b:
            b = Board.create(name=u'Бредtest', dir='test')

        self.staff = Staff.get_user(name=self.test_user)

        self.assertIsInstance(b, Board)
        try:
            b.add_moderator(staff_id=self.staff.id)
        except AssertionError:
            pass

        self.staff = self.staff

        self.assertIsInstance(b.staff[0], Staff)

        b.remove_moderator(staff_id=self.staff.id)
        self.assertIsInstance(b.staff[0], Staff)
        #Staff.remove_user(name=self.test_user)

        #self.assertIsNone(Staff.get_user(name=self.test_user))



