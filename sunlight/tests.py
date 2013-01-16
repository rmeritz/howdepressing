from django.test import LiveServerTestCase
from django.utils import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import StringIO

from sunlight.models import SunlightDetector
from sunlight.models import WeatherApi, GeoApi

class AcceptanceTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def testUserCanSeeDepression(self):
        self.lookup_location('Stockholm')
        full_location = self.browser.find_element_by_id('full-location')
        self.assertEqual(
            full_location.get_attribute("innerHTML"),
            "Stockholm, Sweden")

    def testUserCanSeeError(self):
        erroring_place = 'NonexistantPlace'
        self.lookup_location(erroring_place)
        body = self.browser.find_element_by_tag_name('p')
        self.assertEqual(
            body.get_attribute("innerHTML"),
            "We're depressed to tell you we don't know how depressing %s is at the moment." % erroring_place)

    def lookup_location(self, location_name):
        index = self.browser.get(self.live_server_url)
        location_field = self.browser.find_element_by_name('location')
        location_field.send_keys(location_name)
        location_field.send_keys(Keys.RETURN)

class FakeWeatherApi:
    def __init__(self, sunrise, sunset):
        self.sunrise = sunrise
        self.sunset = sunset

    def sunrise_and_sunset(self, city, country):
        return (self.sunrise, self.sunset)

class SunlightDetectorTest(unittest.TestCase):
    def testTextForAVeryDepressingPlace(self):
        fake_weather_api = FakeWeatherApi(sunrise = 1000, sunset = 1400)
        detector = SunlightDetector('stockholm', fake_weather_api)
        depression_indicator = detector.detect()
        assert "Very Depressing" == depression_indicator.text()

    def testTextForANotDepressingPlace(self):
        fake_weather_api = FakeWeatherApi(sunrise = 759, sunset = 2201)
        detector = SunlightDetector('barcelona', fake_weather_api)
        depression_indicator = detector.detect()
        assert "Not Depressing" == depression_indicator.text()

class FakeDepressingUrllib:
    def __init__(self, city, country, sunrise, sunset):
        self.city = city
        self.country = country
        self.sunrise = sunrise
        self.sunset = sunset

    def urlopen(self, url):
          if ('google' in url):
              return self.__string_io_google(self.city, self.country)
          elif (self.city in url and self.country in url):
              return self.__string_io_wunderground((self.sunrise, self.sunset))
          else:
              print 'Bad URL'

    def __string_io_wunderground(self, sunlights):
        s = StringIO.StringIO()
        s.write(self.__wunderground_json(sunlights))
        s.seek(0)
        return s

    def __string_io_google(self, city, country):
        s = StringIO.StringIO()
        s.write(self.__google_json(city, country))
        s.seek(0)
        return s

    def __wunderground_json(self, sunlights):
        (sunrise, sunset) = sunlights
        sunlight_strings = {
            'sunrise_hour': "%02d" % (sunrise/100),
            'sunrise_minute': "%02d" % (sunrise % 100),
            'sunset_hour': "%02d" % (sunset/100),
            'sunset_minute': "%02d" % (sunset % 100)
            }
        json = open('./sunlight/fixtures/wunderground.json').read()
        return json % sunlight_strings

    def __google_json(self, city, country):
        location_data = {'city': city, 'country':country}
        json = open('./sunlight/fixtures/google.json').read()
        return json % location_data

class FakeGeoApi(unittest.TestCase):
    def __init__(self, locations):
        self.locations = locations

    def city_and_country(self, location):
        return self.locations[location]

class WeatherApiTest(unittest.TestCase):
    def testFindsSunriseAndSunset(self):
        fake_stockholm_urllib = FakeDepressingUrllib('Stockholm', 'Sweden', 1000, 1400)
        self.assertEqual(WeatherApi(fake_stockholm_urllib).sunrise_and_sunset('Stockholm', 'Sweden'),
                         (1000, 1400))
        fake_barcelona_urllib = FakeDepressingUrllib('Barcelona', 'Spain', 559, 2201)
        self.assertEqual(WeatherApi(fake_barcelona_urllib).sunrise_and_sunset('Barcelona', 'Spain'),
                         (559, 2201))

class GeoApiTest(unittest.TestCase):
    def testFindsCityAndCountry(self):
        fake_stockholm_urllib = FakeDepressingUrllib('Stockholm', 'Sweden', 1000, 1400)
        self.assertEqual(GeoApi(fake_stockholm_urllib).city_and_country('Stockholm'),
                         ('Stockholm', 'Sweden'))

class SunlightDetectorTest(unittest.TestCase):
    def testDetect(self):
        fake_geo_api = FakeGeoApi({'Stockholm': ('Stockholm', 'Sweden')})
        fake_weather_api = FakeWeatherApi(1000, 1400)
        detector = SunlightDetector('Stockholm', fake_geo_api, fake_weather_api)
        self.assertEqual(detector.detect(), ('Stockholm', 'Sweden', 1000, 1400))
