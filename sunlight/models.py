from django.db import models
import json

class SunlightDetector():
    def __init__(self, location, geo_api, weather_api):
        self.location = location
        self.geo_api = geo_api
        self.weather_api = weather_api

    def detect(self):
        (city, country) = self.geo_api.city_and_country(self.location)
        (sunrise, sunset) = self.weather_api.sunrise_and_sunset(city, country)
        return (city, country, sunrise, sunset)

class GeoApi:
    def __init__(self, urllib):
        self.urllib = urllib

    def city_and_country(self, location):
        json_file = self.urllib.urlopen(self.__google_url(location))
        location_info = json.load(json_file)
        address_components = location_info['results'][0]['address_components']
        return (self.__city(address_components), self.__country(address_components))

    def __city(self, address):
        return filter(lambda x: x['types'] == [u'locality', u'political'], address)[0]['long_name']

    def __country(self, address):
        country = filter(lambda x: x['types'] == [u'country', u'political'], address)[0]['long_name']
        if country == 'United States':
            return filter(lambda x: x['types'] == [u'administrative_area_level_1', u'political'], address)[0]['short_name']
        else:
            return country

    def __google_url(self, location):
        return ("https://maps.googleapis.com/maps/api/geocode/json?"
               "address=%s&sensor=false") % location

class WeatherApi:
    def __init__(self, urllib):
        self.urllib = urllib

    def sunrise_and_sunset(self, city, country):
        json_file = self.urllib.urlopen(self.__wunder_url(city, country))
        weather_info = json.load(json_file)
        moon_phase = weather_info['moon_phase']
        sunrise = int(moon_phase['sunrise']['hour']) * 100 + int(moon_phase['sunrise']['minute'])
        sunset = int(moon_phase['sunset']['hour']) * 100 + int(moon_phase['sunset']['minute'])
        return (sunrise, sunset, )

    def __wunder_url(self, city, country):
        url_data = {'key': "e75509deda852c8d",'city': city, 'country': country}
        return ("http://api.wunderground.com/api/%(key)s/astronomy/"
                "q/%(country)s/%(city)s.json") % url_data
