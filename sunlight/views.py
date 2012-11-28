from django.template import loader, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
import urllib

from sunlight.models import SunlightDetector, WeatherApi

def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('index.html', c)

def location(request):
    location = request.path.strip('/')
    detector = SunlightDetector(location, WeatherApi(urllib))
    depression_indicator = detector.detect()
    return HttpResponse(depression_indicator.text())

def sunlight(request):
    return redirect('/' + request.POST['location'])
