from django.contrib import admin
from django.urls import path, include

from .views import *

app_name="form"

urlpatterns = [
    path('', dynform, name='dynform'),
]
