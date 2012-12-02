from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from sunlight import views

urlpatterns = patterns(
    '',
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': 'favicon.ico'}),
    url(r'location.css', views.darkness, name='darkness'),
    url(r'sunlight', views.sunlight, name='sunlight'),
    url(r'.+$', views.location, name='location'),
    url(r'', views.index, name='index')
    ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
