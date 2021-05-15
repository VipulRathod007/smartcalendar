from django.contrib import admin
from django.urls import path
from .views import *
import json


with open('config.json', 'r') as file:
    jsonFile = json.load(file)
    context = jsonFile['content']


urlpatterns = [
    path(context['redirectUrls']['home'], home, name=context['urls']['home']),
    path(context['mappingUrls']['authenticate'], authenticate, name=context['urls']['authenticate']),
    path(context['mappingUrls']['logout'], logout, name=context['urls']['logout']),
]
