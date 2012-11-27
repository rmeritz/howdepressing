from django.conf.urls import patterns, url

from sunlight import views

urlpatterns = patterns(
    '',
    url(r'sunlight', views.sunlight, name='sunlight'),
    url(r'.+$', views.location, name='location'),
    url(r'', views.index, name='index')
    )
