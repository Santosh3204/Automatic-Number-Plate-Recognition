from django.urls import path

from anpr.views import *


urlpatterns = [
    path("", home_page, name="home_page"),
    path("recognize/", recognize_number, name="recognize_number"),
    
]


