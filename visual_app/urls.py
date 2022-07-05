from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dv-home'),
    path('index', views.index, name='dv-index')
]
