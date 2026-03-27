from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success_view, name='success'), 
    path('product/<int:product_id>/', views.product_about, name='product_about'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
]