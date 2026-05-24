from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('product/<int:product_id>/', views.product_about, name='product_about'),
    
    # Savatcha tizimi
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/', views.update_cart_view, name='update_cart'),
    
    # Buyurtma
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success_view, name='order-success'), 
    
    # Sotuvchi paneli
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    # urls.py ichiga qo'shing:
    path('live-search/', views.live_search, name='live_search'),
    path('auto-fill-images/', views.auto_fill_empty_images, name='auto_fill_images'),
    path('dashboard/product/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
path('dashboard/product/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),
path('dashboard/product/create/', views.create_product_view, name='create_product'),
]