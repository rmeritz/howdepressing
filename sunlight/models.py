from django.db import models
import json

class SunlightDetector():
    def __init__(self, location, weather_api):
        self.location = location
        self.weather_api = weather_api

    def detect(self):
        (sunrise, sunset) = self.weather_api.sunrise_and_sunset(
            self.location)
        return DepressionIndicator(sunrise, sunset)

class DepressionIndicator():
    def __init__(self, sunrise, sunset):
        self.sunrise = sunrise
        self.sunset = sunset

    def text(self):
        if (self.sunset > 2159):
            return "Not Depressing"
        elif (self.sunset > 1659):
            return "Depressing"
        else:
            return "Very Depressing"

class WeatherApi:
    def __init__(self, urllib):
        self.urllib = urllib
        
    def sunrise_and_sunset(self, location):
        (city, country) = self.__city_and_country(location)
        weather_json = self.__weather_json(city, country)
        (sunrise, sunset) = self.__sunrise_and_sunset(weather_json)
        return (1000, 1400)

    def __city_and_country(self, location):
        json_file = self.urllib.urlopen(self.__google_url(location))
        print self.__google_url(location)
        location_info = json.load(json_file)
        address_components = location_info['results'][0]['address_components']
        city = address_components[0]['long_name']
        country = address_components[1]['long_name']
        return (city, country)

    def __google_url(self, location):
        return ("https://maps.googleapis.com/maps/api/geocode/json?"
               "address=%s&sensor=false") % location

    def __wunder_url(self):
        'http://api.wunderground.com/api/Your_Key/astronomy/q/Australia/Sydney.json'
    
