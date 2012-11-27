from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class AcceptanceTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def testUserCanSeeDepression(self):
        index = self.browser.get(self.live_server_url)
        location_field = self.browser.find_element_by_name('location')
        location_field.send_keys('Stockholm')
        location_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        assert "Very Depressing" == body.get_attribute("innerHTML")
