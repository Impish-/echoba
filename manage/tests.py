import unittest
from selenium import webdriver
from manage.models import Staff, Board


class TestStaffModel(unittest.TestCase):
    def test_make_user(self):
        staff = Staff.get_or_create_user(name='admin', password='123', role='adm')
        self.assertIsInstance(staff, Staff)

    def test_get_auth(self):
        auth = Staff.get_auth('admin', password='123')
        self.assertTrue(auth, True)


class TestManageWeb(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def get_login_page(self):
        self.browser.get('http://localhost:8888/login')
        self.assertTrue(1,1)


class TestBoard(unittest.TestCase):
    def test_make_board(self):
        b = Board()






