from django.utils import unittest
from django.test.client import Client
#from lxml import html

class AcceptanceTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testUserCanSeeDepression(self):
        c = Client()
        response = c.get("/")
        assert 200 == response.status_code

        response = c.get("/stockholm")
        assert 200 == response.status_code
        assert "Very Depressing" == response.content
