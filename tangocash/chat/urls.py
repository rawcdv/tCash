# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.room, name='chat'),
    # path('newChat', views.newMessage, name='newChat'),
]
