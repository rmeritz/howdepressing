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
    try:
        detector = SunlightDetector(location, WeatherApi(urllib))
        depression_indicator = detector.detect()
        return HttpResponse(depression_indicator.text())
    except:
        error = "We're depressed to tell you we don't know how depressing %s is at the moment." % location
        return HttpResponse(content=error, status=500)

def sunlight(request):
    return redirect('/' + request.POST['location'])
