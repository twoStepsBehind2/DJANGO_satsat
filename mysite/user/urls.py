from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('userlist/', views.userlist, name='userlist'),
    path('edit/<int:user_id>/', views.edit_user, name='edit_user'),       # ✅ Edit route
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'), 
]
