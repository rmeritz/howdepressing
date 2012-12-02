from django.template import loader, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
import urllib

from sunlight.models import SunlightDetector, WeatherApi, GeoApi

def index(request):
    context = RequestContext(request)
    context.update(csrf(request))
    return render_to_response('index.html', context)

def location(request):
    location = request.path.strip('/')
    try:
        detector = SunlightDetector(location, GeoApi(urllib), WeatherApi(urllib))
        (city, country, sunrise, sunset) = detector.detect()
        sunrise_readable = "%s:%s" % (sunrise / 100, sunrise % 100)
        sunset_readable = "%s:%s" % (sunset / 100, sunrise % 100)
        daylight_readable = str(int(round((sunset - sunrise) / 2400.0 * 100)))
        context = {
            'city': city,
            'country': country,
            'sunrise': sunrise,
            'sunset': sunset,
            'sunrise_readable': sunrise_readable,
            'daylight_readable': daylight_readable,
            'sunset_readable': sunset_readable
         }
        return render_to_response('location.html', context)
    except:
        context = RequestContext(request)
        context.update({'location': location})
        return render_to_response('detector_error.html', context) 

def sunlight(request):
    return redirect('/' + request.POST['location'])

def darkness(request):
    sunset =  int(request.GET['sunset'])
    sunrise =  int(request.GET['sunrise'])
    morning_darkness = sunrise/24
    evening_darkness = (2400 -sunset)/24
    daylight = 100 - morning_darkness - evening_darkness
    context = {'morning_darkness': morning_darkness,
               'evening_darkness': evening_darkness,
               'daylight': daylight}
    return render_to_response('darkness.css', context)               
