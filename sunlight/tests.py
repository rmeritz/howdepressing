from django.utils import unittest
from django_webtest import WebTest

class AcceptanceTestCase(WebTest):
    def setUp(self):
        pass

    def testUserCanSeeDepression(self):
        index = self.app.get("/")
        assert 200 == index.status_code
        
        form = index.form
        form['location'] = 'Stockholm'
        location = form.submit().follow()
        assert location.request.path_info == '/stockholm'
        assert 200 == location.status_code
        assert "Very Depressing" == location.content
