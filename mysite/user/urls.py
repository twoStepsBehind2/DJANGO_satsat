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

    # -------------------------------
    # Products
    # -------------------------------
    path('products/', views.products, name='products'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),

    # -------------------------------
    # Stock Report
    # -------------------------------
    path('product_stock/', views.product_stock, name='product_stock'),
    


]
