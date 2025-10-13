from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('userlist/', views.userlist, name='userlist'),
    path('signup/', views.signup, name='signup'),
    path('edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('logout/', views.logout_user, name='logout'),

    # ✅ Product List Page
    path('products/', views.products, name='products'),
]
