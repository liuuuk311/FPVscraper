import unittest
from selenium import webdriver


class FunctionalTestCase(unittest.TestCase):
    """ FunctionalTest represent a base class for a functional test (UI) """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
