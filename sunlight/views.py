from django.template import loader, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf

def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('index.html', c)

def location(request):
    return HttpResponse("Very Depressing")

def sunlight(request):
    return redirect('/' + request.POST['location'])
