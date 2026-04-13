from django.contrib import admin
from .models import Category, Product, Cart, Order, OrderItem

# Buyurtma ichidagi mahsulotlarni Order sahifasining o'zida ko'rsatish uchun
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Bo'sh qatorlar ko'rinmasligi uchun
    readonly_fields = ['product', 'price', 'quantity'] # O'zgartirib bo'lmasligi uchun (ixtiyoriy)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'total_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['full_name', 'phone']
    inlines = [OrderItemInline] # Mana shu narsa buyurtma ichida mahsulotlarni ko'rsatadi

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
