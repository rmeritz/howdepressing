from django.template import loader, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
import urllib

from sunlight.models import SunlightDetector, WeatherApi

def index(request):
    context = RequestContext(request)
    context.update(csrf(request))
    return render_to_response('index.html', context)

def location(request):
    location = request.path.strip('/')
    try:
        detector = SunlightDetector(location, WeatherApi(urllib))
        context = {'depression_indicator': detector.detect()}
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
    print (morning_darkness, daylight, evening_darkness)
    context = {'morning_darkness': morning_darkness,
               'evening_darkness': evening_darkness,
               'daylight': daylight}
    return render_to_response('darkness.css', context)               
