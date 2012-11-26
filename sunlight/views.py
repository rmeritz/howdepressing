from django.http import HttpResponse

def index(request):
    return HttpResponse("Location: ")

def location(request):
    return HttpResponse("Very Depressing")
