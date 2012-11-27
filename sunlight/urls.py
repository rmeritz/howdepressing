from django.conf.urls import patterns, url

from sunlight import views

urlpatterns = patterns(
    '',
    url(r'.+$', views.location, name='location'),
    url(r'', views.index, name='index')
    )
