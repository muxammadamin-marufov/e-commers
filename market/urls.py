from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success_view, name='order-success'), 
    path('product/<int:product_id>/', views.product_about, name='product_about'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
path('add-product/', views.add_product, name='add_product'),
path('generate-description/', views.generate_description, name='generate_description'),
]
