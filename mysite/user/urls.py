from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------
    # User Management
    # -------------------------------
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

    # -------------------------------
    # Cashier System
    # -------------------------------
    path('cashier/', views.cashier, name='cashier'),
    path('cashier/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cashier/add_by_code/', views.add_by_code, name='add_by_code'),
    path('cashier/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cashier/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cashier/clear/', views.clear_cart, name='clear_cart'),
    path('cashier/checkout/', views.checkout, name='checkout'),
    path('cashier/receipt/<int:sale_id>/', views.sale_receipt, name='sale_receipt'),
]
