# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 16:35:47 2021

@author: Harvey
"""

from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
        path('', views.index, name='index'),
        path('about',views.about, name = 'about')
        ]