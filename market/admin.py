from django.contrib import admin
from unfold.admin import ModelAdmin  
from .models import Product, Category,Order
from django.contrib.auth.models import User
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["user", "full_name", "phone", "address", "total_amount", "created_at"]
    list_filter = ["user", "created_at"]
    search_fields = ["user__username", "full_name", "phone", "address"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["name", "price", "category"] 
    pass