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
        index = self.browser.get(self.live_server_url)
        location_field = self.browser.find_element_by_name('location')
        location_field.send_keys('Stockholm')
        location_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        assert "Very Depressing" == body.get_attribute("innerHTML")

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

    def assertDepressionLevel(self, sunrise, sunset, level):
        self.assertEqual(DepressionIndicator(sunrise, sunset).text(),
                         level)

class FakeDepressingUrllib:
    def __init__(self, location_to_sunlights):
        self.location_to_sunlights = location_to_sunlights

    def urlopen(self, url):
        for location, sunlights in self.location_to_sunlights.items():
            print location
            print sunlights
            if (location in url):
                if ('google' in url):
                    return self.__string_io_google(location)
                else:
                    return self.__string_io_wunderground(sunlights)
        return self.__empty_string_io()

    def __string_io_wunderground(self, sunlights):
        s = StringIO.StringIO()
        s.write(self.__wunderground_json(sunlights))
        return s

    def __string_io_google(self, location):
        print "In google fake"
        s = StringIO.StringIO()
        s.write(self.__google_json(location))
        s.seek(0)
        return s

    def __empty_string_io(self):
        print "Well we are clearly here"
        s = StringIO.StringIO()
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
  "hour": "%(sunrise_hour),
  "minute": "%(sunrise_minute)"
  },
  "sunset": {
  "hour": "%(sunset_hour)",
  "minute": "%(sunset_minute)"
  }
  }
}"""
        return json % sunlight_strings

    def __google_json(self, location):
        json = """{
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "%s",
               "short_name" : "Stockholm",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Sweden",
               "short_name" : "SE",
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
        return json % location

class WeatherApiTest(unittest.TestCase):
    def testFindsSunriseAndSunset(self):
        fake_http = FakeDepressingUrllib({
                'Stockholm': (1000, 1400),
                'Barcelona': (559, 2201)
                })
        weather_api = WeatherApi(fake_http)
        self.assertEqual(weather_api.sunrise_and_sunset('Stockholm'),
                         (1000, 1400))
        self.assertEqual(weather_api.sunrise_and_sunset('Barcelona'),
                         (559, 2201))
