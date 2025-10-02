from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),               # Home page
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
]
