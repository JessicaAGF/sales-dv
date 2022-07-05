from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dv-index'),
    path('home', views.home, name='dv-home')
]
