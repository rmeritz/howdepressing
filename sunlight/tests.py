from django.test import LiveServerTestCase
from django.utils import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import StringIO

from sunlight.models import SunlightDetector, DepressionIndicator
from sunlight.models import WeatherApi

class AcceptanceTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def testUserCanSeeDepression(self):
        self.lookup_location('Stockholm')
        depression_text = self.browser.find_element_by_id('depression-text')
        self.assertEqual(
            depression_text.get_attribute("innerHTML"),
            "Very Depressing")

    def testUserCanSeeError(self):
        erroring_place = 'NonexistantPlace'
        self.lookup_location(erroring_place)
        body = self.browser.find_element_by_tag_name('body')
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

    def sunrise_and_sunset(self, location):
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

class DepressionIndicatorTest(unittest.TestCase):
    def testTextMatchDepressionLevel(self):
        self.assertDepressionLevel(sunrise = 759, sunset = 2201,
                                   level = "Not Depressing")
        self.assertDepressionLevel(sunrise = 800, sunset = 2200,
                                   level = "Not Depressing")
        self.assertDepressionLevel(sunrise = 801, sunset = 2159,
                                   level = "Depressing")
        self.assertDepressionLevel(sunrise = 900, sunset = 1700,
                                   level = "Depressing")
        self.assertDepressionLevel(sunrise = 901, sunset = 1659,
                                   level = "Very Depressing")

    def testGetters(self):
        indicator = DepressionIndicator(800,1900)
        self.assertEqual(indicator.sunrise, 800)
        self.assertEqual(indicator.sunset, 1900)

    def assertDepressionLevel(self, sunrise, sunset, level):

        self.assertEqual(DepressionIndicator(sunrise, sunset).text(),
                         level)

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
        json = """
{
  "response": {
  "version": "0.1",
  "termsofService": "http://www.wunderground.com/weather/api/d/terms.html",
  "features": {
  "astronomy": 1
  }
  },
  "moon_phase": {
  "percentIlluminated": "81",
  "ageOfMoon": "10",
  "current_time": {
  "hour": "9",
  "minute": "56"
  },
  "sunrise": {
  "hour": "%(sunrise_hour)s",
  "minute": "%(sunrise_minute)s"
  },
  "sunset": {
  "hour": "%(sunset_hour)s",
  "minute": "%(sunset_minute)s"
  }
  }
}"""
        return json % sunlight_strings

    def __google_json(self, city, country):
        location_data = {'city': city, 'country':country}
        json = """{
   "results" : [
         {
         "address_components" : [
            {
               "long_name" : "%(city)s",
               "short_name" : "Barcelona",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Barcelona",
               "short_name" : "B",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "Catalua",
               "short_name" : "CT",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "%(country)s",
               "short_name" : "ES",
               "types" : [ "country", "political" ]
            }
         ],
      
         "formatted_address" : "Stockholm, Sweden",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 59.42784089999999,
                  "lng" : 18.1982290
               },
               "southwest" : {
                  "lat" : 59.2244430,
                  "lng" : 17.77686210
               }
            },
            "location" : {
               "lat" : 59.32893000000001,
               "lng" : 18.064910
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 59.42784089999999,
                  "lng" : 18.1982290
               },
               "southwest" : {
                  "lat" : 59.2244430,
                  "lng" : 17.77686210
               }
            }
         },
         "types" : [ "locality", "political" ]
      }
   ],
   "status" : "OK"
}"""
        return json % location_data

class WeatherApiTest(unittest.TestCase):
    def testFindsSunriseAndSunset(self):
        fake_stockholm_urllib = FakeDepressingUrllib('Stockholm', 'Sweden', 1000, 1400)
        self.assertEqual(WeatherApi(fake_stockholm_urllib).sunrise_and_sunset('Stockholm'),
                         (1000, 1400))
        fake_barcelona_urllib = FakeDepressingUrllib('Barcelona', 'Spain', 559, 2201)
        self.assertEqual(WeatherApi(fake_barcelona_urllib).sunrise_and_sunset('Barcelona'),
                         (559, 2201))
