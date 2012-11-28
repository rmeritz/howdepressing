from django.test import LiveServerTestCase
from django.utils import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sunlight.models import SunlightDetector

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

class FakeLocation:
    def city(self):
        return 'Boston'
    def state(self):
        return 'Georgia'
    def country(self):
        return 'USA'

class FakeAstronomy:
    def __init__(self, sunrise, sunset):
        self.sunrise = sunrise
        self.sunset = sunset

    def sunset(self):
        return self.sunset
    def sunrise(self):
        return self.sunrise

class FakeWeatherApi:
    def __init__(self, sunrise = 800, sunset = 1900, full_location = FakeLocation()):
        self.sunrise = sunrise
        self.sunset = sunset
        self.full_location = full_location

    def full_location(self, input_string):
        return self.full_location

    def astronomy(self):
        return FakeAstronomy(sunrise = self.sunrise, sunset = self.sunset)

class SunlightDetectorTest(unittest.TestCase):
    def testTextForAVeryDepressingPlace(self):
        fake_weather_api = FakeWeatherApi(sunrise = 1000, sunset = 1400)
        detector = SunlightDetector('stockholm', fake_weather_api)
        depression_indicator = detector.detect()
        assert "Very Depressing" == depression_indicator.text()
