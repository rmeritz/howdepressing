import StringIO

class FakeWeatherApi:
    def __init__(self, sunrise, sunset):
        self.sunrise = sunrise
        self.sunset = sunset

    def sunrise_and_sunset(self, city, country):
        return (self.sunrise, self.sunset)

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
        if city == 'Boston':
            return open('./sunlight/fixtures/google_boston.json').read()
        else:
            location_data = {'city': city, 'country':country}
            json = open('./sunlight/fixtures/google.json').read()
            return json % location_data

class FakeGeoApi:
    def __init__(self, locations):
        self.locations = locations

    def city_and_country(self, location):
        return self.locations[location]
